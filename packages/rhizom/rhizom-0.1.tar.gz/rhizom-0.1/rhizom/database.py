# -*- coding: utf-8 -*-
"""
Rhizom - Relationship grapher

Copyright (C) 2015  Aurelien Bompard <aurelien@bompard.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, unicode_literals, print_function

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from alembic import command
from alembic.config import Config as AlembicConfig


def get_session(url):
    engine = create_engine(url, convert_unicode=True)
    session = scoped_session(sessionmaker(
                    autocommit=False, autoflush=False, bind=engine))
    from .models import Base
    Base.query = session.query_property()
    return session


def init_db(url):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    engine = create_engine(url, convert_unicode=True)
    from .models import Base
    Base.metadata.create_all(bind=engine)
    alembic_cfg = AlembicConfig()
    alembic_cfg.set_main_option("script_location", "rhizom:migrations")
    command.stamp(alembic_cfg, "head")

