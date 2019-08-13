# encoding: utf-8

import datetime
import logging
from collections import OrderedDict

from sqlalchemy import orm, Column, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base

from ckan.model.meta import metadata
from ckan.model.types import UuidType

log = logging.getLogger(__name__)

Base = declarative_base(metadata=metadata)


class DatasetVersion(Base):
    __tablename__ = u'package_version'

    id = Column(UuidType, primary_key=True, default=UuidType.default)
    package_id = Column(UuidType, nullable=False)
    package_revision_id = Column(UuidType, nullable=False)
    name = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=True)
    creator_user_id = Column(UuidType, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def as_dict(self):
        _dict = OrderedDict()
        table = orm.class_mapper(self.__class__).mapped_table
        for col in table.c:
            val = getattr(self, col.name)
            if isinstance(val, datetime.date):
                val = str(val)
            if isinstance(val, datetime.datetime):
                val = val.isoformat()
            _dict[col.name] = val
        return _dict


def create_tables():
    DatasetVersion.__table__.create()


def tables_exist():
    return DatasetVersion.__table__.exists()
