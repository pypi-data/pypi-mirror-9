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

from mock import Mock

from oslo_log import log
from neutron_lbaas.tests.unit.db.loadbalancer import test_db_loadbalancerv2

from kemptech_openstack_lbaas.client import KempClient
from kemptech_openstack_lbaas.driver import MapNeutronToKemp
from kemptech_openstack_lbaas.driver import KempLoadMasterDriver

KEMP_CLIENT_CLASS = 'kemptech_openstack_lbaas.client.KempClient'
KEMP_DRIVER_CLASS = 'neutron_lbaas.services.loadbalancer.kemptech_openstack_lbaas.driver.KempLoadMasterDriver'
LBAAS_PROVIDER_NAME = 'KEMPtechnologies'
LBAAS_PROVIDER = ('LOADBALANCERV2:%s:%s:default'
                  % (LBAAS_PROVIDER_NAME, KEMP_DRIVER_CLASS))

LOG = log.getLogger(__name__)

CONF = Mock()
CONF.lm_address = '10.0.0.1'
CONF.lm_username = 'bal'
CONF.lm_password = '2fourall'
CONF.check_interval = 9
CONF.connect_timeout = 4
CONF.retry_count = 2


class TestKempLoadMasterDriver(test_db_loadbalancerv2.LbaasPluginDbTestCase):
    """Test suite to test methods of KempLoadMasterDriver"""
    def setUp(self):
        super(TestKempLoadMasterDriver, self).setUp(lbaas_provider=LBAAS_PROVIDER)
        self.context_mock = Mock()
        self.plugin_mock = Mock()
        self.driver = KempLoadMasterDriver(self.plugin_mock)


class TestLoadBalancerManager(test_db_loadbalancerv2.LbaasLoadBalancerTests):
    """Test suite to test methods of LoadBalancerManager"""
    def __init__(self):
        super(TestLoadBalancerManager, self).__init__()
        self.client_mock = Mock(spec=KempClient)
        self.api_helper_mock = Mock(spec=MapNeutronToKemp)


class TestListenerManager(test_db_loadbalancerv2.ListenerTestBase):
    """Test suite to test methods of ListenerManager"""
    def __init__(self):
        super(TestListenerManager, self).__init__()
        self.client_mock = Mock(spec=KempClient)
        self.api_helper_mock = Mock(spec=MapNeutronToKemp)


class TestPoolManager(test_db_loadbalancerv2.PoolTestBase):
    """Test suite to test methods of PoolManager"""
    def __init__(self):
        super(TestPoolManager, self).__init__()
        self.client_mock = Mock(spec=KempClient)
        self.api_helper_mock = Mock(spec=MapNeutronToKemp)


class TestMemberManager(test_db_loadbalancerv2.MemberTestBase):
    """Test suite to test methods of MemberManager"""
    def __init__(self):
        super(TestMemberManager, self).__init__()
        self.client_mock = Mock(spec=KempClient)
        self.api_helper_mock = Mock(spec=MapNeutronToKemp)


class TestHealthMonitorManager(test_db_loadbalancerv2.HealthMonitorTestBase):
    """Test suite to test methods of KempLoadMasterDriver"""
    def __init__(self):
        super(TestHealthMonitorManager, self).__init__()
        self.client_mock = Mock(spec=KempClient)
        self.api_helper_mock = Mock(spec=MapNeutronToKemp)

