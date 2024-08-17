import os
import pandas as pd
from io import BytesIO
from extensions import db
from . import models as md
from . import schemas as sch


class BaseFileHandler:
    def __init__(self, file):
        self.file = BytesIO(file.read())
        self.filename = file.filename
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

    @staticmethod
    def _read_excel(file):
        return pd.read_excel(file)


class CensusUploadHandler(BaseFileHandler):
    def save(self):
        # create the census master record w/o details
        census_master = {
            "census_name": self.filename,
            "census_path": self.filename,
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
