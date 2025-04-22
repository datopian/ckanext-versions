import datetime
import logging
from collections import OrderedDict
from ckan.model.types import UuidType, make_uuid
import ckan.model.meta as meta

import ckan.plugins.toolkit as tk
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Unicode,
    UniqueConstraint,
    orm,
    Index,
)

import ckan.model.domain_object as DomainObject

log = logging.getLogger(__name__)


class DatasetVersion(DomainObject.DomainObject, tk.BaseModel):
    __tablename__ = "package_version"
    __table_args__ = (
        UniqueConstraint("id", "name"),
        Index("idx_package_version_name", "name", "created"),
    )
    id = Column(UuidType, primary_key=True, default=UuidType.default)
    package_id = Column(UuidType, ForeignKey("package.id"), nullable=False)
    package_activity_id = Column(UuidType, ForeignKey("activity.id"), nullable=False)
    name = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=True)
    creator_user_id = Column(UuidType, ForeignKey("user.id"), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(DatasetVersion, self).__init__(**kwargs)
        self.id = make_uuid()
        self.package_id = kwargs.get("package_id")
        self.package_activity_id = kwargs.get("activity_id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.creator_user_id = kwargs.get("creator_user_id")
        self.created = kwargs.get("created", datetime.datetime.utcnow())

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

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new dataset version.
        """
        # create a records in the database
        # and return the version object
        version = cls(**kwargs)
        try:
            meta.Session.add(version)
            meta.Session.commit()
        except Exception as e:
            meta.Session.rollback()
            log.debug("DB integrity error (version name not unique?): %s", e)
            raise tk.ValidationError("Version names must be unique per resource")
        return version
