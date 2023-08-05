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
Provides as very good filtering system with automatic category generation
for ListView. This allows multiple categories to be specified and for them
to automatically filter the list.

Supports both url based key words e.g. /(?<category>\w+)/ and
get kwargs on the request. Define the urls with the right category id
to get automatic url based atrtirubution.

Example in views.py:

class MyView(CategoryListView):
    model = my_model
    cats = ('status', _("Status")),\
           ('type', _("Type")),\
           ('foo', _("Bar"), Baz),
    opts = ('user', 'username'),

in urls.py:

url('^$', MyView.as_view(), name='myview')
url('^(?P<type>[\w-]+)/$', MyView.as_view(), name='myview')

In this example our ListView is created as normal with a model.
It also specifies a cats class attribute which defines each category
and it's title that will appear in the template.

Status is a ForeignKey on my_model and this will generate a list of selectable
status items which when selected will filter my_model via it's status=item link
The value of status is passed in via the request.GET dictionary. Generated urls
for each selectable item will include the attribute after the quest mark

e.g. /url/?status=value

Type does the same as status, but instead of the attribute existing in the GET
dictionary, it will be passed in via the url kwargs. These are automatically
detected so there isn't any further boilerplait code.

e.g. /type1/

foo acts differently. Where status and type are ForeignKey fields and the linked
model is detected automatically. foo isn't a foreignkey field. We pass in the
categories model which will be listed and the lookup is done on it's direct value
instead of it's link id.

The code depends on a 'value' field or object property existing on each of the
category objects in order to get it's 'slug' name rather than it's display name.

opts contains similar filtering as cats, but are not displayed. They are either
selected by previous/other pages or are selected via simple links which reset
all other category selections.

This allows filtering of fields that don't appear in the category list.

The CategoryFeed allows the same categories to be turned into an rss feed.

All View classes don't need as_view() and can be created directly from urls.
"""

__all__ = ('get_url', 'CategoryListView', 'CategoryFeed')

from django.contrib.syndication.views import Feed
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic.base import TemplateView as View, View as BaseView
from django.core.urlresolvers import reverse, get_resolver
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote
from django.db.models import Model

import types
import sys

from .base import *
from .search_base import get_haystack_query, MR_OD, RMR_OD

#
# Note: We understand we are playing with fire when we change the way the django view
# interface works, but these modifications make the API much easier to use and it is
# my fondest hope that such improvements go into future django versions.
#

def _as_view_call(self, request, *args, **kwargs):
    """Remove the need for as_view() in urls"""
    if hasattr(self, 'get') and not hasattr(self, 'head'):
        self.head = self.get
    self.request = request
    self.args = args
    self.kwargs = kwargs
    return self.dispatch(request, *args, **kwargs)
def _get_datum(self, key, *args):
    """Many views need data, django hides this data behind GET and POST"""
    return self.request.POST.get(key, self.request.GET.get(key, *args))

for (name, arg) in locals().items():
    # MOKEY-PATCHING: Insert the caller into any view without a caller
    if isinstance(arg, (type, types.ClassType)) and issubclass(arg, BaseView):
        arg.__call__ = _as_view_call
        arg.gost = _get_datum
        if 'Base' not in name:
            __all__ += name,

class AllCategory(object):
    """A simple object for 'All' Menu Item"""
    value = None

    @property
    def name(self):
        return _("All")

    def __str__(self):
        return "All"

class Category(list):
    """A menu of items in this category, created by ListView"""
    def __init__(self, view, queryset, cid, name=None):
        self.value = view.get_value(cid)

        self.name = name or cid.replace('_',' ').title()
        self.cid  = cid
        self.item = AllCategory()
        
        # Populate items, mostly these models don't have slug columns.
        self.append( self.item )
        for item in queryset:
            if self.value is not None and item.value == self.value:
                self.item = item
            self.append(item)
        for item in self:
            item.url = delay_call(view.get_url, cid, item.value)
            item.count = delay_call(view.get_count, cid, item)

    def active_items(self):
        return [ item for item in self if item.count() ]

    def count(self):
        """Returns the number of active items"""
        return len(self.active_items()) - 1

    def __str__(self):
        return self.name

    def __eq__(self, value):
        return self.item == value

    def __nonzero__(self):
        return self.item != self[0]


class CategoryListView(View):
    """ListView with categorisation functionality, provides a simple way to
    Define a set of categories and have them availab ein the template with urls"""
    cats = ()
    opts = ()
    orders = ()
    rss_view = None
    redirect = False
    using = 'default'

    def base_queryset(self):
        return self.model._default_manager.all()

    def get_queryset(self, **kwargs):
        self.query = self.get_value('q', None)
        def _get(cat):
            field = getattr(self.model, cat.cid, None)
            if field and (not isinstance(field, (MR_OD, RMR_OD)) or not self.query):
                return cat.item
            return cat.item.value

        if self.query:
            queryset = get_haystack_query(self.query, using=self.using,
                models=(self.model,))
        else:
            queryset = self.base_queryset()
        filters = dict((cat.cid, _get(cat)) for cat in self.get_cats() if cat)

        filters.update(clean_dict(dict(self.get_opts())))
        filters.update(kwargs)
        qs = queryset.filter(**clean_dict(filters, {'True':True,'False':False}))
        ob = self.get_value('order')
        if ob:
            try:
                return qs.order_by(ob)
            except:
                pass
        return qs

    def get_url(self, cid=None, value=None, view=None, exclude=None):
        kwargs = self.kwargs.copy()
        gets = self.request.GET.copy()
        view = view or self.request.resolver_match.url_name
        if cid is not None:
            args = list(self.get_possible_args(view))
            target = kwargs if cid in args else gets
            if value is None:
                target.pop(cid, None)
            else:
                target[cid] = value
        url = get_url(view, **kwargs)
        if gets:
            # Always remove page, start from begining
            gets.pop('page', None)
            get = ('&'.join('%s=%s' % (a,urlquote(b)) for (a,b) in gets.items() if a != exclude))
            if get:
                url += '?' + get
        return url

    @cached
    def get_possible_args(self, view_name):
        """Returns a generator with all possible kwargs for this view name"""
        resolver = get_resolver(None)
        possibilities = resolver.reverse_dict.getlist(view_name)
        for possibility, pattern, defaults in possibilities:
            for r, params in possibility:
                for p in params:
                    # Remove non-keyword arguments
                    if p[0] != '_':
                        yield p

    def get_count(self, cid, item=None, value=None):
        if not hasattr(self.model, cid):
            item = item.value
        if item is None or getattr(item, 'value', item) is None:
            item = None
        return self.get_queryset(**{cid: item}).count()

    def get_value(self, cid, default=None):
        return self.kwargs.get(cid, self.request.GET.get(cid, default))

    @cached
    def get_opts(self):
        return [self.get_opt(*opt) for opt in self._opts()]

    @classmethod
    def _opts(cls):
        """Returns a set of filtered links for manually defined options"""
        for (cid, link) in cls.opts:
            field = cid
            if '__' in link:
                (nfield, rest) = link.split('__', 1)
                if not hasattr(cls.model, field)\
                   and hasattr(cls.model, nfield):
                     (field, link) = (nfield, rest)
            yield (cid, link, field)
        # Yield extra options here via automatic association?

    def get_opt(self, cid, link, field, context=False):
        """Returns a value suitable for filtering"""
        value = self.get_value(cid)
        if self.query and not context:
            # No object lookup for haystack search
            return (cid, value)

        if value is not None:
            if hasattr(self.model, field):
                mfield = getattr(self.model, field)
                try:
                    values = mfield.get_query_set().filter(**{link: value})
                    if values.count() == 1:
                        value = values[0]
                    else:
                        value = [ v for v in values ]
                        field = field + '__in'
                except mfield.field.rel.to.DoesNotExist:
                    value = None
            elif link.split('__')[-1] in ('isnull',):
                field = link
            elif link and not context:
                raise ValueError("Can't find the model for field: %s.%s" % (self.model.__name__, link))
        return (context and cid or field, value)

    @cached
    def get_value_opts(self):
        """Similar to get_opt, but returns value useful for templates"""
        return [self.get_opt(*opt, context=True) for opt in self._opts() ]

    @cached
    def get_cats(self):
        return [ self.get_cat(*cat) for cat in self.cats ]

    def get_cat(self, cid, name, model=None):
        # We could move this into Category class XXX
        field = getattr(self.model, cid, None)
        if field and hasattr(field, 'get_query_set'):
            qs = field.get_query_set()
        elif model:
            if isinstance(model, Model):
                qs = model.objects.all()
            elif isinstance(model, basestring):
                qs = getattr(self, model)()
        else:
            raise KeyError(("The field '%s' isn't a ForeignKey, please add "
                           "the linked model for this category.") % cid)
        return Category(self, qs, cid, name)

    def get(self, *args, **kwargs):
        qs = self.get_queryset()
        if self.redirect and not self.query and qs.count() == 1:
            item = qs.get()
            if hasattr(item, 'get_absolute_url'):
                return redirect( item.get_absolute_url() )
        context = self.get_context_data(object_list=qs)
        return self.render_to_response(context)

    def get_template_names(self):
        opts = self.model._meta
        return ["%s/%s_list.html" % (opts.app_label, opts.object_name.lower())]
 
    def get_context_data(self, **data):
        # this allows search results and object queries to work the same way.
        if not hasattr(self.model, 'object'):
            self.model.object = lambda self: self

        data['query'] = self.get_value('q')
        data['orders'] = self.get_orders()
        data['categories'] = self.get_cats()
        data.update(((cat.cid, cat.item) for cat in self.get_cats() if cat))
        data.update(self.get_value_opts())
        
        if self.rss_view:
            data['rss_url'] = self.get_url(view=self.rss_view)
        data['clear_url'] = self.get_url(exclude='q')
        return data

    def get_orders(self):
        order = self.get_value('order', self.orders[0][0])
        for (o, label) in self.orders:
            yield { 'id': o, 'name': label, 'down': '-' == (order or '*')[0],
                'active': order.strip('-') == o.strip('-'),
                'url': self.get_url('order', reverse_order(o, o == order)) }

def reverse_order(o, active=True):
    if not active:
        return o
    if o[0] == '-':
        return o[1:]
    return '-' + o


class CategoryFeed(Feed):
    """So these CategoryListViews can become Feeds we have to do a few bits for django"""
    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        return Feed.__call__(self, request, *args, **kwargs)

    def items(self):
        return self.get_queryset()

    def link(self):
        return self.get_url()

    # XXX it might be possible to generate a title and description here.


def breadcrumbs(*args):
    yield ('/', _('Home'))
    # XXX We could automatically navigate items here using a parent meta type.
    for model in args:
        if type(model) is str:
            yield ("", _(model))
        elif isinstance(model, tuple):
            (link, name) = model
            if type(link) is str:
                yield (reverse(link), _(name))
            else:
                yield (link.get_absolute_url(), _(name))
        elif model is None:
            pass
        elif not hasattr(model, "get_absolute_url"):
            raise ValueError("Refusing the make '%s' into a breadcrumb!" % str(model))
        else:
            yield (model.get_absolute_url(), unicode(model))

