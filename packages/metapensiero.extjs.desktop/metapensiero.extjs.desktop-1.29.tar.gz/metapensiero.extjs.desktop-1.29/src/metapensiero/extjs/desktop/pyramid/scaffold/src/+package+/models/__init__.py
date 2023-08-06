# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    object_session,
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension


class AbstractBase(object):
    "Abstract base entity class."

    def delete(self):
        "Delete this instance from the database."

        object_session(self).delete(self)

    def __repr__(self):
        "Return an ASCII representation of the entity."

        from sqlalchemy.orm.exc import DetachedInstanceError

        mapper = self.__mapper__
        pkeyf = mapper.primary_key
        try:
            pkeyv = mapper.primary_key_from_instance(self)
        except DetachedInstanceError:
            keys = u"detached-instance"
        else:
            keys = u', '.join(u'%s=%s' % (f.name, v)
                              for f, v in map(None, pkeyf, pkeyv))
        return u'<%s %s>' % (# pragma: no cover
                             self.__class__.__name__, keys)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"The global SA session maker"

Base = declarative_base(cls=AbstractBase)
"The common parent class for all declarative mapped classed."

from .auth import User
