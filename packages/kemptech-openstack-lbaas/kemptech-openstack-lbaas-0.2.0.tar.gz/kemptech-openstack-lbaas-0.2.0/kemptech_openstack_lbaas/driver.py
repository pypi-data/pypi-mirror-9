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
import client
import constants as kemp_consts

from oslo.config import cfg
from oslo_log import log

from neutron_lbaas.services.loadbalancer import constants as lb_constants
from neutron_lbaas.drivers import driver_base


LOG = log.getLogger(__name__)


class LoadBalancerManager(driver_base.BaseLoadBalancerManager):

    def __init__(self, driver):
        super(LoadBalancerManager, self).__init__(driver)
        self.client = self.driver.client
        self.api_helper = self.driver.api_helper

    def create(self, context, lb):
        LOG.debug("KEMP driver create lb: %s" % repr(lb))
        self.driver.plugin.activate_linked_entities(context, lb)

    def update(self, context, old_lb, lb):
        LOG.debug("KEMP driver update lb: %s" % repr(lb))
        self.driver.plugin.activate_linked_entities(context, lb)

    def delete(self, context, lb):
        LOG.debug("KEMP driver delete lb: %s" % repr(lb))
        prep_lb = self.api_helper.prepare_loadbalancer(lb)
        self.client.delete_virtual_services(prep_lb)
        self.driver.plugin.db.delete_loadbalancer(context, lb.id)

    def refresh(self, context, lb):
        LOG.debug("KEMP driver refresh lb: %s" % repr(lb))
        # TODO(smcgough) Compare to back end and fix inconsistencies.
        self.client.refresh_loadbalancer(lb)

    def stats(self, context, lb):
        LOG.debug("KEMP driver stats of lb: %s" % repr(lb))
        # TODO(smcgough) Return nothing for now.
        stats = {
            lb_constants.STATS_IN_BYTES: 0,
            lb_constants.STATS_OUT_BYTES: 0,
            lb_constants.STATS_ACTIVE_CONNECTIONS: 0,
            lb_constants.STATS_TOTAL_CONNECTIONS: 0,
        }
        return stats


class ListenerManager(driver_base.BaseListenerManager):

    def __init__(self, driver):
        super(ListenerManager, self).__init__(driver)
        self.client = self.driver.client
        self.api_helper = self.driver.api_helper

    def create(self, context, listener):
        LOG.debug("KEMP driver create listener: %s" % repr(listener))
        prep_listener = self.api_helper.prepare_listener(context, listener)
        self.client.create_virtual_service(prep_listener)

    def update(self, context, old_listener, listener):
        LOG.debug("KEMP driver update listener: %s" % repr(listener))
        old_prep_listener = self.api_helper.prepare_listener(context,
                                                             old_listener)
        prep_listener = self.api_helper.prepare_listener(context, listener)
        self.client.update_virtual_service(old_prep_listener, prep_listener)

    def delete(self, context, listener):
        LOG.debug("KEMP driver delete listener: %s" % repr(listener))
        prep_listener = self.api_helper.prepare_listener(context, listener)
        self.client.delete_virtual_service(prep_listener)
        self.driver.plugin.db.delete_listener(context, listener.id)


class PoolManager(driver_base.BasePoolManager):

    def __init__(self, driver):
        super(PoolManager, self).__init__(driver)
        self.client = self.driver.client
        self.api_helper = self.driver.api_helper

    def create(self, context, pool):
        LOG.debug("KEMP driver create pool: %s" % repr(pool))

    def update(self, context, old_pool, pool):
        LOG.debug("KEMP driver update pool: %s" % repr(pool))
        if old_pool['lb_method'] != pool['lb_method']:
            prep_pool = self.api_helper.prepare_pool(pool)
            self.client.update_virtual_service(prep_pool)

    def delete(self, context, pool):
        LOG.debug("KEMP driver delete pool: %s" % repr(pool))
        prep_pool = self.api_helper.prepare_pool(pool)
        self.client.delete_virtual_service(prep_pool)
        self.driver.plugin.db.delete_pool(context, pool.id)


class MemberManager(driver_base.BaseMemberManager):

    def __init__(self, driver):
        super(MemberManager, self).__init__(driver)
        self.client = self.driver.client
        self.api_helper = self.driver.api_helper

    def create(self, context, member):
        LOG.debug("KEMP driver create member: %s" % repr(member))
        prep_member = self.api_helper.prepare_member(context, member)
        self.client.create_real_server(prep_member)

    def update(self, context, old_member, member):
        LOG.debug("KEMP driver update member: %s" % repr(member))
        old_prep_member = self.api_helper.prepare_member(context, old_member)
        prep_member = self.api_helper.prepare_member(context, member)
        self.client.update_real_server(old_prep_member, prep_member)

    def delete(self, context, member):
        LOG.debug("KEMP driver delete member: %s" % repr(member))
        prep_member = self.api_helper.prepare_member(context, member)
        self.client.delete_real_server(prep_member)
        self.driver.plugin.db.delete_member(context, member.id)


class HealthMonitorManager(driver_base.BaseHealthMonitorManager):

    def __init__(self, driver):
        super(HealthMonitorManager, self).__init__(driver)
        self.client = self.driver.client
        self.api_helper = self.driver.api_helper

    def create(self, context, health_monitor):
        LOG.debug("create_pool_health_monitor. health_monitor['type']: %s"
                  % health_monitor['type'])
        check_params = self._get_health_check_params(health_monitor)
        if "http" in health_monitor['type']:
            params = self.api_helper.prepare_health_monitor(health_monitor)
            check_params.update(params)
        self.client.update_health_check(check_params)
        self.api_helper.health_monitor(health_monitor)

    def update(self, context, old_health_monitor, health_monitor):
        LOG.debug("KEMP driver update health_monitor: %s" %
                  repr(health_monitor))
        check_params = self._get_health_check_params(health_monitor)
        if "http" in health_monitor['type']:
            params = self.api_helper.prepare_health_monitor(health_monitor)
            check_params.update(params)
        self.client.update_health_check(check_params)

    def delete(self, context, health_monitor):
        LOG.debug("KEMP driver delete health_monitor: %s" %
                  repr(health_monitor))
        check_params = self._get_health_check_params(health_monitor)
        if "http" in health_monitor['type']:
            params = self.api_helper.prepare_health_monitor(health_monitor)
            check_params.update(params)
        self.client.update_health_check(check_params)
        self.driver.plugin.db.health_monitor(context, health_monitor.id)

    @staticmethod
    def _get_health_check_params(health_monitor):
        """Return health check parameters from a health monitor."""
        check_params = {
            'retryinterval': health_monitor['delay'],
            'timeout': health_monitor['timeout'],
            'retrycount': health_monitor['max_retries'],
        }
        return check_params


class MapNeutronToKemp(object):

    MAP_NEUTRON_MODEL_TO_VS = {
        'vip_address': 'vs',
        'protocol_port': 'port',
        'protocol': 'prot',
        'lb_method': 'schedule',
        'type': 'checktype',
        'http_method': 'checkuseget',
        'url_path': 'checkurl',
    }

    MAP_NEUTRON_MODEL_TO_RS = {
        'address': 'rs',
        'protocol_port': 'rsport',
        'weight': 'weight',
    }

    def __init__(self, plugin):
        self.plugin = plugin

    def prepare_listener(self, context, listener):
        loadbalancer = self.plugin.get_loadbalancer(
            context, listener['load_balancer_id']
        )
        pool = self.plugin.get_pool(context, listener['default_pool_id'])
        health_monitor = self.plugin.get_health_monitor(
            context, pool['health_monitor_id']
        )

        vs_params = {}
        for model in [listener, loadbalancer, pool, health_monitor]:
            for key in model.iterkeys():
                vs_key = self.MAP_NEUTRON_MODEL_TO_VS[key]
                value = model[key]
                if key == "lb_method":
                    vs_params[vs_key] = kemp_consts.LB_METHODS[value]
                elif key == "http_method":
                    if model[key] == "GET":
                        vs_params[vs_key] = 1
                    else:
                        vs_params[vs_key] = 0
                else:
                    vs_params[vs_key] = value

        # Need to explicitly set vstype if port and
        # protocol do not meet default requirements
        if (("HTTP" in vs_params['prot']) and
            vs_params['port'] != 80 and
            vs_params['port'] != 443):
            vs_params['vstype'] = 'http'

        if pool['session_persistence'] is not None:
            for session_persist in lb_constants.SUPPORTED_SP_TYPES:
                if session_persist == pool['session_persistence']['type']:
                    persistence = kemp_consts.PERSIST_OPTS[session_persist]
                    vs_params['persist'] = persistence
                    if persistence == kemp_consts.PERS_ACT_COOKIE:
                        cookie = pool['session_persistence']['cookie_name']
                        vs_params['cookie'] = cookie
        return vs_params

    def prepare_member(self, member):
        rs_params = {}
        for key in member.iterkeys():
            rs_params[self.MAP_NEUTRON_MODEL_TO_RS[key]] = member[key]
        for key in member.pool.listener.iterkeys():
            if key in kemp_consts.VS_ID:
                rs_params[self.MAP_NEUTRON_MODEL_TO_VS[key]] = member[key]
        return rs_params

    def prepare_health_monitor(self, health_monitor):
        prep_lister = self.prepare_listener(health_monitor.pool.listener)
        return prep_lister


class KempLoadMasterDriver(driver_base.LoadBalancerBaseDriver):
    """KEMPtechnologies LBaaS driver."""

    def __init__(self, plugin, config):
        self.plugin = plugin
        self.load_balancer = LoadBalancerManager(self)
        self.listener = ListenerManager(self)
        self.pool = PoolManager(self)
        self.member = MemberManager(self)
        self.health_monitor = HealthMonitorManager(self)
        self.api_helper = self.plugin.driver.api_helper
        try:
            self.address = config.lm_address
            self.username = config.lm_username
            self.password = config.lm_password
            self.check_interval = config.check_interval
            self.connect_timeout = config.connect_timeout
            self.retry_count = config.retry_count
            self.client = client.KempClient(self.address, self.username,
                                            self.password)
        except (cfg.NoSuchOptError, client.KempClientRequestError) as error:
            LOG.error(error)
        super(KempLoadMasterDriver, self).__init__(plugin)

    @property
    def default_checker_settings(self):
        """Return default health check parameters."""
        return {
            'retryinterval': self.check_interval,
            'timeout': self.connect_timeout,
            'retrycount': self.retry_count,
        }
