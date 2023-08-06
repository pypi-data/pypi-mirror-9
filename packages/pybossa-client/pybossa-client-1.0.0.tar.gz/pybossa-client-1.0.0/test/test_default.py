# -*- coding: utf8 -*-
# Copyright (C) 2013 Daniel Lombraña González
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pbclient
from mock import patch
from base import TestPyBossaClient
from nose.tools import assert_raises


class TestPybossaClientDefaults(TestPyBossaClient):

    def test_set(self):
        """Test setter works."""
        from pbclient import _opts
        pbclient.set('foo', 'bar')
        assert 'foo' in _opts.keys()
        assert _opts['foo'] == 'bar'

    def test_domain_object(self):
        data = {'foo': 'bar'}
        obj = pbclient.DomainObject(data)
        assert 'foo' in obj.__dict__['data'].keys()
        assert obj.__dict__['data'] == data
        assert obj.foo == 'bar'

    def test_domain_object_data(self):
        obj = pbclient.DomainObject({})
        obj.data = {'foo': 'bar'}
        assert getattr(obj, 'data')['foo'] == 'bar', obj.data

    def test_domain_object_update_value(self):
        data = {'foo': 'bar'}
        obj = pbclient.DomainObject(data)
        obj.foo = 'two'
        assert obj.foo == 'two'

    def test_domain_object_set_unkown_val(self):
        data = {'foo': 'bar'}
        obj = pbclient.DomainObject(data)
        assert_raises(AttributeError, setattr, obj, 'bar', 'three')

    def test_domain_object_error(self):
        data = {'foo': 'bar'}
        obj = pbclient.DomainObject(data)
        assert_raises(AttributeError, getattr, obj, 'nonething')
