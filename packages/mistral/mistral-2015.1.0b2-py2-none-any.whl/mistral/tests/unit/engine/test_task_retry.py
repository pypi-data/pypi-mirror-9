# -*- coding: utf-8 -*-
#
# Copyright 2014 - StackStorm, Inc.
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
import mock
from oslo.config import cfg

from mistral.actions import std_actions
from mistral.db.v1 import api as db_api
from mistral.db.v1.sqlalchemy import models as m
from mistral import engine
from mistral.engine.drivers.default import engine as concrete_engine
from mistral.engine import states
from mistral import exceptions as exc
from mistral.openstack.common import log as logging
from mistral.tests import base
from mistral.workbook import parser as spec_parser


LOG = logging.getLogger(__name__)

# Use the set_default method to set value otherwise in certain test cases
# the change in value is not permanent.
cfg.CONF.set_default('auth_enable', False, group='pecan')

WB_NAME = "my_workbook"


# TODO(rakhmerov): Find a better home for this method.
def get_mock_workbook(file, name='my_wb'):
    wb = m.Workbook()

    wb.name = name
    wb.definition = base.get_resource(file)

    return wb


def _get_workbook(workbook_name):
    wb = db_api.workbook_get(workbook_name)
    return spec_parser.get_workbook_spec_from_yaml(wb["definition"])


class FailBeforeSuccessMocker(object):
    def __init__(self, fail_count):
        self._max_fail_count = fail_count
        self._call_count = 0

    def mock_partial_failure(self, *args):
        if self._call_count < self._max_fail_count:
            self._call_count += 1
            raise exc.ActionException()

        return "result"


@mock.patch.object(
    engine.EngineClient, 'start_workflow_execution',
    mock.MagicMock(side_effect=base.EngineTestCase.mock_start_workflow))
@mock.patch.object(
    engine.EngineClient, 'convey_task_result',
    mock.MagicMock(side_effect=base.EngineTestCase.mock_task_result))
@mock.patch.object(
    concrete_engine.DefaultEngine, '_run_task',
    mock.MagicMock(side_effect=base.EngineTestCase.mock_run_task))
@mock.patch.object(
    std_actions.HTTPAction, 'run',
    mock.MagicMock(return_value='result'))
class TaskRetryTest(base.EngineTestCase):

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/retry_task.yaml')))
    def test_no_retry(self):
        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         'retry_task', None)
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self.engine.convey_task_result(tasks[0]['id'], states.SUCCESS,
                                       {'output': 'result'})

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        self._assert_single_item(tasks, name='retry_task')
        self._assert_single_item(tasks, task_runtime_context=None)

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/retry_task.yaml')))
    def test_retry_always_error(self):
        workbook = _get_workbook(WB_NAME)

        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         'retry_task', None)
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])
        task_spec = workbook.tasks.get(tasks[0]['name'])
        retry_count, _, __ = task_spec.get_retry_parameters()

        for x in xrange(0, retry_count + 1):
            self.engine.convey_task_result(tasks[0]['id'], states.ERROR,
                                           {'output': 'result'})

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name='retry_task')
        self._assert_single_item(tasks, task_runtime_context={
            'retry_no': retry_count - 1})
        self._assert_single_item(tasks, state=states.ERROR)

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/retry_task.yaml')))
    def test_retry_eventual_success(self):
        workbook = _get_workbook(WB_NAME)

        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         'retry_task', None)
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])
        task_spec = workbook.tasks.get(tasks[0]['name'])
        retry_count, _, __ = task_spec.get_retry_parameters()

        for x in xrange(0, retry_count / 2):
            self.engine.convey_task_result(tasks[0]['id'], states.ERROR,
                                           {'output': 'result'})

        self.engine.convey_task_result(tasks[0]['id'], states.SUCCESS,
                                       {'output': 'result'})

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name='retry_task')
        self._assert_single_item(tasks, task_runtime_context={
            'retry_no': retry_count / 2 - 1})

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/delay_retry_task.yaml')))
    def test_retry_delay(self):
        task_name = 'delay_retry_task'
        workbook = _get_workbook(WB_NAME)

        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         task_name, None)

        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])
        task_spec = workbook.tasks.get(tasks[0]['name'])
        retry_count, _, delay = task_spec.get_retry_parameters()

        for x in xrange(0, retry_count):
            tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                     execution_id=execution['id'])

            self._assert_single_item(tasks, name=task_name)
            self._assert_single_item(tasks, state=states.RUNNING)

            self.engine.convey_task_result(tasks[0]['id'], states.ERROR,
                                           {'output': 'result'})

            tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                     execution_id=execution['id'])

            # TODO(rakhmerov): It's not stable, need to avoid race condition.
            self._assert_single_item(tasks, name=task_name)
            self._assert_single_item(tasks, state=states.DELAYED)

            eventlet.sleep(delay * 2)

        # Convey final result outside the loop.
        self.engine.convey_task_result(tasks[0]['id'], states.ERROR,
                                       {'output': 'result'})

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name=task_name)
        self._assert_single_item(tasks, task_runtime_context={
            'retry_no': retry_count - 1})
        self._assert_single_item(tasks, state=states.ERROR)

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/two_tasks.yaml')))
    def test_from_no_retry_to_retry_task(self):
        task_name_1 = 'no_retry_task'
        task_name_2 = 'delay_retry_task'
        workbook = _get_workbook(WB_NAME)

        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         task_name_1, None)

        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name=task_name_1)

        self.engine.convey_task_result(tasks[0]['id'], states.SUCCESS,
                                       {'output': 'result'})

        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name=task_name_2)

        task_spec = workbook.tasks.get(task_name_2)
        retry_count, _, delay = task_spec.get_retry_parameters()

        for x in xrange(0, retry_count):
            self.engine.convey_task_result(tasks[1]['id'], states.ERROR,
                                           {'output': 'result'})

            tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                     execution_id=execution['id'])

            # TODO(rakhmerov): It's not stable, need to avoid race condition.
            self._assert_single_item(tasks, name=task_name_1)
            self._assert_single_item(tasks, state=states.DELAYED)

            eventlet.sleep(delay * 2)

        # Convey final result outside the loop.
        self.engine.convey_task_result(tasks[1]['id'], states.ERROR,
                                       {'output': 'result'})

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name=task_name_2)
        self._assert_single_item(tasks, task_runtime_context={
            'retry_no': retry_count - 1})
        self._assert_single_item(tasks, state=states.ERROR)

    @mock.patch.object(std_actions.EchoAction, "run",
                       mock.MagicMock(side_effect=exc.ActionException))
    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/sync_task.yaml')))
    def test_sync_action_always_error(self):
        workbook = _get_workbook(WB_NAME)
        start_task = 'sync-task'
        task_spec = workbook.tasks.get(start_task)
        retry_count, _, __ = task_spec.get_retry_parameters()

        execution = self.engine.start_workflow_execution(WB_NAME,
                                                         start_task, None)

        # TODO(rakhmerov): It's not stable, need to avoid race condition.
        tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                 execution_id=execution['id'])

        self._assert_single_item(tasks, name=start_task)
        self._assert_single_item(tasks, task_runtime_context={
            'retry_no': retry_count - 1})
        self._assert_single_item(tasks, state=states.ERROR)

    @mock.patch.object(
        db_api, 'workbook_get',
        mock.MagicMock(return_value=get_mock_workbook(
            'retry_task/sync_task.yaml')))
    def test_sync_action_eventual_success(self):
        start_task = 'sync-task'
        workbook = _get_workbook(WB_NAME)
        task_spec = workbook.tasks.get(start_task)
        retry_count, _, __ = task_spec.get_retry_parameters()

        # After a pre-set no of retries the mock method will return a
        # success to simulate this test-case.
        mock_functor = FailBeforeSuccessMocker(retry_count / 2 + 1)

        with mock.patch.object(std_actions.EchoAction, "run",
                               side_effect=mock_functor.mock_partial_failure):
            execution = self.engine.start_workflow_execution(WB_NAME,
                                                             start_task,
                                                             None)

            # TODO(rakhmerov): It's not stable, need to avoid race condition.
            tasks = db_api.tasks_get(workbook_name=WB_NAME,
                                     execution_id=execution['id'])

            self._assert_single_item(tasks, name=start_task)
            self._assert_single_item(tasks, task_runtime_context={
                'retry_no': retry_count / 2})
            self._assert_single_item(tasks, state=states.SUCCESS)
