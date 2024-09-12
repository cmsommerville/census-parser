import os
import re
import pandas as pd
from io import BytesIO
from extensions import db
from typing import Dict
from collections import defaultdict
from . import models as md
from . import schemas as sch
from . import mixins as mix


class BaseFileHandler:
    def __init__(self, file, *args, **kwargs):
        self.file = BytesIO(file.read())
        self.filename = kwargs.get("filename", file.filename)
        self.filepath = file.filename
        self.file_extension = os.path.splitext(file.filename)[1]

        self.dfs = {}
        self.metadata = defaultdict(dict)

    @property
    def multiple_tabs(self):
        return len(self.dfs.keys()) != 1

    def identify_header_row(self, df: pd.DataFrame, nrows=20, threshold=0.5):
        """
        Helper function to identify which row contains the header
        """
        for i, row in df.iloc[:nrows].iterrows():
            if row.isnull().sum() / len(row) < threshold:
                return i
        return None

    def identify_first_column(self, df: pd.DataFrame, nrows=20, threshold=0.1):
        """
        Helper function to identify which column contains the first data
        """
        for i, col in df.iloc[:nrows].items():
            if col.isnull().sum() / len(col) < threshold:
                return i
        return None

    def save(self):
        self.file.save(self.file.filename)
        return self.file.filename

    def read(self):
        if self.file_extension in [".xlsx", ".xls", ".xlsm"]:
            self.dfs = self._read_excel(self.file)
            return self.dfs
        elif self.file_extension == ".csv":
            self.dfs = {"default": pd.read_csv(self.file)}
        else:
            raise ValueError("Invalid file format")

    @classmethod
    def _read_excel(cls, file):
        return pd.read_excel(file, header=None, sheet_name=None, index_col=None)

    def raw_data(self, nrows=10):
        return {
            tab: df.iloc[:nrows]
            .astype("str")
            .rename(columns={col: f"col{i:03}" for i, col in enumerate(df.columns)})
            .to_dict("records")
            for tab, df in self.dfs.items()
        }


class CensusUploadHandler(mix.CensusProcessorLLMMixin, BaseFileHandler):
    def preprocess(self, dfs: Dict[str, pd.DataFrame]):
        data = {
            tab: {
                "start_row": self.identify_header_row(df),
                "start_col": self.identify_first_column(
                    df.iloc[self.identify_header_row(df) :]
                ),
            }
            for tab, df in dfs.items()
        }
        return data

    def select_data_range(self, dfs: Dict[str, pd.DataFrame], census_config):
        selected_tabs = [census_config["tab_name"] for census_config in census_config]
        selected_dfs = {tab: df for tab, df in dfs.items() if tab in selected_tabs}
        for tab in dfs.keys():
            self.metadata[tab]["is_tab_selected"] = tab in selected_tabs

        for config in census_config:
            tab_name = config["tab_name"]
            llm_start_row_number = config["start_row_number"] - 1
            llm_start_column_number = config["start_column_number"] - 1

            try:
                df = selected_dfs[tab_name]
            except KeyError:
                raise ValueError(f"Could not find tab {tab_name}")

            header = df.iloc[llm_start_row_number]
            df = df.iloc[(llm_start_row_number + 1) :, llm_start_column_number:]
            df.columns = header[llm_start_column_number:]

            selected_dfs[tab_name] = df
            self.metadata[tab_name]["start_row"] = llm_start_row_number
            self.metadata[tab_name]["start_col"] = llm_start_column_number

        return selected_dfs

    def map_columns(self, dfs: Dict[str, pd.DataFrame], census_config):
        for config in census_config:
            tab_name = config["tab_name"]
            if tab_name not in dfs:
                raise ValueError(f"Could not find tab {tab_name}")

            column_mapper = config["column_mapper"]
            dfs[tab_name] = dfs[tab_name].rename(columns=column_mapper)
            self.metadata[tab_name]["column_mapper"] = column_mapper
        return dfs

    def stack(self, dfs: Dict[str, pd.DataFrame]):
        schema = sch.SchemaCensusUpload(many=True)
        for tab, df in dfs.items():
            df["tab"] = tab

        df_stack = pd.concat(dfs.values(), ignore_index=True)
        data = df_stack.to_dict(orient="records")
        return schema.dump(data)

    def process(self):
        # read the file
        dfs = self.read()
        # preprocessor
        preprocessor = self.preprocess(dfs)

        # if multiple tabs, identify which tabs contain census data
        census_config = self.llm_identify_tabs_containing_censuses(
            dfs, preprocess=preprocessor
        )
        if not census_config:
            raise ValueError("Could not identify census data in the file")

        # select the data range of each tab
        dfs = self.select_data_range(dfs, census_config)

        # map the columns to the standard schema
        dfs = self.map_columns(dfs, census_config)
        # save the data to the database

        self.processed_data = self.stack(dfs)
        return self.processed_data

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
        detail_data = [
            {**row, "census_master_id": census_master.census_master_id}
            for row in self.processed_data
        ]
        census_details = sch.SchemaCensusDetail(many=True).load(detail_data)
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
