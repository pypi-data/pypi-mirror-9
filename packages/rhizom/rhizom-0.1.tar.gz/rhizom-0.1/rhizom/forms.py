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

import flask
from flask_wtf import Form
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from wtforms import (StringField, HiddenField, SelectField, BooleanField,
                     validators, widgets, FieldList)
from . import app
from .models import Person, User, Permission, PermissionLevel


def _addclass(kwargs, cssclass):
    if "class" in kwargs:
        kwargs["class"] = "{} {}".format(kwargs["class"], cssclass)
    else:
        kwargs["class"] = cssclass


class BootstrapTextInput(widgets.TextInput):

    def __call__(self, field, **kwargs):
        _addclass(kwargs, "form-control")
        return super(BootstrapTextInput, self).__call__(field, **kwargs)


class InlineTextInput(BootstrapTextInput):

    def __call__(self, field, **kwargs):
        kwargs["placeholder"] = field.label.text
        return super(InlineTextInput, self).__call__(field, **kwargs)


class SmallTextInput(InlineTextInput):

    def __call__(self, field, **kwargs):
        _addclass(kwargs, "input-sm")
        return super(SmallTextInput, self).__call__(field, **kwargs)


def strip(s):
    if s:
        return s.strip()
    else:
        return ""


class NewRelationship(Form):
    source = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=SmallTextInput())
    target = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=SmallTextInput())
    rtype =  SelectField("Type",
        validators=[validators.InputRequired()])
    dotted = BooleanField("Pointillé")


class NewAccess(Form):
    name = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=SmallTextInput())
    email = StringField("Email de connexion", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=120),
                    validators.Email()],
        widget=SmallTextInput(input_type="email"))
    level = SelectField("Niveau", filters=[int],
        validators=[validators.InputRequired()])


class NewGraph(Form):
    name = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=InlineTextInput())

class CopyGraph(Form):
    existing = SelectField(filters=[strip],
        validators=[validators.InputRequired()])


class GraphProperties(Form):
    name = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=BootstrapTextInput())
    center_id = SelectField("Centre", filters=[strip],
        validators=[validators.InputRequired()])
    anonymous = BooleanField("Anonyme par défaut")


class RelationshipTypes(Form):
    name = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=32)],
        widget=SmallTextInput())
    color = StringField("Couleur", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=32)],
        widget=SmallTextInput(input_type="color"))


def new_email(form, field):
    if flask.g.db.query(User).filter_by(
        email=field.data).count() != 0:
        raise validators.ValidationError("Email déjà utilisé.")

class UserForm(Form):
    name = StringField("Nom", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=254)],
        widget=SmallTextInput())
    email = StringField("Email de connexion", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=120),
                    validators.Email(), new_email],
        widget=SmallTextInput(input_type="email"))
