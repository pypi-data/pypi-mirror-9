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


class RetrySpec(base.BaseSpec):
    # See http://json-schema.org
    _schema = {
        "type": "object",
        "properties": {
            "count": {"type": "integer"},
            "break-on": {"type": "string"},
            "delay": {"type": "integer"}
        },
        "required": ["count", "delay"],
        "additionalProperties": False
    }

    def __init__(self, data):
        super(RetrySpec, self).__init__(data)

        self._break_on = data.get('break-on')
        self._count = data['count']
        self._delay = data['delay']

    def get_count(self):
        return self._count

    def get_break_on(self):
        return self._break_on

    def get_delay(self):
        return self._delay
