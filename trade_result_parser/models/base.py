from sqlalchemy.orm import declarative_base

from .mixins import IdPrimaryKeyMixin


class BaseModel(IdPrimaryKeyMixin, declarative_base()):
    __abstract__ = True
