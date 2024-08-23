from __future__ import annotations

import decimal
from extensions import db, ma
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from marshmallow import post_dump
from flask import request
from flask_restx import Resource


class BaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        dump_only = (
            "created_dts",
            "updated_dts",
        )

    @post_dump(pass_many=True)
    def formatDecimal(self, data, many, **kwargs):
        if many:
            return [
                {
                    k: v if not isinstance(v, decimal.Decimal) else float(v)
                    for k, v in item.items()
                }
                for item in data
            ]
        else:
            new_data = {
                k: v if not isinstance(v, decimal.Decimal) else float(v)
                for k, v in data.items()
            }
            return new_data


class BaseModel(db.Model):
    __abstract__ = True

    def __repr__(self):
        """
        Print instance as <[Model Name]: [Row SK]>
        """
        return f"<{self.__class__.__name__}: {getattr(self, inspect(self.__class__).primary_key[0].name)}>"

    @declared_attr
    def created_dts(cls):
        return db.Column(
            db.DateTime,
            server_default=db.func.current_timestamp(),
        )

    @declared_attr
    def updated_dts(cls):
        return db.Column(
            db.DateTime,
            server_default=db.func.current_timestamp(),
            onupdate=db.func.current_timestamp(),
        )

    @classmethod
    def get(cls, id, *args, **kwargs) -> BaseModel:
        pk = inspect(cls).primary_key[0]
        qry = cls.query
        return qry.filter(pk == id).one_or_none()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            return self

    @classmethod
    def update(cls, id: int, attrs: dict, *args, **kwargs) -> BaseModel:
        pk = inspect(cls).primary_key[0]
        _ = attrs.pop(pk.name, None)
        rows_updated = cls.query.filter(pk == id).update(
            attrs, synchronize_session="fetch"
        )

        if rows_updated == 1:
            db.session.commit()
            return cls.query.get(id)

        db.session.rollback()
        raise ValueError("Record does not exist")

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            return True


class BaseResource(Resource):
    model: BaseModel
    schema: BaseSchema
    allowed_methods: list = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    @classmethod
    def get(cls, id, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405

        try:
            data = cls.retrieve(id, *args, **request.args, **kwargs)
            return data, 200
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def post(cls, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405
        if "id" in kwargs:
            return {"status": "error", "msg": "Route not implemented"}, 405
        try:
            req = request.get_json()
            data = cls.create(req, *args, **kwargs)
            return data, 201
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def put(cls, id, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405
        try:
            req = request.get_json()
            data = cls.replace(req, *args, **kwargs)
            return data, 201
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def patch(cls, id, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405
        try:
            req = request.get_json()
            data = cls.update(id, data=req, *args, **kwargs)
            return data, 201
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def delete(cls, id, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405
        try:
            cls.destroy(id, *args, **kwargs)
            return {"status": "success", "msg": "Successfully deleted"}
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def retrieve(cls, id, *args, **kwargs):
        obj = cls.model.get(id, *args, **kwargs)
        return cls.schema.dump(obj)

    @classmethod
    def create(cls, data, *args, **kwargs):
        obj = cls.schema.load(data)
        obj.save()
        return cls.schema.dump(obj)

    @classmethod
    def replace(cls, data, *args, **kwargs):
        obj = cls.schema.load(data)
        obj.save()
        return cls.schema.dump(obj)

    @classmethod
    def update(cls, id, data, *args, **kwargs):
        queryparams = kwargs.get("queryparams")
        if cls.validator:
            data = cls.validator.update(data, id=id, *args, **{**queryparams, **kwargs})
        obj = cls.model.update(id, data)
        return cls.schema.dump(obj)

    @classmethod
    def destroy(cls, id, *args, **kwargs):
        obj = cls.model.get(id, *args, **kwargs)
        obj.delete()


class BaseListResource(Resource):
    model: BaseModel
    schema: BaseSchema
    allowed_methods: list = ["GET"]

    @classmethod
    def get(cls, *args, **kwargs):
        if request.method not in cls.allowed_methods:
            return {"status": "error", "msg": "Method not allowed"}, 405
        try:
            data = cls.list(*args, **request.args, **kwargs)
            return data, 200
        except NotImplementedError as e:
            return {"status": "error", "msg": str(e)}, 405
        except Exception as e:
            return {"status": "error", "msg": str(e)}, 400

    @classmethod
    def list(cls, id, *args, **kwargs):
        raise NotImplementedError
