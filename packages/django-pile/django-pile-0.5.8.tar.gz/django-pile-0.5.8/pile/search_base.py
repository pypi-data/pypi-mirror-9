#
# Copyright (C) 2014, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Provides some base functionality for all search indexes
"""

import re

from haystack.indexes import *
from haystack.query import SearchQuerySet, AutoQuery

exact_match_re = re.compile(r'(?P<phrase>[-+]?".*?")')

# This is all required because whoost/haystack is as dumb as a post
# about logical OR between tokens in the query string.
def get_haystack_query(model, query):
    queryset = SearchQuerySet().models(model)
    exacts = exact_match_re.findall(query)
    tokens = []
    for t in exact_match_re.split(query):
        if t in exacts:
            tokens.append(t) # add quotes back
        else:
            tokens += t.split()
    for token in tokens:
        if token[0] in '+-':
            queryset = queryset.filter_and(content=AutoQuery(token.lstrip('+')))
        else:
            queryset = queryset.filter_or(content=AutoQuery(token))
    return queryset

def add_field(cls, field_name, model_attr):
    """Add a field post meta-class, not with setattr, but fields"""
    target = cls.fields
    field = CharField(model_attr=model_attr)
    field.set_instance_name(field_name)
    target[field_name] = field

    # Copied from haystack/indexes.py
    # Only check non-faceted fields for the following info.
    if not hasattr(field, 'facet_for') and field.faceted == True:
        shadow_facet_name = get_facet_field_name(field_name)
        shadow_facet_field = field.facet_class(facet_for=field_name)
        shadow_facet_field.set_instance_name(shadow_facet_name)
        target[shadow_facet_name] = shadow_facet_field

def add_fields(cls, viewcls):
    """Gather the fields from the viewcls (attributes to be searched on)"""
    for (cid, link, field) in viewcls._opts():
        add_field(cls, cid, field+'__'+link)
    for (cid, name) in viewcls.cats:
        add_field(cls, cid, cid)


