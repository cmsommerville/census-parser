import os
import re
import pandas as pd
from io import BytesIO
from extensions import db
from . import models as md
from . import schemas as sch
from . import mixins as mix


class BaseFileHandler:
    def __init__(self, file, *args, **kwargs):
        self.file = BytesIO(file.read())
        self.filename = kwargs.get("filename", file.filename)
        self.filepath = file.filename
        self.file_extension = os.path.splitext(file.filename)[1]

    def save(self):
        self.file.save(self.file.filename)
        return self.file.filename

    def read(self):
        if self.file_extension in [".xlsx", ".xls", ".xlsm"]:
            return self._read_excel(self.file)
        elif self.file_extension == ".csv":
            return pd.read_csv(self.file)
        else:
            raise ValueError("Invalid file format")

    @classmethod
    def _read_excel(cls, file):
        return pd.read_excel(file)


class CensusUploadHandler(BaseFileHandler):
    @staticmethod
    def get_column_mapper(df: pd.DataFrame):
        col_dict = {
            "birthdate": None,
            "relationship": None,
            "tobacco_disposition": None,
            "effective_date": None,
        }
        BIRTHDATE_LABELS = ["birthdate", "dob", "dateofbirth", "birthday"]
        RELATIONSHIP_LABELS = ["relationship", "rel", "relation"]
        TOBACCO_DISPOSITION_LABELS = [
            "tobacco",
            "tobaccodisposition",
            "tobaccostatus",
            "smoker",
            "smokerstatus",
            "smokerdisposition",
        ]
        EFFECTIVE_DATE_LABELS = [
            "effective",
            "effectivedate",
            "eff",
            "ced",
            "coverageeffective",
            "coverageeffectivedate",
            "dateofissue",
            "issuedate",
        ]

        for col in df.columns:
            adjcol = re.sub(r"[^A-Za-z0-9]", "", col).lower()
            if adjcol in BIRTHDATE_LABELS:
                col_dict["birthdate"] = col
            elif adjcol in RELATIONSHIP_LABELS:
                col_dict["relationship"] = col
            elif adjcol in TOBACCO_DISPOSITION_LABELS:
                col_dict["tobacco_disposition"] = col
            elif adjcol in EFFECTIVE_DATE_LABELS:
                col_dict["effective_date"] = col

        if None in col_dict.values():
            raise ValueError("Invalid column names")

        col_mapper = {v: k for k, v in col_dict.items()}
        return col_mapper

    @classmethod
    def _read_excel(cls, file):
        df = pd.read_excel(file)
        col_mapper = cls.get_column_mapper(df)
        return df.rename(columns=col_mapper)

    def save(self):
        # create the census master record w/o details
        census_master = {
            "census_name": self.filename,
            "census_path": self.filepath,
        }
        census_master = sch.SchemaCensusMaster().load(census_master)
        db.session.add(census_master)
        # flush to get the master id
        db.session.flush()

        # create the census details
        df_detail = self.read()
        df_detail["census_master_id"] = census_master.census_master_id
        census_detail_dict = sch.SchemaCensusUpload(many=True).dump(
            df_detail.to_dict(orient="records")
        )
        census_details = sch.SchemaCensusDetail(many=True).load(census_detail_dict)
        db.session.add_all(census_details)
        census_master.census_details = census_details
        db.session.commit()

        return census_master


class RateUploadHandler(mix.RateDetailMixin, BaseFileHandler):
    @staticmethod
    def get_column_mapper(df: pd.DataFrame):
        age_band_col_dict = {
            "age_band": None,
            "lower_age": None,
            "upper_age": None,
        }
        col_dict = {
            "relationship": None,
            "tobacco_disposition": None,
            "rate": None,
        }
        AGE_BAND_LABELS = ["ageband", "age", "agegroup", "agebandgroup"]
        LOWER_AGE_LABELS = ["lowerage", "lower"]
        UPPER_AGE_LABELS = ["upperage", "upper"]
        RELATIONSHIP_LABELS = ["relationship", "rel", "relation"]
        TOBACCO_DISPOSITION_LABELS = [
            "tobacco",
            "tobaccodisposition",
            "tobaccostatus",
            "smoker",
            "smokerstatus",
            "smokerdisposition",
        ]
        RATE_LABELS = [
            "rate",
            "modal",
            "modalrate",
            "modalpremium",
            "prem",
            "premium",
        ]

        for col in df.columns:
            adjcol = re.sub(r"[^A-Za-z0-9]", "", col).lower()
            if adjcol in AGE_BAND_LABELS:
                age_band_col_dict["age_band"] = col
            elif adjcol in LOWER_AGE_LABELS:
                age_band_col_dict["lower_age"] = col
            elif adjcol in UPPER_AGE_LABELS:
                age_band_col_dict["upper_age"] = col

            elif adjcol in RELATIONSHIP_LABELS:
                col_dict["relationship"] = col
            elif adjcol in TOBACCO_DISPOSITION_LABELS:
                col_dict["tobacco_disposition"] = col
            elif adjcol in RATE_LABELS:
                col_dict["rate"] = col

        if None in col_dict.values():
            raise ValueError("Invalid column names")
        if age_band_col_dict["age_band"] is not None:
            _ = age_band_col_dict.pop("lower_age")
            _ = age_band_col_dict.pop("upper_age")
        elif (
            age_band_col_dict["lower_age"] is not None
            and age_band_col_dict["upper_age"] is not None
        ):
            _ = age_band_col_dict.pop("age_band")
        else:
            raise ValueError("Invalid column names")

        col_mapper = {
            **{v: k for k, v in col_dict.items()},
            **{v: k for k, v in age_band_col_dict.items()},
        }
        return col_mapper

    @classmethod
    def _read_excel(cls, file):
        df = pd.read_excel(file)
        col_mapper = cls.get_column_mapper(df)
        return df.rename(columns=col_mapper)

    @staticmethod
    def split_age_band(age_band):
        if "-" in age_band:
            return [val.strip() for val in age_band.split("-")]
        if "to" in age_band:
            return [val.strip() for val in age_band.split("to")]
        if age_band.endswith("+"):
            return [age_band[:-1].strip(), "999"]
        raise ValueError("Invalid age band format")

    @classmethod
    def handle_age_band(cls, df: pd.DataFrame, col_mapper):
        if "age_band" not in col_mapper:
            return df
        df["lower_age"] = df["age_band"].apply(lambda x: int(cls.split_age_band(x)[0]))
        df["upper_age"] = df["age_band"].apply(lambda x: int(cls.split_age_band(x)[1]))
        return df.drop(columns=["age_band"])

    def save(self, **kwargs):
        # create the census master record w/o details
        rate_master = {
            "rate_master_name": self.filename,
        }
        rate_master = sch.SchemaRateMaster().load(rate_master)
        db.session.add(rate_master)
        # flush to get the master id
        db.session.flush()

        # create the census details
        df_detail = self.read()
        df_detail["rate_master_id"] = rate_master.rate_master_id
        df_detail = self.handle_age_band(df_detail, self.get_column_mapper(df_detail))
        dict_detail = self.modify_rate_details(
            df_detail.to_dict(orient="records"), **kwargs
        )

        rate_detail_dict = sch.SchemaRateUpload(many=True).dump(dict_detail)
        rate_details = sch.SchemaRateDetail(many=True).load(rate_detail_dict)
        db.session.add_all(rate_details)
        rate_master.census_details = rate_details
        db.session.commit()

        return rate_master
