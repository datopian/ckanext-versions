import datetime
import logging
from collections import OrderedDict
from ckan.model.types import UuidType, make_uuid
from sqlalchemy.dialects.postgresql import JSONB
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
        UniqueConstraint("package_id", "name", name="uix_package_id_name"),
        Index("idx_package_version_name", "name", "created"),
    )
    id = Column(UuidType, primary_key=True, default=UuidType.default)
    package_id = Column(UuidType, ForeignKey("package.id", ondelete="CASCADE"), nullable=False)
    name = Column(Unicode, nullable=False)
    notes = Column(Unicode, nullable=True)
    data = Column(JSONB, nullable=False)
    creator_user_id = Column(UuidType, ForeignKey("user.id"), nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(DatasetVersion, self).__init__(**kwargs)
        self.id = make_uuid()
        self.package_id = kwargs.get("package_id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.data = kwargs.get("data", {})
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
    def get(cls, **kwargs):
        """
        Get a dataset version by its attributes.
        """
        query = meta.Session.query(cls)
        for key, value in kwargs.items():
            query = query.filter(getattr(cls, key) == value)
        return query.first()
    
    @classmethod
    def get_all(cls, **kwargs):
        """
        Get all dataset versions by their attributes.
        """
        query = meta.Session.query(cls)
        for key, value in kwargs.items():
            query = query.filter(getattr(cls, key) == value)
        return query.order_by(cls.created.desc()).all()

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

    @classmethod
    def update(cls,  **kwargs):
        """
        Update an existing dataset version.
        """
        version = None
        if kwargs.get("id"):
            version = cls.get(id=kwargs.get("id"))
            
        if not version:
            raise tk.ValidationError("Version not found")

        for key, value in kwargs.items():
            if hasattr(version, key) and key != "id":
                setattr(version, key, value)
        try:
            meta.Session.add(version)
            meta.Session.commit()
        except Exception as e:
            meta.Session.rollback()
            log.debug("DB integrity error (version name not unique?): %s", e)
            raise tk.ValidationError("Version names must be unique per resource")
        return version

    @classmethod
    def recent_versions(cls, package_id):
        """
        Get the most recent versions for a given package.
        """
        query = meta.Session.query(cls).filter_by(package_id=package_id)
        return query.order_by(cls.created.desc()).first()
