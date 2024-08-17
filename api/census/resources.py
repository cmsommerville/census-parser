import os
import datetime
import pandas as pd
from extensions import db
from flask import request, current_app
from flask_restx import Resource
from sqlalchemy import and_, literal
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce
from marshmallow import ValidationError
from shared import BaseResource
from .file_handler import CensusUploadHandler

from . import models as md
from . import schemas as sch


class CensusMaster(BaseResource):
    model = md.ModelCensusMaster
    schema = sch.SchemaCensusMaster()

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


class RateMaster(BaseResource):
    model = md.ModelRateMaster
    schema = sch.SchemaRateMaster()

    @classmethod
    def unbounded_min(cls, data, umin="N", default_umin_value=-9999):
        if umin != "Y":
            return data
        data = sorted(data, key=lambda x: x["lower_age"])
        data[0]["lower_age"] = default_umin_value
        return data

    @classmethod
    def unbounded_max(cls, data, umax="N", default_umax_value=9999):
        if umax != "Y":
            return data
        data = sorted(data, key=lambda x: x["upper_age"])
        data[-1]["upper_age"] = default_umax_value
        return data

    @classmethod
    def modify_rate_details(cls, data, *args, **kwargs):
        data = cls.unbounded_min(data, kwargs.get("umin", "N"))
        data = cls.unbounded_max(data, kwargs.get("umax", "N"))
        return data

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


class SaveAgeCalc(Resource):
    @classmethod
    def calc_save_age_data(cls, validated_data):
        CENSUS = md.ModelCensusDetail
        SAVE_AGE_RATE = md.ModelRateDetail
        NEW_RATE = aliased(md.ModelRateDetail)

        new_effective_date = datetime.datetime.strptime(
            validated_data["effective_date"], "%Y-%m-%d"
        ).date()

        output = (
            db.session.query(
                CENSUS.census_detail_id,
                CENSUS.relationship,
                CENSUS.tobacco_disposition,
                CENSUS.issue_age,
                CENSUS.birthdate,
                CENSUS.effective_date.label("save_age_effective_date"),
                literal(new_effective_date).label("new_effective_date"),
                SAVE_AGE_RATE.rate.label("save_age_rate"),
                NEW_RATE.rate.label("new_rate"),
                (coalesce(NEW_RATE.rate, 0) - coalesce(SAVE_AGE_RATE.rate, 0)).label(
                    "diff"
                ),
            )
            .select_from(CENSUS)
            .join(
                SAVE_AGE_RATE,
                and_(
                    SAVE_AGE_RATE.rate_master_id == validated_data["rate_master_id"],
                    CENSUS.relationship == SAVE_AGE_RATE.relationship,
                    CENSUS.tobacco_disposition == SAVE_AGE_RATE.tobacco_disposition,
                    CENSUS.issue_age >= SAVE_AGE_RATE.lower_age,
                    CENSUS.issue_age <= SAVE_AGE_RATE.upper_age,
                ),
                isouter=True,
            )
            .join(
                NEW_RATE,
                and_(
                    NEW_RATE.rate_master_id == validated_data["rate_master_id"],
                    CENSUS.relationship == NEW_RATE.relationship,
                    CENSUS.tobacco_disposition == NEW_RATE.tobacco_disposition,
                    CENSUS.issue_age_as_of(validated_data["effective_date"])
                    >= NEW_RATE.lower_age,
                    CENSUS.issue_age_as_of(validated_data["effective_date"])
                    <= NEW_RATE.upper_age,
                ),
                isouter=True,
            )
            .filter(
                CENSUS.census_master_id == validated_data["census_master_id"],
            )
            .all()
        )
        return output

    @classmethod
    def post(cls, *args, **kwargs):
        data = request.get_json()
        try:
            sch.SchemaSaveAgeInputs().load(data)
        except ValidationError as e:
            return {"status": "error", "msg": e.messages}, 400

        result = cls.calc_save_age_data(data)
        return sch.SchemaSaveAgeOutput(many=True).dump(result), 200


class CensusUpload(Resource):
    @classmethod
    def post(cls, *args, **kwargs):
        uploaded_file = request.files["file"]
        filename = uploaded_file.filename
        if filename == "":
            return {"status": "error", "msg": "No file selected"}, 400
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config["FILE_UPLOAD_EXTENSIONS"]:
            return {"status": "error", "msg": "Invalid file format"}, 400

        file_handler = CensusUploadHandler(uploaded_file)
        census_master = file_handler.save()
        output_data = sch.SchemaCensusMaster().dump(census_master)
        return {"status": "success", "data": output_data}, 200
