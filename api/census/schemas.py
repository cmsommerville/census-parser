from extensions import ma
from shared import BaseSchema

from . import models as md


class SchemaCensusDetail(BaseSchema):
    class Meta:
        model = md.ModelCensusDetail
        load_instance = True
        include_relationships = True
        include_fk = True


class SchemaCensusMaster(BaseSchema):
    class Meta:
        model = md.ModelCensusMaster
        load_instance = True
        include_relationships = True
        include_fk = True

    census_details = ma.Nested(SchemaCensusDetail, many=True)


class SchemaCensusMasterDropdown(BaseSchema):
    census_master_id = ma.Integer(data_key="id")
    census_name = ma.String(data_key="name")


class SchemaCensusUpload(ma.Schema):
    tab = ma.String()
    birthdate = ma.Date()
    relationship = ma.String()
    tobacco_disposition = ma.String()
    effective_date = ma.Date()


class SchemaRateUpload(ma.Schema):
    rate_master_id = ma.Integer()
    lower_age = ma.Integer()
    upper_age = ma.Integer()
    relationship = ma.String()
    tobacco_disposition = ma.String()
    rate = ma.Float()


class SchemaRateDetail(BaseSchema):
    class Meta:
        model = md.ModelRateDetail
        load_instance = True
        include_relationships = True
        include_fk = True


class SchemaRateMaster(BaseSchema):
    class Meta:
        model = md.ModelRateMaster
        load_instance = True
        include_relationships = True
        include_fk = True

    rate_details = ma.Nested(SchemaRateDetail, many=True)


class SchemaRateMasterDropdown(BaseSchema):
    rate_master_id = ma.Integer(data_key="id")
    rate_master_name = ma.String(data_key="name")


class SchemaSaveAgeInputs(ma.Schema):
    effective_date = ma.Date(required=True)
    rate_master_id = ma.Integer(required=True)
    census_master_id = ma.Integer(required=True)


class SchemaSaveAgeOutput(ma.Schema):
    census_detail_id = ma.Integer()
    relationship = ma.String()
    tobacco_disposition = ma.String()
    issue_age = ma.Integer()
    birthdate = ma.Date("%Y-%m-%d")
    save_age_effective_date = ma.Date("%Y-%m-%d")
    new_effective_date = ma.Date("%Y-%m-%d")
    save_age_rate = ma.Float()
    new_rate = ma.Float()
    diff = ma.Float()


class SchemaCensusConfigLLM(ma.Schema):
    tab_name = ma.String()
    start_row_number = ma.Integer()
    start_column_number = ma.Integer()
    column_mapper = ma.Dict()
