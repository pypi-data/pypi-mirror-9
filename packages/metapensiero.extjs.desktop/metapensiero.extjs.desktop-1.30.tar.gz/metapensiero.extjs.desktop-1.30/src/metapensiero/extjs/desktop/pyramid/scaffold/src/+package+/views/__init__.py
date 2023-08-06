# -*- coding: utf-8 -*-

from metapensiero.sqlalchemy.proxy.pyramid import expose

from ..models import DBSession
from ..models.utils import save_changes


# Configure the `expose` decorator
expose.create_session = staticmethod(lambda request: DBSession())
expose.save_changes = staticmethod(save_changes)
