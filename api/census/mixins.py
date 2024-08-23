import datetime
from extensions import db
from sqlalchemy import and_, literal, func, cast, text
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce
from . import models as md


class CensusStatsMixin:
    @staticmethod
    def year(dt):
        return db.func.strftime("%Y", dt)

    @staticmethod
    def month(dt):
        return db.func.strftime("%m", dt)

    @staticmethod
    def day(dt):
        return db.func.strftime("%d", dt)

    @classmethod
    def yyyymmdd(cls, dt):
        return cls.year(dt) * 10000 + cls.month(dt) * 100 + cls.day(dt)

    @classmethod
    def base_census_query(cls, census_master_id):
        CENSUS = md.ModelCensusDetail

        qry = (
            db.session.query(
                CENSUS.census_detail_id,
                CENSUS.relationship,
                CENSUS.tobacco_disposition,
                CENSUS.issue_age,
                CENSUS.birthdate,
                CENSUS.effective_date,
                cast(
                    (cls.yyyymmdd(func.now()) - cls.yyyymmdd(CENSUS.effective_date))
                    / 10000,
                    db.Integer,
                ).label("tenure"),
            )
            .select_from(CENSUS)
            .filter(
                CENSUS.census_master_id == census_master_id,
            )
        )

        return qry

    @classmethod
    def calc_tobacco_stats(cls, qry):
        subquery = qry.subquery()
        stats = (
            db.session.query(
                subquery.c.tobacco_disposition, func.count().label("count")
            )
            .group_by(subquery.c.tobacco_disposition)
            .all()
        )
        return [row._asdict() for row in stats]

    @classmethod
    def calc_relationship_stats(cls, qry):
        subquery = qry.subquery()
        stats = (
            db.session.query(subquery.c.relationship, func.count().label("count"))
            .group_by(subquery.c.relationship)
            .all()
        )
        return [row._asdict() for row in stats]

    @classmethod
    def calc_issue_age_stats(cls, qry):
        subquery = qry.subquery()
        stats = (
            db.session.query(subquery.c.issue_age, func.count().label("count"))
            .group_by(subquery.c.issue_age)
            .all()
        )
        return [row._asdict() for row in stats]

    @classmethod
    def calc_tenure_stats(cls, qry):
        subquery = qry.subquery()
        stats = (
            db.session.query(subquery.c.tenure, func.count().label("count"))
            .group_by(subquery.c.tenure)
            .all()
        )
        return [row._asdict() for row in stats]

    @classmethod
    def get_stats(cls, census_master_id: int):
        qry = cls.base_census_query(census_master_id)
        tobacco_stats = cls.calc_tobacco_stats(qry)
        relationship_stats = cls.calc_relationship_stats(qry)
        issue_age_stats = cls.calc_issue_age_stats(qry)
        tenure_stats = cls.calc_tenure_stats(qry)
        return {
            "tobacco_stats": tobacco_stats,
            "relationship_stats": relationship_stats,
            "issue_age_stats": issue_age_stats,
            "tenure_stats": tenure_stats,
        }


class SaveAgeQueryMixin:
    @classmethod
    def base_save_age_query(cls, validated_data, offset, limit):
        CENSUS = md.ModelCensusDetail
        SAVE_AGE_RATE = md.ModelRateDetail
        NEW_RATE = aliased(md.ModelRateDetail)

        new_effective_date = datetime.datetime.strptime(
            validated_data["effective_date"], "%Y-%m-%d"
        ).date()

        qry = (
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
        )

        return qry

    @classmethod
    def calc_save_age_data(cls, qry, filters=[], sorts=None, offset=0, limit=100):
        _qry = qry.filter(*filters)
        if sorts is not None:
            _qry = _qry.order_by(text(sorts))
        return _qry.limit(limit).offset(offset).all()

    @classmethod
    def calc_save_age_stats(cls, qry):
        subquery = qry.subquery()
        stats = (
            db.session.query(
                func.count().label("count"),
                func.sum(subquery.c.save_age_rate).label("save_age_rate"),
                func.sum(subquery.c.new_rate).label("new_rate"),
                func.sum(subquery.c.diff).label("diff"),
            )
            .one()
            ._asdict()
        )
        return stats


class RateDetailMixin:
    @classmethod
    def unbounded_min(cls, data, umin="N", default_umin_value=-9999):
        if umin != "Y":
            return data
        data = sorted(data, key=lambda x: x["lower_age"])
        lowest_age = data[0]["lower_age"]
        return [
            row
            if row["lower_age"] != lowest_age
            else {**row, "lower_age": default_umin_value}
            for row in data
        ]

    @classmethod
    def unbounded_max(cls, data, umax="N", default_umax_value=9999):
        if umax != "Y":
            return data
        data = sorted(data, key=lambda x: x["upper_age"])
        highest_age = data[-1]["upper_age"]
        return [
            row
            if row["upper_age"] != highest_age
            else {**row, "upper_age": default_umax_value}
            for row in data
        ]

    @classmethod
    def modify_rate_details(cls, data, *args, **kwargs):
        data = cls.unbounded_min(data, kwargs.get("umin", "N"))
        data = cls.unbounded_max(data, kwargs.get("umax", "N"))
        return data
