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

from mistral.workbook import base
from mistral.workbook.v1 import tasks


class WorkflowSpec(base.BaseSpec):
    # See http://json-schema.org
    _schema = {
        "type": "object",
        "properties": {
            "tasks": {"type": "object"},
        },
        "required": ["tasks"],
        "additionalProperties": False
    }

    def __init__(self, workflow):
        super(WorkflowSpec, self).__init__(workflow)

        self.tasks = tasks.TaskSpecList(workflow['tasks'])
