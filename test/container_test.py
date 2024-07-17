# Copyright Modal Labs 2022

import asyncio
import base64
import dataclasses
import json
import os
import pathlib
import pickle
import pytest
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from unittest import mock
from unittest.mock import MagicMock

from grpclib import Status
from grpclib.exceptions import GRPCError

import modal
from modal import Client, Queue, Volume, is_local
from modal._container_entrypoint import UserException, main
from modal._serialization import (
    deserialize,
    deserialize_data_format,
    serialize,
    serialize_data_format,
)
from modal._utils import async_utils
from modal._utils.blob_utils import MAX_OBJECT_SIZE_BYTES
from modal.app import _App
from modal.exception import InvalidError
from modal.partial_function import enter, method
from modal_proto import api_pb2

from .helpers import deploy_app_externally
from .supports.skip import skip_github_non_linux

EXTRA_TOLERANCE_DELAY = 2.0 if sys.platform == "linux" else 5.0
SLEEP_DELAY = 0.1


def _get_inputs(
    args: Tuple[Tuple, Dict] = ((42,), {}),
    n: int = 1,
    kill_switch=True,
    method_name: Optional[str] = None,
) -> List[api_pb2.FunctionGetInputsResponse]:
    input_pb = api_pb2.FunctionInput(
        args=serialize(args), data_format=api_pb2.DATA_FORMAT_PICKLE, method_name=method_name or ""
    )
    inputs = [
        *(
            api_pb2.FunctionGetInputsItem(input_id=f"in-xyz{i}", function_call_id="fc-123", input=input_pb)
            for i in range(n)
        ),
        *([api_pb2.FunctionGetInputsItem(kill_switch=True)] if kill_switch else []),
    ]
    return [api_pb2.FunctionGetInputsResponse(inputs=[x]) for x in inputs]


def _get_multi_inputs(args: List[Tuple[str, Tuple, Dict]] = []) -> List[api_pb2.FunctionGetInputsResponse]:
    responses = []
    for input_n, (method_name, input_args, input_kwargs) in enumerate(args):
        resp = api_pb2.FunctionGetInputsResponse(
            inputs=[
                api_pb2.FunctionGetInputsItem(
                    input_id=f"in-{input_n:03}",
                    input=api_pb2.FunctionInput(args=serialize((input_args, input_kwargs)), method_name=method_name),
                )
            ]
        )
        responses.append(resp)

    return responses + [api_pb2.FunctionGetInputsResponse(inputs=[api_pb2.FunctionGetInputsItem(kill_switch=True)])]


@dataclasses.dataclass
class ContainerResult:
    client: Client
    items: List[api_pb2.FunctionPutOutputsItem]
    data_chunks: List[api_pb2.DataChunk]
    task_result: api_pb2.GenericResult


def _get_multi_inputs_with_methods(args: List[Tuple[str, Tuple, Dict]] = []) -> List[api_pb2.FunctionGetInputsResponse]:
    responses = []
    for input_n, (method_name, *input_args) in enumerate(args):
        resp = api_pb2.FunctionGetInputsResponse(
            inputs=[
                api_pb2.FunctionGetInputsItem(
                    input_id=f"in-{input_n:03}",
                    input=api_pb2.FunctionInput(args=serialize(input_args), method_name=method_name),
                )
            ]
        )
        responses.append(resp)

    return responses + [api_pb2.FunctionGetInputsResponse(inputs=[api_pb2.FunctionGetInputsItem(kill_switch=True)])]


def _container_args(
    module_name,
    function_name,
    function_type=api_pb2.Function.FUNCTION_TYPE_FUNCTION,
    webhook_type=api_pb2.WEBHOOK_TYPE_UNSPECIFIED,
    definition_type=api_pb2.Function.DEFINITION_TYPE_FILE,
    app_name: str = "",
    is_builder_function: bool = False,
    allow_concurrent_inputs: Optional[int] = None,
    serialized_params: Optional[bytes] = None,
    is_checkpointing_function: bool = False,
    deps: List[str] = ["im-1"],
    volume_mounts: Optional[List[api_pb2.VolumeMount]] = None,
    is_auto_snapshot: bool = False,
    max_inputs: Optional[int] = None,
    is_class: bool = False,
    class_parameter_info=api_pb2.ClassParameterInfo(
        format=api_pb2.ClassParameterInfo.PARAM_SERIALIZATION_FORMAT_UNSPECIFIED, schema=[]
    ),
):
    if webhook_type:
        webhook_config = api_pb2.WebhookConfig(
            type=webhook_type,
            method="GET",
            async_mode=api_pb2.WEBHOOK_ASYNC_MODE_AUTO,
        )
    else:
        webhook_config = None

    function_def = api_pb2.Function(
        module_name=module_name,
        function_name=function_name,
        function_type=function_type,
        volume_mounts=volume_mounts,
        webhook_config=webhook_config,
        definition_type=definition_type,
        app_name=app_name or "",
        is_builder_function=is_builder_function,
        is_auto_snapshot=is_auto_snapshot,
        allow_concurrent_inputs=allow_concurrent_inputs,
        is_checkpointing_function=is_checkpointing_function,
        object_dependencies=[api_pb2.ObjectDependency(object_id=object_id) for object_id in deps],
        max_inputs=max_inputs,
        is_class=is_class,
        class_parameter_info=class_parameter_info,
    )

    return api_pb2.ContainerArguments(
        task_id="ta-123",
        function_id="fu-123",
        app_id="ap-1",
        function_def=function_def,
        serialized_params=serialized_params,
        checkpoint_id=f"ch-{uuid.uuid4()}",
    )


def _flatten_outputs(outputs) -> List[api_pb2.FunctionPutOutputsItem]:
    items: List[api_pb2.FunctionPutOutputsItem] = []
    for req in outputs:
        items += list(req.outputs)
    return items


def _run_container(
    servicer,
    module_name,
    function_name,
    fail_get_inputs=False,
    inputs=None,
    function_type=api_pb2.Function.FUNCTION_TYPE_FUNCTION,
    webhook_type=api_pb2.WEBHOOK_TYPE_UNSPECIFIED,
    definition_type=api_pb2.Function.DEFINITION_TYPE_FILE,
    app_name: str = "",
    is_builder_function: bool = False,
    allow_concurrent_inputs: Optional[int] = None,
    serialized_params: Optional[bytes] = None,
    is_checkpointing_function: bool = False,
    deps: List[str] = ["im-1"],
    volume_mounts: Optional[List[api_pb2.VolumeMount]] = None,
    is_auto_snapshot: bool = False,
    max_inputs: Optional[int] = None,
    is_class: bool = False,
    class_parameter_info=api_pb2.ClassParameterInfo(
        format=api_pb2.ClassParameterInfo.PARAM_SERIALIZATION_FORMAT_UNSPECIFIED, schema=[]
    ),
) -> ContainerResult:
    container_args = _container_args(
        module_name,
        function_name,
        function_type,
        webhook_type,
        definition_type,
        app_name,
        is_builder_function,
        allow_concurrent_inputs,
        serialized_params,
        is_checkpointing_function,
        deps,
        volume_mounts,
        is_auto_snapshot,
        max_inputs,
        is_class=is_class,
        class_parameter_info=class_parameter_info,
    )
    with Client(servicer.container_addr, api_pb2.CLIENT_TYPE_CONTAINER, ("ta-123", "task-secret")) as client:
        if inputs is None:
            servicer.container_inputs = _get_inputs()
        else:
            servicer.container_inputs = inputs
        function_call_id = servicer.container_inputs[0].inputs[0].function_call_id
        servicer.fail_get_inputs = fail_get_inputs

        if module_name in sys.modules:
            # Drop the module from sys.modules since some function code relies on the
            # assumption that that the app is created before the user code is imported.
            # This is really only an issue for tests.
            sys.modules.pop(module_name)

        env = os.environ.copy()
        temp_restore_file_path = tempfile.NamedTemporaryFile()
        if is_checkpointing_function:
            # State file is written to allow for a restore to happen.
            tmp_file_name = temp_restore_file_path.name
            with pathlib.Path(tmp_file_name).open("w") as target:
                json.dump({}, target)
            env["MODAL_RESTORE_STATE_PATH"] = tmp_file_name

            # Override server URL to reproduce restore behavior.
            env["MODAL_SERVER_URL"] = servicer.container_addr

        # reset _App tracking state between runs
        _App._all_apps.clear()

        try:
            with mock.patch.dict(os.environ, env):
                main(container_args, client)
        except UserException:
            # Handle it gracefully
            pass
        finally:
            temp_restore_file_path.close()

        # Flatten outputs
        items = _flatten_outputs(servicer.container_outputs)

        # Get data chunks
        data_chunks: List[api_pb2.DataChunk] = []
        if function_call_id in servicer.fc_data_out:
            try:
                while True:
                    chunk = servicer.fc_data_out[function_call_id].get_nowait()
                    data_chunks.append(chunk)
            except asyncio.QueueEmpty:
                pass

        return ContainerResult(client, items, data_chunks, servicer.task_result)


def _unwrap_scalar(ret: ContainerResult):
    assert len(ret.items) == 1
    assert ret.items[0].result.status == api_pb2.GenericResult.GENERIC_STATUS_SUCCESS
    return deserialize(ret.items[0].result.data, ret.client)


def _unwrap_exception(ret: ContainerResult):
    assert len(ret.items) == 1
    assert ret.items[0].result.status == api_pb2.GenericResult.GENERIC_STATUS_FAILURE
    assert "Traceback" in ret.items[0].result.traceback
    return ret.items[0].result.exception


def _unwrap_generator(ret: ContainerResult) -> Tuple[List[Any], Optional[Exception]]:
    assert len(ret.items) == 1
    item = ret.items[0]
    assert item.result.gen_status == api_pb2.GenericResult.GENERATOR_STATUS_UNSPECIFIED

    values: List[Any] = [deserialize_data_format(chunk.data, chunk.data_format, None) for chunk in ret.data_chunks]

    if item.result.status == api_pb2.GenericResult.GENERIC_STATUS_FAILURE:
        exc = deserialize(item.result.data, ret.client)
        return values, exc
    elif item.result.status == api_pb2.GenericResult.GENERIC_STATUS_SUCCESS:
        assert item.data_format == api_pb2.DATA_FORMAT_GENERATOR_DONE
        done: api_pb2.GeneratorDone = deserialize_data_format(item.result.data, item.data_format, None)
        assert done.items_total == len(values)
        return values, None
    else:
        raise RuntimeError("unknown result type")


def _unwrap_asgi(ret: ContainerResult):
    values, exc = _unwrap_generator(ret)
    assert exc is None, "web endpoint raised exception"
    return values


def _get_web_inputs(path="/", method_name=""):
    scope = {
        "method": "GET",
        "type": "http",
        "path": path,
        "headers": {},
        "query_string": b"arg=space",
        "http_version": "2",
    }
    return _get_inputs(((scope,), {}), method_name=method_name)


# needs to be synchronized so the asyncio.Queue gets used from the same event loop as the servicer
@async_utils.synchronize_api
async def _put_web_body(servicer, body: bytes):
    asgi = {"type": "http.request", "body": body, "more_body": False}
    data = serialize_data_format(asgi, api_pb2.DATA_FORMAT_ASGI)

    q = servicer.fc_data_in.setdefault("fc-123", asyncio.Queue())
    q.put_nowait(api_pb2.DataChunk(data_format=api_pb2.DATA_FORMAT_ASGI, data=data, index=1))


SLEEP_TIME = 0.7


def _unwrap_concurrent_input_outputs(n_inputs: int, n_parallel: int, ret: ContainerResult):
    # Ensure that outputs align with expectation of running concurrent inputs

    # Each group of n_parallel inputs should start together of each other
    # and different groups should start SLEEP_TIME apart.
    assert len(ret.items) == n_inputs
    for i in range(1, len(ret.items)):
        diff = ret.items[i].input_started_at - ret.items[i - 1].input_started_at
        expected_diff = SLEEP_TIME if i % n_parallel == 0 else 0
        assert diff == pytest.approx(expected_diff, abs=0.3)

    outputs = []
    for item in ret.items:
        assert item.output_created_at - item.input_started_at == pytest.approx(SLEEP_TIME, abs=0.3)
        assert item.result.status == api_pb2.GenericResult.GENERIC_STATUS_SUCCESS
        outputs.append(deserialize(item.result.data, ret.client))
    return outputs


def _run_container_process(
    servicer,
    module_name,
    function_name,
    *,
    inputs: List[Tuple[str, Tuple, Dict[str, Any]]],
    allow_concurrent_inputs: Optional[int] = None,
    cls_params: Tuple[Tuple, Dict[str, Any]] = ((), {}),
    print=False,  # for debugging - print directly to stdout/stderr instead of pipeing
    env={},
    is_class=False,
) -> subprocess.Popen:
    container_args = _container_args(
        module_name,
        function_name,
        allow_concurrent_inputs=allow_concurrent_inputs,
        serialized_params=serialize(cls_params),
        is_class=is_class,
    )
    encoded_container_args = base64.b64encode(container_args.SerializeToString())
    servicer.container_inputs = _get_multi_inputs(inputs)
    return subprocess.Popen(
        [sys.executable, "-m", "modal._container_entrypoint", encoded_container_args],
        env={**os.environ, **env},
        stdout=subprocess.PIPE if not print else None,
        stderr=subprocess.PIPE if not print else None,
    )


## modal.experimental functionality ##


class Foo:
    def __init__(self, x):
        self.x = x

    @enter()
    def some_enter(self):
        self.x += "_enter"

    @method()
    def method_a(self, y):
        return self.x + f"_a_{y}"

    @method()
    def method_b(self, y):
        return self.x + f"_b_{y}"
