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

import browserid
from flask import request, g, render_template, abort, redirect, url_for, flash, jsonify
from flask.ext.login import login_user, logout_user, current_user
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from . import app
from .models import Graph, Person, Relationship, User, Permission, PermissionLevel, RelationshipType
from .lib import compute_node_circles, compute_node_branch, require_permission_level
from .forms import (NewRelationship, NewAccess, NewGraph, CopyGraph,
                    RelationshipTypes, GraphProperties, UserForm)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # La requête doit avoir une assertion à vérifier
        if 'assertion' not in request.form:
            abort(400)
        data = browserid.verify(request.form['assertion'],
                                app.config["BROWSERID_AUDIENCE"])
        user = g.db.query(User).get(data['email'])
        if user is None:
            if g.db.query(User).count() == 0:
                user = User(email=data["email"], name="Admin")
                g.db.add(user)
                g.db.commit()
            else:
                flash("Echec de la connexion, utilisateur inconnu.", "warning")
                return redirect(url_for("index"))
        login_user(user)
        flash("Bonjour {} ! :-)".format(user.name), "success")
        # no redirect here, the JS will follow it in the AJAX request and load
        # the page twice.
        return request.args.get("next") or url_for("index")
    if current_user.is_authenticated():
        print("Already authenticated")
    return redirect(request.args.get("next") or url_for("index"))


@app.route('/logout', methods=["GET", "POST"])
def logout():
    if current_user.is_authenticated():
        name = current_user.name
        logout_user()
        flash("Déconnexion réussie, à bientôt {} !".format(name), "success")
    # no redirect here, the JS will follow it in the AJAX request and load the
    # page twice.
    return url_for('index')


@app.route('/', methods=["GET", "POST"])
def index():
    if not current_user.is_authenticated():
        graphs = []
    else:
        if current_user.is_master:
            graphs = g.db.query(Graph).order_by(Graph.id).all()
        else:
            graphs = g.db.query(Graph).join(Permission).filter(
                Permission.user_email == current_user.email,
                Permission.level >= PermissionLevel.view
                ).order_by(Graph.id).all()
    new_form = NewGraph(prefix="newgraph")
    copy_form = CopyGraph(prefix="copygraph")
    copy_form.existing.choices = [ (str(graph.id), graph.name) for graph in graphs ]
    if request.method == "POST":
        if request.form.get("formname") == "new" and new_form.validate():
            graph = Graph(name=new_form.name.data)
            g.db.add(graph)
            g.db.flush() # otherwise graph.id is None
            g.db.add(Permission(graph_id=graph.id,
                                user_email=current_user.email,
                                level=PermissionLevel.admin))
            g.db.commit()
            flash("Graphe créé", "success")
            return redirect(url_for("admin", graph_id=graph.id))
        if request.form.get("formname") == "copy" and copy_form.validate():
            existing = g.db.query(Graph).get(copy_form.existing.data)
            graph = Graph(name="Copie de {}".format(existing.name))
            g.db.add(graph)
            g.db.flush() # otherwise graph.id is None
            graph.copy_from(existing)
            # The copying user is the admin of the new graph
            myperm = g.db.query(Permission).get((graph.id, current_user.email))
            myperm.level = PermissionLevel.admin
            g.db.commit()
            flash("Graphe copié", "success")
            return redirect(url_for("admin", graph_id=graph.id))
    return render_template("index.html",
        graphs=graphs, new_form=new_form, copy_form=copy_form)


@app.route('/graph/<int:graph_id>')
def graph(graph_id):
    graph = g.db.query(Graph).get(graph_id)
    if not graph:
        return render_template("error.html",
                               code=404, message="Graphe introuvable"), 404
    if not require_permission_level(graph_id, PermissionLevel.view):
        return render_template("error.html",
                               code=403, message="Accès interdit"), 403
    rel_types = g.db.query(RelationshipType).filter_by(
        graph_id=graph_id).order_by(RelationshipType.name).all()
    return render_template("view.html", graph=graph, rel_types=rel_types)


@app.route('/api/graph/<int:graph_id>/data.js')
def data(graph_id):
    graph = g.db.query(Graph).get(graph_id)
    if not graph:
        abort(404)
    if not require_permission_level(graph_id, PermissionLevel.view):
        abort(403)
    data = {"nodes": [], "links": [], "center": None,
            "anonymous": graph.anonymous}
    node_index = {}
    for index, person in enumerate(g.db.query(Person).filter_by(
        graph_id=graph_id).order_by(Person.id)):
        node = {"id": person.id}
        #node["fixed"] = True
        if person.center:
            node.update({"size": 15, "fixed": True, "center": True})
            data["center"] = index
        node["name"] = person.name
        data["nodes"].append(node)
        node_index[person.id] = index
    siblings = {}
    for rel in g.db.query(Relationship).filter_by(graph_id=graph_id).all():
        link = {"source": node_index[rel.source_id],
                "target": node_index[rel.target_id],
                "css": rel.type.cssname.lower(),
                "dotted": rel.dotted}
        siblings_count = g.db.query(Relationship).filter_by(
            source_id=rel.source_id, target_id=rel.target_id
            ).count()
        link["siblings"] = siblings_count
        if siblings_count > 0:
            if (rel.source_id, rel.target_id) in siblings:
                siblings[(rel.source_id, rel.target_id)] += 1
                sibling_id = siblings[(rel.source_id, rel.target_id)]
            elif (rel.target_id, rel.source_id) in siblings:
                siblings[(rel.target_id, rel.source_id)] += 1
                sibling_id = siblings[(rel.target_id, rel.source_id)]
            else:
                siblings[(rel.source_id, rel.target_id)] = sibling_id = 0
            link["sibling_id"] = sibling_id
        data["links"].append(link)
    if data["center"] is not None:
        compute_node_circles(data["nodes"], data["links"], data["center"])
        compute_node_branch(data["nodes"], data["links"])
    return jsonify(**data)


@app.route('/graph/<int:graph_id>/edit', methods=["GET", "POST"])
def edit(graph_id):
    graph = g.db.query(Graph).get(graph_id)
    if not graph:
        abort(404)
    if not require_permission_level(graph_id, PermissionLevel.edit):
        return render_template("error.html",
                               code=403, message="Accès interdit"), 403
    newrel_form = NewRelationship()
    rel_types = [ rt.name for rt in g.db.query(RelationshipType.name).filter_by(
        graph_id=graph_id).order_by(RelationshipType.name) ]
    newrel_form.rtype.choices = [ (rt, rt) for rt in rel_types ]
    context = dict(
        graph = graph,
        newrel_form = newrel_form,
        relationships = g.db.query(Relationship).filter_by(
            graph_id=graph_id).order_by(Relationship.source_id).all(),
        rel_types = rel_types,
    )
    if request.method == "POST":
        if request.form.get("action") == "delete":
            sid = int(request.form["source"])
            tid = int(request.form["target"])
            ltype = request.form["origltype"]
            link = g.db.query(Relationship).filter_by(
                source_id=sid, target_id=tid, type_name=ltype).one()
            g.db.delete(link)
            g.db.flush() # flushing is required for the next step
            # Cleanup orphans
            for pid in (sid, tid):
                if g.db.query(Relationship).filter(or_(
                    Relationship.source_id == pid,
                    Relationship.target_id == pid)).count() == 0:
                    g.db.delete(g.db.query(Person).get(pid))
            g.db.commit()
            #flash("Relation supprimée", "success")
            return jsonify({"status": "OK"})
            #return redirect(url_for("edit", graph_id=graph_id))
        elif request.form.get("action") == "edit":
            sid = int(request.form["source"])
            tid = int(request.form["target"])
            ltype = request.form["origltype"]
            newltype = request.form["ltype"]
            dotted = request.form["dotted"] not in ("", "false")
            if ltype != newltype and g.db.query(Relationship).filter_by(
                source_id=sid, target_id=tid, type_name=newltype).count():
                return jsonify({"status": "error",
                                "message": "Cette relation existe déjà"})
            link = g.db.query(Relationship).filter_by(
                source_id=sid, target_id=tid, type_name=ltype).one()
            link.type_name = newltype
            link.dotted = dotted
            g.db.commit()
            flash("Relation modifiée", "success")
            return jsonify({"status": "OK"})
        elif request.form.get("action") == "add":
            if not newrel_form.validate():
                return render_template("edit.html", **context)
            try:
                source = g.db.query(Person).filter_by(
                    graph_id=graph_id, name=newrel_form.source.data).one()
            except NoResultFound:
                source = Person(graph_id=graph_id, name=newrel_form.source.data)
                g.db.add(source)
            try:
                target = g.db.query(Person).filter_by(
                    graph_id=graph_id, name=newrel_form.target.data).one()
            except NoResultFound:
                target = Person(graph_id=graph_id, name=newrel_form.target.data)
                g.db.add(target)
            g.db.flush() # flushing is required for the next step
            if source.id > target.id:
                source, target = target, source # the source is always the lowest id
            if g.db.query(Relationship).get(
                (source.id, target.id, newrel_form.rtype.data)) is not None:
                flash("Cette relation existe déjà", "warning")
                return render_template("edit.html", **context)
            newlink = Relationship(
                source_id=source.id, target_id=target.id,
                type_name=newrel_form.rtype.data, graph_id=graph.id,
                dotted=newrel_form.dotted.data)
            g.db.add(newlink)
            g.db.commit()
            flash("Relation ajoutée", "success")
            return redirect(url_for("edit", graph_id=graph_id))
    return render_template("edit.html", **context)


@app.route('/graph/<int:graph_id>/admin', methods=["GET", "POST"])
def admin(graph_id):
    graph = g.db.query(Graph).get(graph_id)
    if not graph:
        abort(404)
    if not require_permission_level(graph_id, PermissionLevel.admin):
        return render_template("error.html",
                               code=403, message="Accès interdit"), 403
    newaccess_form = NewAccess(prefix="newaccess")
    graphprops_form = GraphProperties(obj=graph, prefix="graphprops")
    graphprops_form.center_id.choices = [("0", "(personne)")] + [
        (str(p.id), p.name) for p in g.db.query(Person).filter_by(graph_id=graph_id
        ).order_by(Person.name) ]
    reltypes_form = RelationshipTypes(prefix="reltypes")
    perm_choices = [ (int(getattr(PermissionLevel, l)), n) for l, n in
                  ( ("view", "Voir"), ("edit", "Modifier"),
                    ("admin", "Administrer") ) ]
    newaccess_form.level.choices = perm_choices
    context = dict(
        graph = graph,
        graphprops_form = graphprops_form,
        reltypes_form = reltypes_form,
        newaccess_form = newaccess_form,
        permissions = g.db.query(Permission).join(User).filter(
            Permission.graph_id == graph_id).order_by(User.name).all(),
        rel_types = g.db.query(RelationshipType).filter_by(
            graph_id=graph_id).order_by(RelationshipType.name).all(),
        perm_choices = perm_choices,
    )
    if request.method == "POST":
        # Graph: properties edition
        if request.form.get("formname") == "graphprops":
            if not graphprops_form.validate():
                return render_template("admin.html", **context)
            graph.name = graphprops_form.name.data
            graph.center_id = int(graphprops_form.center_id.data)
            g.db.commit()
            flash("Graphe mis à jour", "success")
            return redirect(url_for("admin", graph_id=graph_id))
        # Permissions
        elif request.form.get("formname") == "permissions":
            if request.form.get("action") == "add":
                if not newaccess_form.validate():
                    return render_template("admin.html", **context)
                user = g.db.query(User).get(newaccess_form.email.data)
                if user is None:
                    user = User(email=newaccess_form.email.data,
                                name=newaccess_form.name.data)
                    g.db.add(user)
                perm = Permission(graph_id=graph_id,
                                  user_email=newaccess_form.email.data,
                                  level=newaccess_form.level.data)
                g.db.add(perm)
                g.db.commit()
                flash("Accès ajouté", "success")
                return redirect(url_for("admin", graph_id=graph_id))
            elif request.form.get("action") == "delete":
                perm = g.db.query(Permission).get((graph_id, request.form["email"]))
                if perm is None:
                    return jsonify({"status": "error",
                                    "message": "Invalid permission"})
                user = perm.user
                g.db.delete(perm)
                g.db.flush() # flushing is required for the next step
                if len(user.permissions) == 0:
                    g.db.delete(user) # no permissions left
                g.db.commit()
                #flash("Accès supprimé", "success")
                return jsonify({"status": "OK"})
            elif request.form.get("action") == "edit":
                perm = g.db.query(Permission).get((graph_id, request.form["email"]))
                if perm is None:
                    return jsonify({"status": "error",
                                    "message": "Invalid relationship type"})
                perm.level = request.form["level"]
                perm.user.name = request.form["name"]
                g.db.commit()
                flash("Utilisateur modifié", "success")
                return jsonify({"status": "OK"})
        ## Graph: relationship types
        elif request.form.get("formname") == "reltypes":
            if request.form.get("action") == "add":
                if not reltypes_form.validate():
                    return render_template("admin.html", **context)
                reltype = RelationshipType(graph_id=graph_id,
                                           name=reltypes_form.name.data,
                                           color=reltypes_form.color.data)
                for existing_types in g.db.query(RelationshipType
                    ).filter_by(graph_id=graph_id):
                    if reltype.cssname == existing_types.cssname:
                        reltypes_form.name.errors.append("Ce nom est déjà utilisé")
                        return render_template("admin.html", **context)
                g.db.add(reltype)
                g.db.commit()
                flash("Type de relation ajouté", "success")
                return redirect(url_for("admin", graph_id=graph_id))
            elif request.form.get("action") == "delete":
                reltype = g.db.query(RelationshipType).get(
                    (graph_id, request.form["origname"]))
                if reltype is None:
                    return jsonify({"status": "error",
                                    "message": "Invalid relationship type"})
                g.db.delete(reltype)
                g.db.commit()
                #flash("Type de relation supprimé", "success")
                return jsonify({"status": "OK"})
            elif request.form.get("action") == "edit":
                reltype = g.db.query(RelationshipType).get(
                    (graph_id, request.form["origname"]))
                if reltype is None:
                    return jsonify({"status": "error",
                                    "message": "Invalid relationship type"})
                reltype.name = request.form["name"]
                reltype.color = request.form["color"]
                g.db.commit()
                flash("Type de relation modifié", "success")
                return jsonify({"status": "OK"})
            else:
                flash("Invalid request", "danger")
        elif request.form.get("formname") == "graphdel":
            g.db.delete(graph)
            g.db.commit()
            flash("Graphe supprimé", "success")
            return redirect(url_for("index"))
    return render_template("admin.html", **context)


@app.route('/users', methods=["GET", "POST"])
def users():
    if not current_user.is_master:
        return render_template("error.html",
                               code=403, message="Accès interdit"), 403
    user_form = UserForm()
    context = dict(
        user_form = user_form,
        users = g.db.query(User).order_by(User.name).all(),
    )
    if request.method == "POST":
        if request.form.get("action") == "delete":
            user = g.db.query(User).get(request.form["email"])
            g.db.delete(user)
            g.db.commit()
            #flash("Utilisateur supprimé", "success")
            return jsonify({"status": "OK"})
            #return redirect(url_for("users"))
        elif request.form.get("action") == "edit":
            user = g.db.query(User).get(request.form["email"])
            user.name = request.form["name"]
            g.db.commit()
            flash("Utilisateur modifié", "success")
            return jsonify({"status": "OK"})
        elif request.form.get("action") == "add" and user_form.validate():
            user = User(name=user_form.name.data, email=user_form.email.data)
            g.db.add(user)
            g.db.commit()
            flash("Utilisateur ajouté", "success")
            return redirect(url_for("users"))
    return render_template("users.html", **context)


@app.route('/errors/<int:code>')
def error(code):
    return render_template("error.html", code=code), code
