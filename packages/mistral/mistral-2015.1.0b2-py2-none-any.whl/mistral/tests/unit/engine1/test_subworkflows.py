# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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

import mock
from oslo.config import cfg

from mistral.actions import std_actions
from mistral import context as auth_context
from mistral.db.v2 import api as db_api
from mistral import exceptions as exc
from mistral.openstack.common import log as logging
from mistral.services import workbooks as wb_service
from mistral.tests.unit.engine1 import base

LOG = logging.getLogger(__name__)

# Use the set_default method to set value otherwise in certain test cases
# the change in value is not permanent.
cfg.CONF.set_default('auth_enable', False, group='pecan')


WORKBOOK = """
---
version: '2.0'

name: my_wb

workflows:
  wf1:
    type: reverse
    input:
      - param1
      - param2
    output:
      final_result: $.final_result

    tasks:
      task1:
        action: std.echo output='{$.param1}'
        publish:
          result1: $.task1

      task2:
        action: std.echo output="'{$.param1} & {$.param2}'"
        publish:
          final_result: $.task2
        requires: [task1]

  wf2:
    type: direct
    output:
      slogan: $.slogan

    tasks:
      task1:
        workflow: wf1 param1='Bonnie' param2='Clyde' task_name='task2'
        publish:
          slogan: "{$.task1.final_result} is a cool movie!"
"""


class SubworkflowsTest(base.EngineTestCase):
    def setUp(self):
        super(SubworkflowsTest, self).setUp()

        wb_service.create_workbook_v2(WORKBOOK)

    def test_subworkflow_success(self):
        exec1_db = self.engine.start_workflow('my_wb.wf2', None)
        project_id = auth_context.ctx().project_id

        # Execution 1.
        self.assertEqual(project_id, exec1_db.project_id)
        self.assertIsNotNone(exec1_db)
        self.assertDictEqual({}, exec1_db.input)
        self.assertDictEqual({}, exec1_db.start_params)

        db_execs = db_api.get_executions()

        self.assertEqual(2, len(db_execs))

        # Execution 2.
        if db_execs[0].id != exec1_db.id:
            exec2_db = db_execs[0]
        else:
            exec2_db = db_execs[1]

        self.assertEqual(project_id, exec2_db.project_id)
        self.assertIsNotNone(exec2_db.parent_task_id)
        self.assertDictEqual(
            {
                'task_name': 'task2',
                'parent_task_id': exec2_db.parent_task_id
            },
            exec2_db.start_params
        )
        self.assertDictEqual(
            {
                'param1': 'Bonnie',
                'param2': 'Clyde'
            },
            exec2_db.input
        )

        # Wait till workflow 'wf1' is completed.
        self._await(lambda: self.is_execution_success(exec2_db.id))

        exec2_db = db_api.get_execution(exec2_db.id)

        self.assertDictEqual(
            {
                'final_result': "'Bonnie & Clyde'"
            },
            exec2_db.output
        )

        # Wait till workflow 'wf2' is completed.
        self._await(lambda: self.is_execution_success(exec1_db.id))

        exec1_db = db_api.get_execution(exec1_db.id)

        self.assertDictEqual(
            {
                'slogan': "'Bonnie & Clyde' is a cool movie!"
            },
            exec1_db.output
        )

        # Check project_id in tasks.
        tasks_exec1 = db_api.get_tasks(execution_id=exec1_db.id)
        tasks_exec2 = db_api.get_tasks(execution_id=exec2_db.id)

        task1_exec1 = self._assert_single_item(tasks_exec1, name="task1")
        task1_exec2 = self._assert_single_item(tasks_exec2, name="task1")
        task2_exec2 = self._assert_single_item(tasks_exec2, name="task2")

        self.assertEqual(project_id, task1_exec1.project_id)
        self.assertEqual(project_id, task1_exec2.project_id)
        self.assertEqual(project_id, task2_exec2.project_id)

    @mock.patch.object(std_actions.EchoAction, 'run',
                       mock.MagicMock(side_effect=exc.ActionException))
    def test_subworkflow_error(self):
        exec1_db = self.engine.start_workflow('my_wb.wf2', None)

        db_execs = db_api.get_executions()

        self.assertEqual(2, len(db_execs))

        if db_execs[0].id != exec1_db.id:
            exec2_db = db_execs[0]
        else:
            exec2_db = db_execs[1]

        # Wait till workflow 'wf1' is completed.
        self._await(lambda: self.is_execution_error(exec2_db.id))

        # Wait till workflow 'wf2' is completed, its state must be ERROR.
        self._await(lambda: self.is_execution_error(exec1_db.id))

    def test_subworkflow_environment_inheritance(self):
        env = {'key1': 'abc'}
        exec1_db = self.engine.start_workflow('my_wb.wf2',
                                              None,
                                              env=env)

        # Execution 1.
        self.assertIsNotNone(exec1_db)
        self.assertDictEqual({}, exec1_db.input)
        self.assertDictEqual({'env': env}, exec1_db.start_params)

        db_execs = db_api.get_executions()

        self.assertEqual(2, len(db_execs))

        # Execution 2.
        if db_execs[0].id != exec1_db.id:
            exec2_db = db_execs[0]
        else:
            exec2_db = db_execs[1]

        expected_start_params = {
            'task_name': 'task2',
            'parent_task_id': exec2_db.parent_task_id,
            'env': env
        }

        self.assertIsNotNone(exec2_db.parent_task_id)
        self.assertDictEqual(exec2_db.start_params, expected_start_params)

        # Wait till workflow 'wf1' is completed.
        self._await(lambda: self.is_execution_success(exec2_db.id))

        # Wait till workflow 'wf2' is completed.
        self._await(lambda: self.is_execution_success(exec1_db.id))
