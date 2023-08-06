# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)


def entity_from_primary_key(pkname):
    """Given the name of a primary key, return the mapped entity.

    :param pkname: the name of a primary key
    :rtype: a mapped class
    """

    from sqlalchemy.orm.mapper import _mapper_registry

    for m in list(_mapper_registry):
        if len(m.primary_key) == 1 and m.primary_key[0].name == pkname:
            return m.class_
    raise Exception('Unknown PK: %s' % pkname)


def table_from_primary_key(pkname):
    """Given the name of a primary key, return the related table.

    :param pkname: the name of a primary key
    :rtype: a SQLAlchemy table
    """

    from . import Base

    for t in Base.metadata.sorted_tables:
        if len(t.primary_key.columns) == 1 and pkname in t.primary_key.columns:
            return t
    raise Exception('Unknown PK: %s' % pkname)


def save_changes(sasess, request, modified, deleted):
    """Save insertions, changes and deletions to the database.

    :param sasess: the SQLAlchemy session
    :param request: the Pyramid web request
    :param modified: a sequence of record changes, each represented by
                     a tuple of two items, the PK name and a
                     dictionary with the modified fields; if the value
                     of the PK field is null or 0 then the record is
                     considered new and will be inserted instead of updated
    :param deleted: a sequence of deletions, each represented by a tuple
                    of two items, the PK name and the ID of the record to
                    be removed
    :rtype: a tuple of three lists, respectively inserted, modified and
            deleted record IDs, grouped in a dictionary keyed on PK name.
    """

    iids = []
    mids = []
    dids = []

    # Dictionary with last inserted PK ids: each newly inserted
    # primary key (records with id==0) is stored here by name, and
    # used for the homonym FK with value of 0. This let us insert a
    # new master record with its details in a single call.
    last_ins_ids = {}

    for key, mdata in modified:
        entity = entity_from_primary_key(key)
        table = entity.__table__

        fvalues = {}
        for f, v in mdata.items():
            if f in table.c and f != key:
                if v != '':
                    fvalues[f] = v
                else:
                    fvalues[f] = None

        # Update the NULL foreign keys with previously
        # inserted master ids
        for lik in last_ins_ids:
            if lik != key and fvalues.get(lik) == 0:
                fvalues[lik] = last_ins_ids[lik]

        # If there are no changes, do not do anything
        if not fvalues:
            continue

        # If the PK is missing or None, assume it's a new record
        idrecord = int(mdata.get(key) or 0)

        if idrecord == 0:
            instance = entity(**fvalues)
            sasess.add(instance)
            sasess.flush()
            nextid = getattr(instance, key)
            iids.append({key: nextid})
            last_ins_ids[key] = nextid
        else:
            instance = sasess.query(entity).get(idrecord)
            if instance is not None:
                mids.append({key: idrecord})
                for f, v in fvalues.items():
                    setattr(instance, f, v)
                sasess.flush()

    for key, ddata in deleted:
        entity = entity_from_primary_key(key)
        instance = sasess.query(entity).get(ddata)
        if instance is not None:
            instance.delete()
            dids.append({key: ddata})

    return iids, mids, dids
