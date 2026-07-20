from sqlalchemy.orm import DeclarativeBase

from .mixins import IdPrimaryKeyMixin


class BaseModel(IdPrimaryKeyMixin, DeclarativeBase):
    __abstract__ = True
