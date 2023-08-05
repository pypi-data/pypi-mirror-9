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

from flask import current_app, g
from flask.ext.login import current_user

from .models import User, Permission, PermissionLevel


def get_relationship_ids(nodeid, links):
    rel_ids = set()
    for link in links:
        if link["source"] == nodeid:
            rel_ids.add(link["target"])
        if link["target"] == nodeid:
            rel_ids.add(link["source"])
    return rel_ids

def compute_node_circles(nodes, links, center_index):
    def compute_circle(circle):
        if circle > 30:
            return # Recursion failsafe
        next_nodes = set()
        for nodeid, node in enumerate(nodes):
            if circle is not None and node.get("circle") != circle:
                continue # only consider the current circle
            next_nodes.update(get_relationship_ids(nodeid, links))
        next_nodes = [ n for n in next_nodes
                       if not nodes[n].has_key("circle") ]
        if not next_nodes:
            return # nothing left to set
        for nodeid in next_nodes:
            nodes[nodeid]["circle"] = circle + 1
        compute_circle(circle + 1)
    nodes[center_index]["circle"] = 0
    compute_circle(0)


def compute_node_branch(nodes, links):
    def compute_branch(circle):
        if circle > 30:
            return # Recursion failsafe
        next_nodes_ids = [ n["id"] for n in nodes
                           if "circle" in n and n["circle"] == circle ]
        for nodeid, node in enumerate(nodes):
            if node["id"] not in next_nodes_ids or node.has_key("branch"):
                continue
            branch = None
            for rel_id in get_relationship_ids(nodeid, links):
                rel_branch = nodes[rel_id].get("branch")
                if rel_branch is not None:
                    branch = rel_branch # TODO: allow being on multiple branches
                    #print(node["name"], "has branch", branch, "by", nodes[rel_id]["name"])
            assert branch is not None, "No branch found for %s" % node["name"]
            node["branch"] = branch
        compute_branch(circle + 1)
    first_circle = [ n for n in nodes if "circle" in n and n["circle"] == 1 ]
    for node in first_circle:
        node["branch"] = node["name"]
    compute_branch(2)


def require_permission_level(graph, level):
    if current_app.login_manager._login_disabled:
        return True
    if not current_user.is_authenticated():
        return False
    if current_user.is_master:
        return True
    perm = g.db.query(Permission).filter(
        graph_id=graph, user_email=current_user.email
        ).order_by(Permission.level.desc()).first()
    if perm is None:
        return False
    return perm.level >= level
