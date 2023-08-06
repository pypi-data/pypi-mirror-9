# -*- coding: utf-8 -*-
#
#  quickapi/utils/doc.py
#  
#  Copyright 2014 Grigoriy Kramarenko <root@rosix.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
#  
from __future__ import unicode_literals

from django.utils import six
from django.utils.translation import lazy, ugettext_lazy as _


def _apidoc_lazy(header, params=_('Nothing'), data='', footer=''):
    """
    Returns formatted documentation by generic template.
    """

    template = _("""
%(header)s

#### Request parameters

%(params)s

#### Returned object

%(data)s

%(footer)s

""")
    return template % {'header':header, 'params':params, 'data':data, 'footer':footer}

apidoc_lazy = lazy(_apidoc_lazy, six.text_type)

def _combine_string(string, args=None):
    """
    Combines a template string with the passed arguments
    """
    if args is None:
        return string
    return string % args

string_lazy = lazy(_combine_string, six.text_type)

JS_BOOLEAN_TEMPLATE = """
```
#!javascript

true // %s false
```
"""

RETURN_BOOLEAN_SUCCESS = string_lazy(JS_BOOLEAN_TEMPLATE, _('if success or'))
RETURN_BOOLEAN_NOTSUCCESS = string_lazy(JS_BOOLEAN_TEMPLATE, _('if not success or'))
RETURN_BOOLEAN_EXISTS = string_lazy(JS_BOOLEAN_TEMPLATE, _('if exists or'))
RETURN_BOOLEAN_NOTEXISTS = string_lazy(JS_BOOLEAN_TEMPLATE, _('if not exists or'))

PARAMS_UPDATE_FIELD_TEMPLATE = """
    1. "pk" - %s;
    2. "field" - %s;
    3. "value" - %s.
"""

PARAMS_UPDATE_FIELD = string_lazy(PARAMS_UPDATE_FIELD_TEMPLATE,
    (_('primary key'), _('name of field'), _('new value for field')))


QUICKTABLE_PARAMS = string_lazy("""
    1. "filters" - %s;
    2. "ordering" - %s;
    3. "page" - %s;
    4. "limit" - %s.
""", (_('filters'), _('ordering'), _('page number'), _('objects per page')))


QUICKTABLE_DATA = string_lazy("""
```
#!javascript

{
    objects: [%s],
    page: 1,
    num_pages: 3,
    info: null // %s
}
```
""", (_('list of objects'), _('or specific information')))

