# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import eventlet
import mock
from oslo.config import cfg

eventlet.monkey_patch()

from mistral.actions import std_actions
from mistral.db.v1 import api as db_api
from mistral import engine
from mistral.engine import executor
from mistral.engine import states
from mistral import exceptions
from mistral.openstack.common import importutils
from mistral.openstack.common import log as logging
from mistral.tests import base


# We need to make sure that all configuration properties are registered.
importutils.import_module("mistral.config")
LOG = logging.getLogger(__name__)

# Use the set_default method to set value otherwise in certain test cases
# the change in value is not permanent.
cfg.CONF.set_default('auth_enable', False, group='pecan')


WORKBOOK_NAME = 'my_workbook'
TASK_NAME = 'create-vms'

SAMPLE_WORKBOOK = {
    'id': str(uuid.uuid4()),
    'name': WORKBOOK_NAME,
    'description': 'my description',
    'definition': base.get_resource("test_rest.yaml"),
    'tags': [],
    'scope': 'public',
    'updated_at': None,
    'project_id': '123',
    'trust_id': '1234'
}

SAMPLE_EXECUTION = {
    'id': str(uuid.uuid4()),
    'workbook_name': WORKBOOK_NAME,
    'task': TASK_NAME,
    'state': states.RUNNING,
    'updated_at': None,
    'context': None
}

SAMPLE_TASK = {
    'name': TASK_NAME,
    'workbook_name': WORKBOOK_NAME,
    'execution_id': 'Will be filled up by SetUp',
    'action_spec': {
        'name': 'my-action',
        'class': 'std.http',
        'base-parameters': {
            'url': 'http://localhost:8989/v1/workbooks',
            'method': 'GET'
        },
        'namespace': 'MyRest'
    },
    'in_context': {},
    'parameters': {},
    'task_spec': {
        'action': 'MyRest.my-action',
        'name': TASK_NAME},
    'requires': [],
    'state': states.IDLE}

SAMPLE_CONTEXT = {
    'user': 'admin',
    'tenant': 'mistral'
}


@mock.patch.object(
    executor.ExecutorClient, 'handle_task',
    mock.MagicMock(side_effect=base.EngineTestCase.mock_handle_task))
class TestExecutor(base.DbTestCase):
    def __init__(self, *args, **kwargs):
        super(TestExecutor, self).__init__(*args, **kwargs)

        self.transport = base.get_fake_transport()

    def setUp(self):
        super(TestExecutor, self).setUp()

        # Create a new workbook.
        self.workbook = db_api.workbook_create(SAMPLE_WORKBOOK)

        # Create a new execution.
        self.execution = db_api.execution_create(
            SAMPLE_EXECUTION['workbook_name'], SAMPLE_EXECUTION)

        self.addCleanup(db_api.execution_delete, SAMPLE_EXECUTION['id'])

        # Create a new task.
        SAMPLE_TASK['execution_id'] = self.execution['id']
        self.task = db_api.task_create(
            SAMPLE_TASK['execution_id'], SAMPLE_TASK)

    def test_setup(self):
        """Validate test setup."""
        self.assertIsNotNone(self.workbook)
        self.assertIsNotNone(self.execution)
        self.assertIsNotNone(self.task)
        self.assertIsNotNone(self.task.id)

    @mock.patch.object(std_actions.EchoAction, 'run')
    @mock.patch.object(engine.EngineClient, 'convey_task_result',
                       mock.MagicMock())
    def test_handle_task(self, action):
        task_id = '12345'
        action_name = 'std.echo'
        params = {
            'output': 'some'
        }

        # Send the task request to the Executor.
        ex_client = executor.ExecutorClient(self.transport)
        ex_client.handle_task(SAMPLE_CONTEXT,
                              task_id=task_id,
                              action_name=action_name,
                              params=params)

        engine.EngineClient.convey_task_result.assert_called_once_with(
            task_id,
            states.SUCCESS,
            action.return_value)

    @mock.patch.object(engine.EngineClient, 'convey_task_result',
                       mock.MagicMock())
    def test_handle_task_not_registered(self):
        task_id = '12345'
        action_name = 'not.registered'
        params = {
            'output': 'some'
        }

        # Send the task request to the Executor.
        ex_client = executor.ExecutorClient(self.transport)
        self.assertRaises(exceptions.ActionException, ex_client.handle_task,
                          SAMPLE_CONTEXT,
                          task_id=task_id,
                          action_name=action_name,
                          params=params)

        self.assertFalse(engine.EngineClient.convey_task_result.called)

    @mock.patch.object(std_actions.EchoAction, 'run',
                       mock.MagicMock(side_effect=exceptions.ActionException))
    @mock.patch.object(engine.EngineClient, 'convey_task_result',
                       mock.MagicMock())
    def test_handle_task_action_exception(self):
        task_id = '12345'
        action_name = 'std.echo'
        params = {
            'output': 'some'
        }

        # Send the task request to the Executor.
        ex_client = executor.ExecutorClient(self.transport)
        with mock.patch('mistral.engine.drivers.default.executor.'
                        'DefaultExecutor._log_action_exception') as log:
            ex_client.handle_task(SAMPLE_CONTEXT,
                                  task_id=task_id,
                                  action_name=action_name,
                                  params=params)
            self.assertTrue(log.called, "Exception must be logged")

        engine.EngineClient.convey_task_result.assert_called_once_with(
            task_id, states.ERROR, None)
