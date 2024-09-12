import os
from extensions import db, limiter
from typing import List
from flask import request, current_app
from flask_restx import Resource
from sqlalchemy import not_
from marshmallow import ValidationError
from shared import BaseResource, BaseListResource
from .file_handler import CensusUploadHandler, RateUploadHandler

from . import models as md
from . import schemas as sch
from . import mixins as mix


class CRUDCensusMaster(BaseResource):
    model = md.ModelCensusMaster
    schema = sch.SchemaCensusMaster()

    RETRIEVE_EXCLUDE_FIELDS = ["census_details"]

    @classmethod
    def retrieve(cls, id, *args, **kwargs):
        obj = cls.model.get(id)
        exclude = [
            field
            for field in cls.RETRIEVE_EXCLUDE_FIELDS
            if field not in kwargs.get("field_mask", [])
        ]
        return sch.SchemaCensusMaster(exclude=exclude).dump(obj)

    @classmethod
    def update(cls, id, data, *args, **kwargs):
        try:
            census = cls.model.get(id)
            if "census_details" in data:
                for dtl in census.census_details:
                    db.session.delete(
                        dtl
                    )  # relies on the save() method below to commit or rollback

                new_census_detail_data = data.pop("census_details", [])
                new_census_detail_objs = sch.SchemaCensusDetail(many=True).load(
                    new_census_detail_data
                )
                census.census_details = new_census_detail_objs

            for key, value in data.items():
                setattr(census, key, value)

            census.save()
            return cls.schema.dump(census)
        except Exception as e:
            raise e


class CRUDCensusMasterDropdownList(BaseListResource):
    model = md.ModelCensusMaster
    schema = sch.SchemaCensusMasterDropdown(many=True)

    @classmethod
    def list(cls, name, *args, **kwargs):
        offset = kwargs.get("offset", 0)
        limit = kwargs.get("limit", 20)
        fuzzy_search = "%" + "%".join(list(name)) + "%"
        obj = (
            cls.model.query.filter(cls.model.census_name.ilike(fuzzy_search))
            .limit(limit)
            .offset(offset)
            .all()
        )
        return cls.schema.dump(obj)


class CensusStats(mix.CensusStatsMixin, Resource):
    @classmethod
    def get(cls, id, *args, **kwargs):
        stats = cls.get_stats(id)
        return stats, 200


class CRUDCensusDetailList(BaseListResource):
    model = md.ModelCensusDetail
    schema = sch.SchemaCensusDetail(many=True)

    @classmethod
    def get_filters(cls, args):
        filters = {}
        for k, v in args.items():
            if k in cls.model.__table__.columns:
                filters[k] = v
        return filters

    @classmethod
    def list(cls, id, *args, **kwargs):
        offset = kwargs.get("offset", 0)
        limit = kwargs.get("limit", 100)
        # sortby = getattr(cls.model, kwargs.get("sort", "census_detail_id"))
        obj = (
            cls.model.query.filter(cls.model.census_master_id == id)
            .filter_by(**cls.get_filters(request.args))
            # .order_by(sortby.desc() if desc == "Y" else sortby)
            .limit(limit)
            .offset(offset)
            .all()
        )
        return cls.schema.dump(obj)


class CRUDRateMaster(mix.RateDetailMixin, BaseResource):
    model = md.ModelRateMaster
    schema = sch.SchemaRateMaster()

    RETRIEVE_EXCLUDE_FIELDS = ["rate_details"]

    @classmethod
    def retrieve(cls, id, *args, **kwargs):
        obj = cls.model.get(id)
        exclude = [
            field
            for field in cls.RETRIEVE_EXCLUDE_FIELDS
            if field not in kwargs.get("field_mask", [])
        ]
        return sch.SchemaRateMaster(exclude=exclude).dump(obj)

    @classmethod
    def update(cls, id, data, *args, **kwargs):
        try:
            rate_master = cls.model.get(id)
            if "rate_details" in data:
                for dtl in rate_master.rate_details:
                    db.session.delete(
                        dtl
                    )  # relies on the save() method below to commit or rollback

                new_rate_detail_data = data.pop("rate_details", [])
                new_rate_detail_data = cls.modify_rate_details(
                    new_rate_detail_data, **kwargs
                )

                new_rate_detail_objs = sch.SchemaRateDetail(many=True).load(
                    new_rate_detail_data
                )
                rate_master.rate_details = new_rate_detail_objs

            for key, value in data.items():
                setattr(rate_master, key, value)

            rate_master.save()
            return cls.schema.dump(rate_master)
        except Exception as e:
            raise e

    @classmethod
    def patch(cls, id, *args, **kwargs):
        return super().patch(id, *args, **request.args)


class CRUDRateMasterDropdownList(BaseListResource):
    model = md.ModelRateMaster
    schema = sch.SchemaRateMasterDropdown(many=True)

    @classmethod
    def list(cls, name, *args, **kwargs):
        offset = kwargs.get("offset", 0)
        limit = kwargs.get("limit", 20)
        fuzzy_search = "%" + "%".join(list(name)) + "%"
        obj = (
            cls.model.query.filter(cls.model.rate_master_name.ilike(fuzzy_search))
            .limit(limit)
            .offset(offset)
            .all()
        )
        return cls.schema.dump(obj)


class SaveAgeCalc(mix.SaveAgeQueryMixin, Resource):
    @classmethod
    def apply_operator(cls, col, op, val):
        if op == "greaterThan":
            return col > val
        elif op == "lessThan":
            return col < val
        elif op == "equals":
            return col == val
        elif op == "notEqual":
            return col != val
        elif op == "greaterThanOrEqual":
            return col >= val
        elif op == "lessThanOrEqual":
            return col <= val
        elif op == "contains":
            return col.contains(val)
        elif op == "notContains":
            return not_(col.contains(val))
        else:
            raise ValueError("Invalid operator")

    @classmethod
    def filter_parser(cls, filter_string: str):
        """
        Parses a filter string into a list of SQLAlchemy filter objects
        Required format is `column::operator::value`
        Multiple filters can be separated by `;;`
        """
        output_filters = []
        filters = filter_string.split(";;")

        for cond in filters:
            ft = cond.split("::")
            if len(ft) != 3:
                raise ValueError("Invalid filter format")
            col = getattr(md.ModelCensusDetail, ft[0])
            if col is None:
                raise ValueError("Invalid column name")
            output_filters.append(cls.apply_operator(col, ft[1], ft[2]))
        return output_filters

    @classmethod
    def sort_parser(cls, qry_columns: List[str], sort_string: str = None):
        if not sort_string:
            return None
        sort_colnames = sort_string.split(",")
        sort_cols = []
        for col in sort_colnames:
            desc = False
            if col[0] == "-":
                desc = True
                col = col[1:]

            if col not in qry_columns:
                raise ValueError("Invalid column name")

            sort_cols.append(col + " " + ("desc" if desc else "asc"))
        return ",".join(sort_cols)

    @classmethod
    def post(cls, *args, **kwargs):
        data = request.get_json()
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 100)
        filter_string = request.args.get("filters")
        qry = cls.base_save_age_query(data, offset, limit)
        qry_columns = [col.get("name") for col in qry.column_descriptions]

        try:
            filters = cls.filter_parser(filter_string) if filter_string else []
            sort = cls.sort_parser(qry_columns, request.args.get("sort"))
        except ValueError as e:
            return {"status": "error", "msg": str(e)}, 400

        try:
            sch.SchemaSaveAgeInputs().load(data)
        except ValidationError as e:
            return {"status": "error", "msg": e.messages}, 400

        data = cls.calc_save_age_data(
            qry, filters=filters, sorts=sort, offset=offset, limit=limit
        )
        stats = cls.calc_save_age_stats(qry)
        return {
            "data": sch.SchemaSaveAgeOutput(many=True).dump(data),
            "stats": stats,
        }, 200


class CensusUpload(Resource):
    @classmethod
    def post(cls, *args, **kwargs):
        uploaded_file = request.files["file"]
        custom_filename = request.form.get("name", uploaded_file.filename)
        filename = uploaded_file.filename
        if filename == "":
            return {"status": "error", "msg": "No file selected"}, 400
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config["FILE_UPLOAD_EXTENSIONS"]:
            return {"status": "error", "msg": "Invalid file format"}, 400

        file_handler = CensusUploadHandler(uploaded_file, filename=custom_filename)
        census_master = file_handler.save()
        output_data = sch.SchemaCensusMaster(exclude=("census_details",)).dump(
            census_master
        )
        return output_data, 200


class RateUpload(Resource):
    @classmethod
    def post(cls, *args, **kwargs):
        uploaded_file = request.files["file"]
        custom_filename = request.form.get("name", uploaded_file.filename)
        filename = uploaded_file.filename
        if filename == "":
            return {"status": "error", "msg": "No file selected"}, 400
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config["FILE_UPLOAD_EXTENSIONS"]:
            return {"status": "error", "msg": "Invalid file format"}, 400

        file_handler = RateUploadHandler(uploaded_file, filename=custom_filename)
        rate_master = file_handler.save(**request.args)
        output_data = sch.SchemaRateMaster(exclude=("rate_details",)).dump(rate_master)
        return output_data, 200

        #     col_dict["birthdate"] = col
        # elif adjcol in RELATIONSHIP_LABELS:
        #     col_dict["relationship"] = col
        # elif adjcol in TOBACCO_DISPOSITION_LABELS:
        #     col_dict["tobacco_disposition"] = col
        # elif adjcol in EFFECTIVE_DATE_LABELS:
        #     col_dict["effective_date"] = col


class CensusParser(Resource):
    SYSTEM_PROMPT = """The prompt contains multiple CSV files, each as a string.
    Your job is to identify which files, if any, contain census data. 
    A census file will be tabular data with columns that include the following columns: 
    - relationship
    - tobacco_disposition
    - effective_date
    The file will also contain at least one of 
    - birthdate
    - issue_age
    The columns may be named differently. 
    There may be blank rows and columns at the top of the file.
    There may be more columns than those listed, but those are the minimum required columns.
    If a file contains census data, you should return the file name, the row number containing the column names, 
    the column number of the first column in the data, and a mapper which maps the column names in the file to the required columns. 
    Use 1-based indexing for row and column numbers.
    Return the data in the following format:
    [
        {
            "file_name": "file_name",
            "start_row_number": "1",
            "start_column_number": "1",
            "column_mapper": {
                "relationship": "relationship",
                "tobacco_disposition": "tobacco_disposition",
                "effective_date": "effective_date",
                "birthdate": "birthdate", 
                "issue_age": "issue_age"
            }
        }, 
        ...
    ]
    The keys in the column_mapper should be the current column names. 
    The values should be the required column names.
    Be concise. Do not include any extraneous information.
    """

    @limiter.limit("30/hour")
    @limiter.limit("10/minute")
    @limiter.limit("1/second")
    def post(self):
        uploaded_file = request.files["file"]
        custom_filename = request.form.get("name", uploaded_file.filename)
        filename = uploaded_file.filename
        if filename == "":
            return {"status": "error", "msg": "No file selected"}, 400
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config["FILE_UPLOAD_EXTENSIONS"]:
            return {"status": "error", "msg": "Invalid file format"}, 400

        file_handler = CensusUploadHandler(uploaded_file, filename=custom_filename)
        config = file_handler.process()
        raw_data = file_handler.raw_data()
        return {
            "status": "success",
            "msg": {
                "data": config,
                "metadata": dict(file_handler.metadata),
                "raw_data": raw_data,
            },
        }, 200
