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

from __future__ import unicode_literals, print_function

import os
import json
from optparse import OptionParser

from sqlalchemy.orm.exc import NoResultFound
from alembic import command
from alembic.config import Config as AlembicConfig

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rhizom import app
from rhizom.database import init_db, get_session
from rhizom.models import Person, Relationship, User



def initdb(args):
    init_db(app.config["SQLALCHEMY_DATABASE_URI"])


def runserver(args):
    if args:
        app.run(port=int(args[0]))
    else:
        app.run()


def main():
    if len(sys.argv) < 2:
        print("wrong number of arguments.", file=sys.stderr)
        sys.exit(2)
    funcname = sys.argv[1]
    localnames = locals().keys()
    funcnames = [ n for n in localnames
                  if callable(locals()[n]) and n != "main" ]
    if funcname in ("-h", "--help"):
        print("Available scripts: {}".format(", ".join(funcnames)))
        sys.exit(2)
    if funcname not in funcnames:
        print("no such script: {}.".format(funcname), file=sys.stderr)
        sys.exit(2)
    locals()[funcname](sys.argv[2:])


if __name__ == '__main__':
    main()
