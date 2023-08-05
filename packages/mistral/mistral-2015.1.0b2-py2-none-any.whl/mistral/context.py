# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import eventlet
from keystoneclient.v3 import client as keystone_client
from oslo.config import cfg
from oslo import messaging
from pecan import hooks

from mistral import exceptions as exc
from mistral.openstack.common import jsonutils
from mistral.openstack.common import log as logging
from mistral import utils

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

_CTX_THREAD_LOCAL_NAME = "MISTRAL_APP_CTX_THREAD_LOCAL"


class BaseContext(object):
    """Container for context variables."""

    _elements = set()

    def __init__(self, __mapping=None, **kwargs):
        if __mapping is None:
            self.__values = dict(**kwargs)
        else:
            if isinstance(__mapping, BaseContext):
                __mapping = __mapping.__values
            self.__values = dict(__mapping)
            self.__values.update(**kwargs)

        bad_keys = set(self.__values) - self._elements

        if bad_keys:
            raise TypeError("Only %s keys are supported. %s given" %
                            (tuple(self._elements), tuple(bad_keys)))

    def __getattr__(self, name):
        try:
            return self.__values[name]
        except KeyError:
            if name in self._elements:
                return None
            else:
                raise AttributeError(name)

    def to_dict(self):
        return self.__values


class MistralContext(BaseContext):
    # Use set([...]) since set literals are not supported in Python 2.6.
    _elements = set([
        "user_id",
        "project_id",
        "auth_token",
        "service_catalog",
        "user_name",
        "project_name",
        "roles",
        "is_admin",
    ])

    def __repr__(self):
        return "MistralContext %s" % self.to_dict()


def has_ctx():
    return utils.has_thread_local(_CTX_THREAD_LOCAL_NAME)


def ctx():
    if not has_ctx():
        raise exc.ApplicationContextNotFoundException()

    return utils.get_thread_local(_CTX_THREAD_LOCAL_NAME)


def set_ctx(new_ctx):
    utils.set_thread_local(_CTX_THREAD_LOCAL_NAME, new_ctx)


def _wrapper(context, thread_desc, thread_group, func, *args, **kwargs):
    try:
        set_ctx(context)
        func(*args, **kwargs)
    except Exception as e:
        LOG.exception("Thread '%s' fails with exception: '%s'"
                      % (thread_desc, e))
        if thread_group and not thread_group.exc:
            thread_group.exc = e
            thread_group.failed_thread = thread_desc
    finally:
        if thread_group:
            thread_group._on_thread_exit()

        set_ctx(None)


def spawn(thread_description, func, *args, **kwargs):
    eventlet.spawn(_wrapper, ctx().clone(), thread_description,
                   None, func, *args, **kwargs)


def context_from_headers(headers):
    return MistralContext(
        user_id=headers.get('X-User-Id'),
        project_id=headers.get('X-Project-Id'),
        auth_token=headers.get('X-Auth-Token'),
        service_catalog=headers.get('X-Service-Catalog'),
        user_name=headers.get('X-User-Name'),
        project_name=headers.get('X-Project-Name'),
        roles=headers.get('X-Roles', "").split(",")
    )


def context_from_config():
    keystone = keystone_client.Client(
        username=CONF.keystone_authtoken.admin_user,
        password=CONF.keystone_authtoken.admin_password,
        tenant_name=CONF.keystone_authtoken.admin_tenant_name,
        auth_url=CONF.keystone_authtoken.auth_uri
    )

    keystone.authenticate()

    return MistralContext(
        user_id=keystone.user_id,
        project_id=keystone.project_id,
        auth_token=keystone.auth_token,
        project_name=CONF.keystone_authtoken.admin_tenant_name,
        user_name=CONF.keystone_authtoken.admin_user
    )


class JsonPayloadSerializer(messaging.NoOpSerializer):
    @staticmethod
    def serialize_entity(context, entity):
        return jsonutils.to_primitive(entity, convert_instances=True)


class RpcContextSerializer(messaging.Serializer):

    def __init__(self, base=None):
        self._base = base or messaging.NoOpSerializer()

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity

        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity

        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context.to_dict()

    def deserialize_context(self, context):
        ctx = MistralContext(**context)
        set_ctx(ctx)

        return ctx


class ContextHook(hooks.PecanHook):
    def before(self, state):
        set_ctx(context_from_headers(state.request.headers))

    def after(self, state):
        set_ctx(None)
