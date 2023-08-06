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

from oslo.config import cfg
from oslo import messaging

from mistral import context as auth_ctx
from mistral.engine1 import base
from mistral.openstack.common import log as logging
from mistral.workflow import utils as wf_utils

LOG = logging.getLogger(__name__)


_TRANSPORT = None

_ENGINE_CLIENT = None
_EXECUTOR_CLIENT = None


def get_transport():
    global _TRANSPORT

    if not _TRANSPORT:
        _TRANSPORT = messaging.get_transport(cfg.CONF)

    return _TRANSPORT


def get_engine_client():
    global _ENGINE_CLIENT

    if not _ENGINE_CLIENT:
        _ENGINE_CLIENT = EngineClient(get_transport())

    return _ENGINE_CLIENT


def get_executor_client():
    global _EXECUTOR_CLIENT

    if not _EXECUTOR_CLIENT:
        _EXECUTOR_CLIENT = ExecutorClient(get_transport())

    return _EXECUTOR_CLIENT


class EngineServer(object):
    """RPC Engine server."""

    def __init__(self, engine):
        self._engine = engine

    def start_workflow(self, rpc_ctx, workflow_name, workflow_input, params):
        """Receives calls over RPC to start workflows on engine.

        :param rpc_ctx: RPC request context.
        :return: Workflow execution.
        """

        LOG.info(
            "Received RPC request 'start_workflow'[rpc_ctx=%s,"
            " workflow_name=%s, workflow_input=%s, params=%s]"
            % (rpc_ctx, workflow_name, workflow_input, params)
        )

        return self._engine.start_workflow(
            workflow_name,
            workflow_input,
            **params
        )

    def on_task_state_change(self, rpc_ctx, state, task_ex_id):
        return self._engine.on_task_state_change(state, task_ex_id)

    def on_action_complete(self, rpc_ctx, action_ex_id, result_data,
                           result_error):
        """Receives RPC calls to communicate action result to engine.

        :param rpc_ctx: RPC request context.
        :param action_ex_id: Action execution id.
        :return: Action execution.
        """

        result = wf_utils.Result(result_data, result_error)

        LOG.info(
            "Received RPC request 'on_action_complete'[rpc_ctx=%s,"
            " action_ex_id=%s, result=%s]" % (rpc_ctx, action_ex_id, result)
        )

        return self._engine.on_action_complete(action_ex_id, result)

    def pause_workflow(self, rpc_ctx, execution_id):
        """Receives calls over RPC to pause workflows on engine.

        :param rpc_ctx: Request context.
        :return: Workflow execution.
        """

        LOG.info(
            "Received RPC request 'pause_workflow'[rpc_ctx=%s,"
            " execution_id=%s]" % (rpc_ctx, execution_id)
        )

        return self._engine.pause_workflow(execution_id)

    def resume_workflow(self, rpc_ctx, execution_id):
        """Receives calls over RPC to resume workflows on engine.

        :param rpc_ctx: RPC request context.
        :return: Workflow execution.
        """

        LOG.info(
            "Received RPC request 'resume_workflow'[rpc_ctx=%s,"
            " execution_id=%s]" % (rpc_ctx, execution_id)
        )

        return self._engine.resume_workflow(execution_id)

    def stop_workflow(self, rpc_ctx, execution_id, state, message=None):
        """Receives calls over RPC to stop workflows on engine.

        Sets execution state to SUCCESS or ERROR. No more tasks will be
        scheduled. Running tasks won't be killed, but their results
        will be ignored.

        :param rpc_ctx: RPC request context.
        :param execution_id: Workflow execution id.
        :param state: State assigned to the workflow. Permitted states are
            SUCCESS or ERROR.
        :param message: Optional information string.

        :return: Workflow execution.
        """

        LOG.info(
            "Received RPC request 'stop_workflow'[rpc_ctx=%s, execution_id=%s,"
            " state=%s, message=%s]" % (rpc_ctx, execution_id, state, message)
        )

        return self._engine.stop_workflow(execution_id, state, message)

    def rollback_workflow(self, rpc_ctx, execution_id):
        """Receives calls over RPC to rollback workflows on engine.

        :param rpc_ctx: RPC request context.
        :return: Workflow execution.
        """

        LOG.info(
            "Received RPC request 'rollback_workflow'[rpc_ctx=%s,"
            " execution_id=%s]" % (rpc_ctx, execution_id)
        )

        return self._engine.resume_workflow(execution_id)


class EngineClient(base.Engine):
    """RPC Engine client."""

    def __init__(self, transport):
        """Constructs an RPC client for engine.

        :param transport: Messaging transport.
        """
        serializer = auth_ctx.RpcContextSerializer(
            auth_ctx.JsonPayloadSerializer())

        self._client = messaging.RPCClient(
            transport,
            messaging.Target(topic=cfg.CONF.engine.topic),
            serializer=serializer
        )

    def start_workflow(self, wf_name, wf_input, **params):
        """Starts workflow sending a request to engine over RPC.

        :return: Workflow execution.
        """
        return self._client.call(
            auth_ctx.ctx(),
            'start_workflow',
            workflow_name=wf_name,
            workflow_input=wf_input or {},
            params=params
        )

    def on_task_state_change(self, state, task_ex_id):
        return self._client.call(
            auth_ctx.ctx(),
            'on_task_state_change',
            state=state,
            task_ex_id=task_ex_id,
        )

    def on_action_complete(self, action_ex_id, result):
        """Conveys action result to Mistral Engine.

        This method should be used by clients of Mistral Engine to update
        state of a action execution once action has executed. One of the
        clients of this method is Mistral REST API server that receives
        action result from the outside action handlers.

        Note: calling this method serves an event notifying Mistral that
        it possibly needs to move the workflow on, i.e. run other workflow
        tasks for which all dependencies are satisfied.

        :return: Task.
        """

        return self._client.call(
            auth_ctx.ctx(),
            'on_action_complete',
            action_ex_id=action_ex_id,
            result_data=result.data,
            result_error=result.error
        )

    def pause_workflow(self, execution_id):
        """Stops the workflow with the given execution id.

        :return: Workflow execution.
        """

        return self._client.call(
            auth_ctx.ctx(),
            'pause_workflow',
            execution_id=execution_id
        )

    def resume_workflow(self, execution_id):
        """Resumes the workflow with the given execution id.

        :return: Workflow execution.
        """

        return self._client.call(
            auth_ctx.ctx(),
            'resume_workflow',
            execution_id=execution_id
        )

    def stop_workflow(self, execution_id, state, message=None):
        """Stops workflow execution with given status.

        Once stopped, the workflow is complete with SUCCESS or ERROR,
        and can not be resumed.

        :param execution_id: Workflow execution id
        :param state: State assigned to the workflow: SUCCESS or ERROR
        :param message: Optional information string

        :return: Workflow execution, model.Execution
        """

        return self._client.call(
            auth_ctx.ctx(),
            'stop_workflow',
            execution_id=execution_id,
            state=state,
            message=message
        )

    def rollback_workflow(self, execution_id):
        """Rolls back the workflow with the given execution id.

        :return: Workflow execution.
        """

        return self._client.call(
            auth_ctx.ctx(),
            'rollback_workflow',
            execution_id=execution_id
        )


class ExecutorServer(object):
    """RPC Executor server."""

    def __init__(self, executor):
        self._executor = executor

    def run_action(self, rpc_ctx, action_ex_id, action_class_str,
                   attributes, params):
        """Receives calls over RPC to run action on executor.

        :param rpc_ctx: RPC request context dictionary.
        """

        LOG.info(
            "Received RPC request 'run_action'[rpc_ctx=%s,"
            " action_ex_id=%s, action_class=%s, attributes=%s, params=%s]"
            % (rpc_ctx, action_ex_id, action_class_str, attributes, params)
        )

        self._executor.run_action(
            action_ex_id,
            action_class_str,
            attributes,
            params
        )


class ExecutorClient(base.Executor):
    """RPC Executor client."""

    def __init__(self, transport):
        """Constructs an RPC client for the Executor.

        :param transport: Messaging transport.
        :type transport: Transport.
        """
        serializer = auth_ctx.RpcContextSerializer(
            auth_ctx.JsonPayloadSerializer()
        )

        self.topic = cfg.CONF.executor.topic
        self._client = messaging.RPCClient(
            transport,
            messaging.Target(),
            serializer=serializer
        )

    def run_action(self, action_ex_id, action_class_str, attributes,
                   action_params, target=None):
        """Sends a request to run action to executor."""

        kwargs = {
            'action_ex_id': action_ex_id,
            'action_class_str': action_class_str,
            'attributes': attributes,
            'params': action_params
        }

        self._client.prepare(topic=self.topic, server=target).cast(
            auth_ctx.ctx(),
            'run_action',
            **kwargs
        )
