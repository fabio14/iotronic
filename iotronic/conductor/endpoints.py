# coding=utf-8

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from iotronic.common import exception
from iotronic import objects
from iotronic.objects import base as objects_base
from oslo_log import log as logging


LOG = logging.getLogger(__name__)

serializer = objects_base.IotronicObjectSerializer()


class ConductorEndpoint(object):
    def echo(self, ctx, data):
        LOG.info("ECHO: %s" % data)
        return data

    def registration(self, ctx, token, session_num):
        LOG.debug('Receved registration from %s with session %s',
                  token, session_num)
        try:
            node = objects.Node.get_by_code({}, token)
        except Exception:
            return exception.NodeNotFound(node=token)
        try:
            old_session = objects.SessionWP(
                {}).get_session_by_node_uuid(node.uuid, valid=True)
            old_session.valid = False
            old_session.save()
        except Exception:
            LOG.debug('valid session for %s Not found', node.uuid)

        session = objects.SessionWP({})
        session.node_id = node.id
        session.node_uuid = node.uuid
        session.session_id = session_num
        session.create()
        session.save()

        return

    def destroy_node(self, ctx, node_id):
        LOG.debug('Destroying node with id %s',
                  node_id)
        node = objects.Node.get_by_uuid(ctx, node_id)
        node.destroy()
        return {}

    def create_node(self, ctx, node_obj, location_obj):
        new_node = serializer.deserialize_entity(ctx, node_obj)
        LOG.debug('Creating node %s',
                  new_node.name)
        new_location = serializer.deserialize_entity(ctx, location_obj)
        new_node.create()
        new_location.node_id = new_node.id
        new_location.create()

        return serializer.serialize_entity(ctx, new_node)