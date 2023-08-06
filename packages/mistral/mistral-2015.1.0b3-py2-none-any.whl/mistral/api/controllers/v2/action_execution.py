# -*- coding: utf-8 -*-
#
# Copyright 2015 - Mirantis, Inc.
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

import json

from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from mistral.api.controllers import resource
from mistral.db.v2 import api as db_api
# TODO(nmakhotkin) Uncomment these lines after refactoring.
from mistral.engine1 import rpc
from mistral import exceptions as exc
from mistral.openstack.common import log as logging
from mistral.utils import rest_utils
from mistral.workflow import states
from mistral.workflow import utils as wf_utils


LOG = logging.getLogger(__name__)


class ActionExecution(resource.Resource):
    """ActionExecution resource."""

    id = wtypes.text

    workflow_name = wtypes.text
    task_execution_id = wtypes.text

    state = wtypes.text

    state_info = wtypes.text
    tags = [wtypes.text]
    name = wtypes.text
    accepted = bool
    input = wtypes.text
    output = wtypes.text
    created_at = wtypes.text
    updated_at = wtypes.text

    @classmethod
    def from_dict(cls, d):
        e = cls()

        for key, val in d.items():
            if hasattr(e, key):
                # Nonetype check for dictionary must be explicit.
                if val is not None and (
                        key == 'input' or key == 'output'):
                    val = json.dumps(val)
                setattr(e, key, val)

        return e

    @classmethod
    def sample(cls):
        return cls(
            id='123e4567-e89b-12d3-a456-426655440000',
            workflow_name='flow',
            workflow_execution_id='653e4127-e89b-12d3-a456-426655440076',
            task_execution_id='343e45623-e89b-12d3-a456-426655440090',
            state=states.SUCCESS,
            state_info=states.SUCCESS,
            tags=['foo', 'fee'],
            definition_name='std.echo',
            accepted=True,
            input='{"first_name": "John", "last_name": "Doe"}',
            output='{"some_output": "Hello, John Doe!"}',
            created_at='1970-01-01T00:00:00.000000',
            updated_at='1970-01-01T00:00:00.000000'
        )


class ActionExecutions(resource.Resource):
    """A collection of action_executions."""

    action_executions = [ActionExecution]

    @classmethod
    def sample(cls):
        return cls(action_executions=[ActionExecution.sample()])


class ActionExecutionsController(rest.RestController):
    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(ActionExecution, wtypes.text)
    def get(self, id):
        """Return the specified action_execution."""
        LOG.info("Fetch action_execution [id=%s]" % id)

        db_model = db_api.get_action_execution(id)

        return ActionExecution.from_dict(db_model.to_dict())

    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(ActionExecution, wtypes.text, body=ActionExecution)
    def put(self, id, action_execution):
        """Update the specified action_execution."""
        LOG.info(
            "Update action_execution [id=%s, action_execution=%s]"
            % (id, action_execution)
        )

        # Client must provide a valid json. It shouldn't  necessarily be an
        # object but it should be json complaint so strings have to be escaped.
        output = None

        if action_execution.output:
            try:
                output = json.loads(action_execution.output)
            except (ValueError, TypeError) as e:
                raise exc.InvalidResultException(str(e))

        if action_execution.state == states.SUCCESS:
            result = wf_utils.Result(data=output)
        elif action_execution.state == states.ERROR:
            result = wf_utils.Result(error=output)
        else:
            raise exc.InvalidResultException(
                "Error. Expected on of %s, actual: %s" %
                ([states.SUCCESS, states.ERROR], action_execution.state)
            )

        engine = rpc.get_engine_client()
        values = engine.on_action_complete(id, result)

        return ActionExecution.from_dict(values)

    @wsme_pecan.wsexpose(ActionExecutions)
    def get_all(self):
        """Return all action_executions within the execution."""
        LOG.info("Fetch action_executions")

        action_executions = [ActionExecution.from_dict(db_model.to_dict())
                             for db_model in db_api.get_action_executions()]

        return ActionExecutions(action_executions=action_executions)


class TasksActionExecutionController(rest.RestController):
    @wsme_pecan.wsexpose(ActionExecutions, wtypes.text)
    def get_all(self, task_execution_id):
        """Return all action executions within the task execution."""
        LOG.info("Fetch action executions")

        action_execs = db_api.get_action_executions(
            task_execution_id=task_execution_id
        )

        return ActionExecutions(
            action_executions=[ActionExecution.from_dict(db_model.to_dict())
                               for db_model in action_execs]
        )
