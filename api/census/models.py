from extensions import db
from sqlalchemy import cast
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from shared import BaseModel


class ModelCensusMaster(BaseModel):
    __tablename__ = "census_master"

    census_master_id = db.Column(db.Integer, primary_key=True)
    census_name = db.Column(db.String(200))
    census_path = db.Column(db.String(1000))

    census_details = db.relationship(
        "ModelCensusDetail", backref="census_master", cascade="all,delete"
    )


class ModelCensusDetail(BaseModel):
    __tablename__ = "census_detail"

    census_detail_id = db.Column(db.Integer, primary_key=True)
    census_master_id = db.Column(
        db.ForeignKey(
            "census_master.census_master_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
    )
    birthdate = db.Column(db.Date, nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    tobacco_disposition = db.Column(db.String(50), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)

    @staticmethod
    def year(dt):
        return db.func.strftime("%Y", dt)

    @staticmethod
    def month(dt):
        return db.func.strftime("%m", dt)

    @staticmethod
    def day(dt):
        return db.func.strftime("%d", dt)

    @hybrid_property
    def issue_age(self):
        return (
            (
                self.effective_date.year * 10000
                + self.effective_date.month * 100
                - self.effective_date.day
            )
            - (
                self.birthdate.year * 10000
                + self.birthdate.month * 100
                - self.birthdate.day
            )
        ) // 10000

    @issue_age.expression
    def issue_age(cls):
        return cast(
            (
                (
                    cls.year(cls.effective_date) * 10000
                    + cls.month(cls.effective_date) * 100
                    + cls.day(cls.effective_date)
                )
                - (
                    cls.year(cls.birthdate) * 10000
                    + cls.month(cls.birthdate) * 100
                    + cls.day(cls.birthdate)
                )
            )
            / 10000,
            db.Integer,
        )

    @hybrid_method
    def issue_age_as_of(self, effective_date):
        return (
            (
                effective_date.year * 10000
                + effective_date.month * 100
                - effective_date.day
            )
            - (
                self.birthdate.year * 10000
                + self.birthdate.month * 100
                - self.birthdate.day
            )
        ) // 10000

    @issue_age_as_of.expression
    def issue_age_as_of(cls, effective_date):
        return cast(
            (
                (
                    cls.year(effective_date) * 10000
                    + cls.month(effective_date) * 100
                    + cls.day(effective_date)
                )
                - (
                    cls.year(cls.birthdate) * 10000
                    + cls.month(cls.birthdate) * 100
                    + cls.day(cls.birthdate)
                )
            )
            / 10000,
            db.Integer,
        )


class ModelRateMaster(BaseModel):
    __tablename__ = "rate_master"

    rate_master_id = db.Column(db.Integer, primary_key=True)
    rate_master_name = db.Column(db.String(200))

    rate_details = db.relationship(
        "ModelRateDetail", backref="rate_master", cascade="all,delete"
    )


class ModelRateDetail(BaseModel):
    __tablename__ = "rate_detail"

    rate_detail_id = db.Column(db.Integer, primary_key=True)
    rate_master_id = db.Column(
        db.ForeignKey(
            "rate_master.rate_master_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
    )
    lower_age = db.Column(db.Integer, nullable=False)
    upper_age = db.Column(db.Integer, nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    tobacco_disposition = db.Column(db.String(50), nullable=False)
    rate = db.Column(db.Float, nullable=False)
