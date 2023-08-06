# -*- coding: utf-8 -*-
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

# TODO(rakhmerov): Deprecated in favor of package 'mistral.engine1'.

from mistral import context as auth_context
from mistral import engine
from mistral.engine import executor
from mistral.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class DefaultEngine(engine.Engine):
    def _run_task(self, task_id, action_name, params):
        # TODO(rakhmerov):
        # This call outside of DB transaction creates a window
        # when the engine may crash and DB will not be consistent with
        # the task message queue state. Need to figure out the best
        # solution to recover from this situation.
        # However, making this call in DB transaction is really bad
        # since it makes transaction much longer in time and under load
        # may overload DB with open transactions.
        # TODO(m4dcoder): Use a pool for transport and client

        exctr = executor.ExecutorClient(self.transport)

        LOG.info("Submitted task for execution: '%s'" % task_id)

        exctr.handle_task(auth_context.ctx(),
                          task_id=task_id,
                          action_name=action_name,
                          params=params)
