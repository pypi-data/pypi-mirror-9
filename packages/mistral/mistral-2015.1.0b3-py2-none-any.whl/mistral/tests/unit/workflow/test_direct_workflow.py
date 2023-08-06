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

from mistral.db.v2.sqlalchemy import models
from mistral.openstack.common import log as logging
from mistral.tests import base
from mistral.workbook import parser as spec_parser
from mistral.workflow import direct_workflow as d_wf
from mistral.workflow import states

LOG = logging.getLogger(__name__)

WB = """
---
version: '2.0'

name: my_wb

workflows:
  wf:
    type: direct

    tasks:
      task1:
        action: std.echo output="Hey"
        publish:
          res1: <% $.task1 %>
        on-complete:
          - task2: <% $.res1 = 'Hey' %>
          - task3: <% $.res1 = 'Not Hey' %>

      task2:
        action: std.echo output="Hi"

      task3:
        action: std.echo output="Hoy"
"""


class DirectWorkflowControllerTest(base.BaseTest):
    def setUp(self):
        super(DirectWorkflowControllerTest, self).setUp()

        wb_spec = spec_parser.get_workbook_spec_from_yaml(WB)

        wf_ex = models.WorkflowExecution()
        wf_ex.update({
            'id': '1-2-3-4',
            'spec': wb_spec.get_workflows().get('wf').to_dict(),
            'state': states.RUNNING
        })

        self.wf_ex = wf_ex
        self.wb_spec = wb_spec
        self.wf_ctrl = d_wf.DirectWorkflowController(wf_ex)

    def _create_task_execution(self, name, state):
        tasks_spec = self.wb_spec.get_workflows()['wf'].get_tasks()

        task_ex = models.TaskExecution(
            name=name,
            spec=tasks_spec[name].to_dict(),
            state=state
        )

        self.wf_ex.task_executions.append(task_ex)

        return task_ex

    def test_continue_workflow(self):
        # Workflow execution is in initial step. No running tasks.
        cmds = self.wf_ctrl.continue_workflow()

        self.assertEqual(1, len(cmds))

        cmd = cmds[0]

        self.assertIs(self.wf_ctrl.wf_ex, cmd.wf_ex)
        self.assertIsNotNone(cmd.task_spec)
        self.assertEqual('task1', cmd.task_spec.get_name())
        self.assertEqual(states.RUNNING, self.wf_ex.state)

        # Assume that 'task1' completed successfully.
        task1_ex = self._create_task_execution('task1', states.SUCCESS)
        task1_ex.published = {'res1': 'Hey'}

        task1_ex.executions.append(
            models.ActionExecution(
                name='std.echo',
                workflow_name='wf',
                state=states.SUCCESS,
                output={'result': 'Hey'},
                accepted=True
            )
        )

        cmds = self.wf_ctrl.continue_workflow()

        task1_ex.processed = True

        self.assertEqual(1, len(cmds))
        self.assertEqual('task2', cmds[0].task_spec.get_name())

        self.assertEqual(states.RUNNING, self.wf_ex.state)
        self.assertEqual(states.SUCCESS, task1_ex.state)

        # Now assume that 'task2' completed successfully.
        task2_ex = self._create_task_execution('task2', states.SUCCESS)
        task2_ex.executions.append(
            models.ActionExecution(
                name='std.echo',
                workflow_name='wf',
                state=states.SUCCESS,
                output={'result': 'Hi'},
                accepted=True
            )
        )

        cmds = self.wf_ctrl.continue_workflow()

        task2_ex.processed = True

        self.assertEqual(0, len(cmds))
