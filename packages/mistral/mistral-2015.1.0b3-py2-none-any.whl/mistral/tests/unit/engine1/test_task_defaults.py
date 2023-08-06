# Copyright 2014 - Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import datetime as dt
from oslo.config import cfg
import testtools

from mistral.db.v2 import api as db_api
from mistral.engine import states
from mistral.openstack.common import log as logging
from mistral.services import scheduler
from mistral.services import workflows as wf_service
from mistral.tests.unit.engine1 import base


LOG = logging.getLogger(__name__)
# Use the set_default method to set value otherwise in certain test cases
# the change in value is not permanent.
cfg.CONF.set_default('auth_enable', False, group='pecan')

DIRECT_WF_ON_ERROR = """
---
version: '2.0'

wf:
  type: direct

  task-defaults:
    on-error:
      - task3

  tasks:
    task1:
      description: That should lead to transition to task3.
      action: std.http url="http://some_url"
      on-success:
        - task2

    task2:
      action: std.echo output="Morpheus"

    task3:
      action: std.echo output="output"
"""


class TaskDefaultsDirectWorkflowEngineTest(base.EngineTestCase):
    def test_task_defaults_on_error(self):
        wf_service.create_workflows(DIRECT_WF_ON_ERROR)

        # Start workflow.
        wf_ex = self.engine.start_workflow('wf', {})

        self._await(lambda: self.is_execution_success(wf_ex.id))

        # Note: We need to reread execution to access related tasks.
        wf_ex = db_api.get_workflow_execution(wf_ex.id)

        tasks = wf_ex.task_executions

        task1 = self._assert_single_item(tasks, name='task1')
        task3 = self._assert_single_item(tasks, name='task3')

        self.assertEqual(2, len(tasks))
        self.assertEqual(states.ERROR, task1.state)
        self.assertEqual(states.SUCCESS, task3.state)


REVERSE_WF_RETRY = """
---
version: '2.0'

wf:
  type: reverse

  task-defaults:
    policies:
      retry:
        count: 2
        delay: 1

  tasks:
    task1:
      action: std.fail

    task2:
      action: std.echo output=2
      requires: [task1]
"""


REVERSE_WF_TIMEOUT = """
---
version: '2.0'

wf:
  type: reverse

  task-defaults:
    policies:
      timeout: 1

  tasks:
    task1:
      action: std.async_noop

    task2:
      action: std.echo output=2
      requires: [task1]
"""

REVERSE_WF_WAIT = """
---
version: '2.0'

wf:
  type: reverse

  task-defaults:
    policies:
      wait-before: 1
      wait-after: 1

  tasks:
    task1:
      action: std.echo output=1
"""


class TaskDefaultsReverseWorkflowEngineTest(base.EngineTestCase):
    def setUp(self):
        super(TaskDefaultsReverseWorkflowEngineTest, self).setUp()

        thread_group = scheduler.setup()

        self.addCleanup(thread_group.stop)

    @testtools.skip("Fix 'retry' policy.")
    def test_task_defaults_retry_policy(self):
        wf_service.create_workflows(REVERSE_WF_RETRY)

        # Start workflow.
        wf_ex = self.engine.start_workflow('wf', {}, task_name='task2')

        self._await(lambda: self.is_execution_error(wf_ex.id))

        # Note: We need to reread execution to access related tasks.
        wf_ex = db_api.get_workflow_execution(wf_ex.id)

        tasks = wf_ex.task_executions

        self.assertEqual(1, len(tasks))

        task1 = self._assert_single_item(
            tasks,
            name='task1',
            state=states.ERROR
        )

        self.assertTrue(
            task1.runtime_context['retry_task_policy']['retry_no'] > 0
        )

    @testtools.skip("Fix 'timeout' policy.")
    def test_task_defaults_timeout_policy(self):
        wf_service.create_workflows(REVERSE_WF_TIMEOUT)

        # Start workflow.
        wf_ex = self.engine.start_workflow('wf', {}, task_name='task2')

        self._await(lambda: self.is_execution_error(wf_ex.id))

        # Note: We need to reread execution to access related tasks.
        wf_ex = db_api.get_workflow_execution(wf_ex.id)

        tasks = wf_ex.task_executions

        self.assertEqual(1, len(tasks))

        self._assert_single_item(tasks, name='task1', state=states.ERROR)

    @testtools.skip("Fix 'wait' policies.")
    def test_task_defaults_wait_policies(self):
        wf_service.create_workflows(REVERSE_WF_WAIT)

        time_before = dt.datetime.now()

        # Start workflow.
        wf_ex = self.engine.start_workflow('wf', {}, task_name='task1')

        self._await(lambda: self.is_execution_success(wf_ex.id))

        # Workflow must work at least 2 seconds (1+1).
        self.assertGreater(
            (dt.datetime.now() - time_before).total_seconds(),
            2
        )

        # Note: We need to reread execution to access related tasks.
        wf_ex = db_api.get_workflow_execution(wf_ex.id)

        tasks = wf_ex.task_executions

        self.assertEqual(1, len(tasks))

        self._assert_single_item(tasks, name='task1', state=states.SUCCESS)
