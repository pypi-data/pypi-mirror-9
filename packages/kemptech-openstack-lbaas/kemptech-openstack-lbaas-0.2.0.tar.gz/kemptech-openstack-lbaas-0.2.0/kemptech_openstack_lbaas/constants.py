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

from neutron_lbaas.services.loadbalancer import constants

ROUND_ROBIN = 'rr'
LEAST_CONNECTIONS = 'lc'
SOURCE_IP = 'sh'
PERS_SOURCE_IP = 'src'
PERS_HTTP_COOKIE = 'cookie'
PERS_ACT_COOKIE = 'active-cookie'

LB_METHODS = {
    constants.LB_METHOD_ROUND_ROBIN: ROUND_ROBIN,
    constants.LB_METHOD_LEAST_CONNECTIONS: LEAST_CONNECTIONS,
    constants.LB_METHOD_SOURCE_IP: SOURCE_IP,
}

PERSIST_OPTS = {
    constants.SESSION_PERSISTENCE_SOURCE_IP: PERS_SOURCE_IP,
    constants.SESSION_PERSISTENCE_HTTP_COOKIE: PERS_HTTP_COOKIE,
    constants.SESSION_PERSISTENCE_APP_COOKIE: PERS_ACT_COOKIE,
}

VS_ID = [
    "vs",
    "vsport",
    "vsprot",
]

RS_ID = [
    "rs",
    "rsport",
]

CHECKER_OPTS = [
    'retryinterval',
    'timeout',
    'retrycount',
]
