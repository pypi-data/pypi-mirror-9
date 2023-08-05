# -*- coding: utf-8 -*-
# copyright 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""user interface libraries

Contains some helpers designed to help implementation of cubicweb user
interface.

This is a CW monkey patch and should disappear as soon as
https://www.cubicweb.org/ticket/4959538 is closed.

"""

__docformat__ = "restructuredtext en"

from cubicweb.utils import js_dumps, JSString

class _JSId(object):
    def __init__(self, id, parent=None):
        self.id = id
        self.parent = parent
    def __unicode__(self):
        if self.parent:
            return u'%s.%s' % (self.parent, self.id)
        return unicode(self.id)
    def __str__(self):
        return unicode(self).encode('utf8')
    def __getattr__(self, attr):
        return _JSId(attr, self)
    def __call__(self, *args):
        return _JSCallArgs(args, self)

class _JSCallArgs(_JSId):
    def __init__(self, args, parent=None):
        assert isinstance(args, tuple)
        self.args = args
        self.parent = parent
    def __unicode__(self):
        args = []
        for arg in self.args:
            if isinstance(arg, JSString):
                args.append(arg)
            else:
                args.append(js_dumps(arg))
        if self.parent:
            return u'%s(%s)' % (self.parent, ','.join(args))
        return ','.join(args)

class _JS(object):
    def __getattr__(self, attr):
        return _JSId(attr)

js = _JS()
js.__doc__ = """\
magic object to return strings suitable to call some javascript function with
the given arguments (which should be correctly typed).

>>> str(js.pouet(1, "2"))
'pouet(1,"2")'
>>> str(js.cw.pouet(1, "2"))
'cw.pouet(1,"2")'
>>> str(js.cw.pouet(1, "2").pouet(None))
'cw.pouet(1,"2").pouet(null)'
>>> str(js.cw.pouet(1, JSString("$")).pouet(None))
'cw.pouet(1,$).pouet(null)'
>>> str.js.cw.pouet({'hop': JSString('$.hop'), 'bar': None})
'cw.pouet({bar: null, hop: $.hop})'
"""
