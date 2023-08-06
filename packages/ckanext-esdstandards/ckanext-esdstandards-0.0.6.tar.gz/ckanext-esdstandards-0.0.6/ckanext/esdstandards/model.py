import uuid

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper, Session
from ckan import model

import logging
log = logging.getLogger(__name__)


esd_function_table = None
esd_service_table = None


def _make_uuid():
    return unicode(uuid.uuid4())


def tables_exist():
    if esd_function_table is None:
        define_esd_tables()

    return esd_function_table.exists()


def setup():
    if esd_function_table is None:
        define_esd_tables()
        log.debug('ESD Standards tables defined in memory')

    if model.package_table.exists():
        if not tables_exist():
            esd_function_table.create()
            esd_service_table.create()
            log.debug('ESD Standards  table created')
        else:
            log.debug('ESD Standards  table already exists')
    else:
        log.debug('ESD Standards  table creation deferred')


class ESDObject(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        pkg = cls.filter(**kwargs).first()
        return pkg

    @classmethod
    def create(cls, **kwargs):
        esd_function = cls(**kwargs)
        Session.add(esd_function)
        Session.commit()
        return esd_function.as_dict()


class ESDFunction(ESDObject):
    pass


class ESDService(ESDObject):
    pass


def define_esd_tables():
    global esd_function_table
    global esd_service_table

    esd_function_table = Table('esd_function', metadata,
                               Column('id', types.UnicodeText,
                                      primary_key=True,
                                      default=_make_uuid),
                               Column('esd_id', types.UnicodeText, nullable=False),
                               Column('title', types.UnicodeText),
                               Column('description', types.UnicodeText),
                               Column('uri', types.UnicodeText),
                               Column('parent', types.UnicodeText))

    mapper(ESDFunction, esd_function_table)

    esd_service_table = Table('esd_service', metadata,
                              Column('id', types.UnicodeText,
                                     primary_key=True,
                                     default=_make_uuid),
                              Column('esd_id', types.UnicodeText, nullable=False),
                              Column('title', types.UnicodeText),
                              Column('description', types.UnicodeText),
                              Column('uri', types.UnicodeText))

    mapper(ESDService, esd_service_table)
