# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.network import network_service
from openstack import resource


class PoolMember(resource.Resource):
    resource_key = 'member'
    resources_key = 'members'
    base_path = '/pools/%(pool_id)s/members'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    # TODO(briancurtin): I can't find where this is documented.
    address = resource.prop('address')
    admin_state_up = resource.prop('admin_state_up', type=bool)
    project_id = resource.prop('tenant_id')
    protocol_port = resource.prop('protocol_port', type=int)
    pool_id = resource.prop('pool_id')
    status = resource.prop('status')
    subnet_id = resource.prop('subnet_id')
    weight = resource.prop('weight', type=int)
