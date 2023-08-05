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

import re

from enum import IntEnum

from sqlalchemy import Column, Integer, Unicode, Boolean, ForeignKey, or_
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

from flask.ext.login import UserMixin
from . import app


Base = declarative_base()


class DumpableMixin:

    dump_attr = ()

    def as_dict(self):
        return dict((a, getattr(self, a)) for a in self.dump_attr)


class Graph(Base):

    __tablename__ = 'graphs'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(254), index=True)
    anonymous = Column(Boolean, server_default=false(), nullable=False)
    persons = relationship("Person",
        backref="graph", cascade="all, delete-orphan", passive_deletes=True)
    permissions = relationship("Permission", backref="graph")

    @property
    def center_id(self):
        result = object_session(self).query(Person.id).filter_by(
            graph_id=self.id, center=True).first()
        if result is None:
            return None
        return result.id
    @center_id.setter
    def center_id(self, person_id):
        if not person_id: # 0 or None
            for p in object_session(self).query(Person).filter_by(
                graph_id=self.id, center=True):
                p.center = False
        else:
            person = object_session(self).query(Person).get(person_id)
            if person.graph_id != self.id:
                raise ValueError
            person.center = True

    def copy_from(self, graph):
        db = object_session(self)
        self.anonymous = graph.anonymous
        for perm in db.query(Permission).filter_by(graph_id=graph.id):
            db.add(Permission(graph_id=self.id,
                user_email=perm.user_email, level=perm.level))
        for person in db.query(Person).filter_by(graph_id=graph.id):
            db.add(Person(graph_id=self.id,
                name=person.name, center=person.center))
        for reltype in db.query(RelationshipType).filter_by(graph_id=graph.id):
            db.add(RelationshipType(graph_id=self.id,
                name=reltype.name, color=reltype.color))
        db.flush()
        for rel in db.query(Relationship).filter_by(graph_id=graph.id):
            source = db.query(Person).filter_by(
                graph_id=self.id, name=rel.source.name).one()
            target = db.query(Person).filter_by(
                graph_id=self.id, name=rel.target.name).one()
            db.add(Relationship(graph_id=self.id,
                source=source, target=target, type_name=rel.type_name))


class Person(Base, DumpableMixin):

    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    graph_id = Column(Integer,
        ForeignKey("graphs.id", ondelete="cascade", onupdate="cascade"),
        nullable=False)
    name = Column(Unicode(254), index=True)
    center = Column(Boolean, server_default=false(), nullable=False)

    dump_attr = ("id", "name", "center")

    def __repr__(self):
        return '<Person %r>' % (self.name)

    @property
    def relationships(self):
        targets = object_session(self).query(Person).join(
            Relationship, Person.id==Relationship.target_id
            ).filter(Relationship.source_id == self.id)
        sources = object_session(self).query(Person).join(
            Relationship, Person.id==Relationship.source_id
            ).filter(Relationship.target_id == self.id)
        return targets.union(sources).all()


class Relationship(Base, DumpableMixin):

    __tablename__ = "relationships"
    __table_args__ = (
        ForeignKeyConstraint(
            ['graph_id', 'type_name'],
            ['relationship_types.graph_id', 'relationship_types.name'],
            ondelete="cascade", onupdate="cascade"
        ),
    )

    source_id = Column(Integer,
        ForeignKey("persons.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True)
    target_id = Column(Integer,
        ForeignKey("persons.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True)
    type_name = Column(Unicode(32), primary_key=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    dotted = Column(Boolean, server_default=false(), nullable=False)
    type = relationship("RelationshipType")
    source = relationship("Person", foreign_keys=[source_id])
    target = relationship("Person", foreign_keys=[target_id])

    dump_attr = ("source_id", "target_id", "type", "dotted")

    def __repr__(self):
        return '<Relationship %r - %r (%r)>' % (
                self.source_id, self.target_id, self.type)


class RelationshipType(Base):

    __tablename__ = "relationship_types"

    graph_id = Column(Integer,
        ForeignKey("graphs.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True, nullable=False)
    name = Column(Unicode(32), primary_key=True, nullable=False)
    color = Column(Unicode(32))

    @property
    def cssname(self):
        return re.sub('[^a-z0-9-]', '', self.name.lower())

    @property
    def rel_count(self):
        return object_session(self).query(Relationship).filter_by(
            graph_id=self.graph_id, type_name=self.name).count()


class User(Base, UserMixin, DumpableMixin):

    __tablename__ = 'users'

    email = Column(Unicode(120), primary_key=True)
    name = Column(Unicode(254))
    permissions = relationship("Permission",
        backref="user", cascade="all, delete-orphan", passive_deletes=True)

    dump_attr = ("email", "name")

    def __repr__(self):
        return '<User %r>' % (self.email)

    def get_id(self):
        return self.email

    def has_perm(self, graph, level):
        if self.is_master:
            return True
        try:
            level = object_session(self).query(Permission.level
                ).with_parent(self).filter_by(
                graph_id=graph.id).one().level
        except NoResultFound:
            return False
        return level >= PermissionLevel(level)

    @property
    def is_master(self):
        return self.email in app.config.get("ADMINS", [])

    def perm_for(self, graph):
        try:
            level = object_session(self).query(Permission.level
                ).with_parent(self).filter_by(
                graph_id=graph.id).one().level
        except NoResultFound:
            return None
        return PermissionLevel(level)


class Permission(Base):

    __tablename__ = 'permissions'

    graph_id = Column(Integer,
        ForeignKey("graphs.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True)
    user_email = Column(Unicode(120),
        ForeignKey("users.email", ondelete="cascade", onupdate="cascade"),
        primary_key=True)
    level = Column(Integer)

    @property
    def level_as_string(self):
        return PermissionLevel(self.level).name


class PermissionLevel(IntEnum):
    view   = 1
    edit   = 2
    admin  = 3
