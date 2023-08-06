#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
import logging as log
import unittest

import mock

from kemptech_openstack_lbaas import driver as kemptech
from kemptech_openstack_lbaas import client

LOG = log.getLogger(__name__)

CONF = mock.Mock()
CONF.lm_address = '10.0.0.1'
CONF.lm_username = 'bal'
CONF.lm_password = '2fourall'
CONF.check_interval = 9
CONF.connect_timeout = 4
CONF.retry_count = 2


class TestKempLoadMasterDriver(unittest.TestCase):
    """Test suite to test methods of KempLoadMasterDriver."""
    def setUp(self):

        self.plugin_mock = mock.Mock()
        self.driver = kemptech.KempLoadMasterDriver(self.plugin_mock)


class TestLoadBalancerManager(unittest.TestCase):
    """Test suite to test methods of LoadBalancerManager."""
    def setUp(self):
        self.client_mock = mock.Mock(spec=client.KempClient)
        self.api_helper_mock = mock.Mock(spec=kemptech.MapNeutronToKemp)
        self.lb = kemptech.LoadBalancerManager()

    def test_create(self, model):
        self.lb.create(model)

    def test_update(self, old_model, model):
        self.lb.update(old_model, model)

    def test_delete(self, model):
        self.lb.delete(model)


class TestListenerManager(unittest.TestCase):
    """Test suite to test methods of ListenerManager."""
    def setUp(self):
        super(TestListenerManager, self).__init__()
        self.client_mock = mock.Mock(spec=client.KempClient)
        self.api_helper_mock = mock.Mock(spec=kemptech.MapNeutronToKemp)
        self.listener = kemptech.ListenerManager()

    def test_create(self, model):
        self.lb.create(model)

    def test_update(self, old_model, model):
        self.lb.update(old_model, model)

    def test_delete(self, model):
        self.lb.delete(model)

class TestPoolManager(unittest.TestCase):
    """Test suite to test methods of PoolManager."""
    def setUp(self):
        super(TestPoolManager, self).__init__()
        self.client_mock = mock.Mock(spec=client.KempClient)
        self.api_helper_mock = mock.Mock(spec=kemptech.MapNeutronToKemp)
        self.pool = kemptech.PoolManager()

    def test_create(self, model):
        self.pool.create(model)

    def test_update(self, old_model, model):
        self.pool.update(old_model, model)

    def test_delete(self, model):
        self.pool.delete(model)


class TestMemberManager(unittest.TestCase):
    """Test suite to test methods of MemberManager."""
    def setUp(self):
        super(TestMemberManager, self).__init__()
        self.client_mock = mock.Mock(spec=client.KempClient)
        self.api_helper_mock = mock.Mock(spec=kemptech.MapNeutronToKemp)
        self.member = kemptech.MemberManager()

    def test_create(self, model):
        self.member.create(model)

    def test_update(self, old_model, model):
        self.member.update(old_model, model)

    def test_delete(self, model):
        self.member.delete(model)


class TestHealthMonitorManager(unittest.TestCase):
    """Test suite to test methods of KempLoadMasterDriver."""
    def setUp(self):
        super(TestHealthMonitorManager, self).__init__()
        self.client_mock = mock.Mock(spec=client.KempClient)
        self.api_helper_mock = mock.Mock(spec=kemptech.MapNeutronToKemp)
        self.hm = kemptech.HealthMonitorManager()

    def test_create(self, model):
        self.hm.create(model)

    def test_update(self, old_model, model):
        self.hm.update(old_model, model)

    def test_delete(self, model):
        self.hm.delete(model)

