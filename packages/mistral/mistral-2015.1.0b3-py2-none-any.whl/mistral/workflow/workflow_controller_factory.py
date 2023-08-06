# -*- coding: utf-8 -*-
#
# Copyright 2014 - Mirantis, Inc.
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

from mistral import exceptions as exc
from mistral.workbook import parser as spec_parser
from mistral.workflow import direct_workflow
from mistral.workflow import reverse_workflow


def create_workflow_controller(wf_ex, wf_spec=None):
    if not wf_spec:
        wf_spec = spec_parser.get_workflow_spec(wf_ex.spec)

    cls = _select_workflow_controller(wf_spec)

    if not cls:
        msg = 'Failed to find a workflow controller [wf_spec=%s]' % wf_spec
        raise exc.WorkflowException(msg)

    return cls(wf_ex)


def _select_workflow_controller(wf_spec):
    # TODO(rakhmerov): This algorithm is actually for DSL v2.
    # TODO(rakhmerov): Take DSL versions into account.
    wf_type = wf_spec.get_type() or 'direct'

    if wf_type == 'reverse':
        return reverse_workflow.ReverseWorkflowController

    if wf_type == 'direct':
        return direct_workflow.DirectWorkflowController

    return None
