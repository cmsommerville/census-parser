import os
import json
import pandas as pd
import datetime
import anthropic
from typing import Dict
from extensions import db
from sqlalchemy import and_, literal, func, cast, text, case
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import coalesce
from . import models as md
from . import schemas as sch


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
        q = db.session.query(
            func.count().label("count"),
            func.sum(subquery.c.save_age_rate).label("save_age_rate"),
            func.sum(subquery.c.new_rate).label("new_rate"),
            func.sum(subquery.c.diff).label("diff"),
            func.count(
                case(
                    (
                        subquery.c.diff / subquery.c.save_age_rate <= 0,
                        literal(1),
                    ),
                    else_=None,
                )
            ).label("pct_range_le_0"),
            func.count(
                case(
                    (
                        and_(
                            subquery.c.diff / subquery.c.save_age_rate > 0,
                            subquery.c.diff / subquery.c.save_age_rate <= 0.05,
                        ),
                        literal(1),
                    ),
                    else_=None,
                )
            ).label("pct_range_00_05"),
            func.count(
                case(
                    (
                        and_(
                            subquery.c.diff / subquery.c.save_age_rate > 0.05,
                            subquery.c.diff / subquery.c.save_age_rate <= 0.1,
                        ),
                        literal(1),
                    ),
                    else_=None,
                )
            ).label("pct_range_05_10"),
            func.count(
                case(
                    (
                        and_(
                            subquery.c.diff / subquery.c.save_age_rate > 0.1,
                            subquery.c.diff / subquery.c.save_age_rate <= 0.2,
                        ),
                        literal(1),
                    ),
                    else_=None,
                )
            ).label("pct_range_10_20"),
            func.count(
                case(
                    (
                        subquery.c.diff / subquery.c.save_age_rate > 0.2,
                        literal(1),
                    ),
                    else_=None,
                )
            ).label("pct_range_gt_20"),
        )
        stats = q.one()._asdict()
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


class CensusProcessorLLMMixin:
    LLM_CLIENT = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    SYSTEM_PROMPT__TABS_CONTAINING_CENSUSES = """
    The prompt contains multiple Excel tabs, each of which has its data concatentated together in a comma-separated string.
    Your job is to identify which tabs, if any, contain census data. 
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
    If a file contains census data, you should return: 
    - The tab name
    - The row number containing the column names
    - The column number of the first column in the data
    - A mapper which maps the column names in the file to the required columns
    The row containing the column names must be the first row in the tab with more than 50% non-empty cells. 
    Return the data in the following format:
    [
        {
            "tab_name": "Sheet1",
            "start_row_number": 1,
            "start_column_number": 1,
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
    Use 1-based indexing for row and column numbers.
    The keys in the column_mapper should be the current column names. 
    The values should be the required column names.
    Be concise. Do not include any extraneous information.
"""
    SYSTEM_PROMPT__COLUMN_MAPPER = """
    The prompt contains data from a single Excel tab whose data is concatentated together in a comma-separated string.
    Your job is to map the columns into a common schema with the following columns: 
    - relationship
    - tobacco_disposition
    - effective_date
    The file will also contain at least one of 
    - birthdate
    - issue_age
    The columns may be named differently. 
    There may be blank rows and columns at the top of the file.
    There may be more columns than those listed, but those are the minimum required columns.
    You should return a mapper which maps the column names in the file to the required columns
    Return the data in the following format:
        {
            "column_mapper": {
                "relationship": "relationship",
                "tobacco_disposition": "tobacco_disposition",
                "effective_date": "effective_date",
                "birthdate": "birthdate", 
                "issue_age": "issue_age"
            }
        }
    The keys in the column_mapper should be the current column names. 
    The values should be the required column names.
    Be concise. Do not include any extraneous information.
"""

    @classmethod
    def tab_to_text(cls, dfs: Dict[str, pd.DataFrame], nrow=20, *args, **kwargs):
        return {
            tab: df.iloc[:nrow].to_csv(index=False, header=False)
            for tab, df in dfs.items()
            if df is not None
        }

    @classmethod
    def preprocessor_to_text(cls, data: Dict[str, Dict[str, int]]):
        return ". ".join(
            [
                f"I believe that tab, `{tab_name}`, has data starting in row {vals['start_row'] + 1} and column {vals['start_col'] + 1}"
                for tab_name, vals in data.items()
                if vals["start_row"] is not None and vals["start_col"] is not None
            ]
        )

    @classmethod
    def llm_identify_tabs_containing_censuses(
        cls, dfs: Dict[str, pd.DataFrame], preprocess=None, **kwargs
    ):
        tab_strings = cls.tab_to_text(dfs, **kwargs)
        prompt = "\n\n".join(
            [f"{tab}\n{tab_string}" for tab, tab_string in tab_strings.items()]
        )
        system_prompt = cls.SYSTEM_PROMPT__TABS_CONTAINING_CENSUSES
        if preprocess is not None:
            system_prompt = (
                system_prompt + "\n\n" + cls.preprocessor_to_text(preprocess)
            )

        message = cls.LLM_CLIENT.messages.create(
            model=os.getenv("ANTHROPIC_MODEL_ID"),
            system=system_prompt,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            mapper = [json.loads(msg.text) for msg in message.content][0]
            schema = sch.SchemaCensusConfigLLM(many=True)
            mapper = schema.load(mapper)
        except Exception:
            raise ValueError("Unable to process the file by the LLM")
        else:
            return mapper

    @classmethod
    def llm_identify_column_mapping(cls, df: pd.DataFrame, **kwargs):
        prompt = cls.tab_to_text({"default": df}, **kwargs)["default"]

        message = cls.LLM_CLIENT.messages.create(
            model=os.getenv("ANTHROPIC_MODEL_ID"),
            system=cls.SYSTEM_PROMPT__COLUMN_MAPPER,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            mapper = [json.loads(msg.text) for msg in message.content][0]
        except Exception:
            raise ValueError("Unable to process column mapping provided by the LLM")
        else:
            return mapper
