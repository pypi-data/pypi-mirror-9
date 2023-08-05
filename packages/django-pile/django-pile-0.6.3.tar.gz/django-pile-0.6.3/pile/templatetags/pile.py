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

from django.conf import settings
from django.template.base import Library
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date, timesince
from django.templatetags.tz import localtime
from django.utils import timezone

from datetime import timedelta, datetime

register = Library()

def _dt(arg):
    if not arg:
        return datetime.now(timezone.utc)
    elif isinstance(arg, (str, unicode)):
        try:
            (d,t) = arg.split(' ')
            date = [ int(i) for i in d.split('-')[:3] + t.split(':')[:3] ]
            return datetime(*(date+[0, timezone.utc]))
        except Exception:
            raise ValueError("Should be a datetime object, got string: %s" % arg)
    elif not isinstance(arg, datetime) or not arg.tzinfo:
        return datetime(arg.year, arg.month, arg.day,
                        arg.hour, arg.minute, arg.second,
                        arg.microsecond, timezone.utc)
    return arg

@register.filter("placeholder")
def add_placeholder(form, text=None):
    """Add a placeholder attribute to input widgets"""
    if text == None:
        raise ValueError("Placeholder requires text content for widget.")
    form.field.widget.attrs.update({ "placeholder": text })
    return form

@register.filter("add")
def add_filter(value, arg=1):
    """Add a number to another, default is incriment by 1"""
    return int(value) + arg

@register.filter("timetag", is_safe=True)
def timetag_filter(value, arg=None):
    """Formats a date as a time since if less than 1 day old or as a date otherwise
    Will return <time...> html tag as part of the output.
    """
    if not value:
        return
    value = _dt(value)
    arg = _dt(arg)

    if arg - value > timedelta(days=1):
        label = date(value, 'Y-m-d')
    else:
        label = timesince(value, arg) + " ago"

    return mark_safe("<time datetime=\"%s\" title=\"%s\">%s</time>" % (
        date(value, 'Y-m-d\TH:i:sO'), date(localtime(value), 'Y-m-d H:i:sO'), label))

