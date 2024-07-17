# Copyright Modal Labs 2024
import asyncio
import typing
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Set, Tuple

from aiostream import pipe, stream
from grpclib import Status

from modal._utils.async_utils import (
    AsyncOrSyncIteratable,
    queue_batch_iterator,
    synchronize_api,
    synchronizer,
    warn_if_generator_is_not_consumed,
)
from modal._utils.blob_utils import BLOB_MAX_PARALLELISM
from modal._utils.function_utils import (
    ATTEMPT_TIMEOUT_GRACE_PERIOD,
    OUTPUTS_TIMEOUT,
    _create_input,
    _process_result,
)
from modal._utils.grpc_utils import retry_transient_errors
from modal.config import logger
from modal.execution_context import current_input_id
from modal_proto import api_pb2

if typing.TYPE_CHECKING


class _SynchronizedQueue:
    """mdmd:hidden"""

    # small wrapper around asyncio.Queue to make it cross-thread compatible through synchronicity
    async def init(self):
        # in Python 3.8 the asyncio.Queue is bound to the event loop on creation
        # so it needs to be created in a synchronicity-wrapped init method
        self.q = asyncio.Queue()

    @synchronizer.no_io_translation
    async def put(self, item):
        await self.q.put(item)

    @synchronizer.no_io_translation
    async def get(self):
        return await self.q.get()


SynchronizedQueue = synchronize_api(_SynchronizedQueue)


@dataclass
class _OutputValue:
    # box class for distinguishing None results from non-existing/None markers
    value: Any


MAP_INVOCATION_CHUNK_SIZE = 49

if typing.TYPE_CHECKING


@warn_if_generator_is_not_consumed(function_name="Function.map.aio")
async def _map_async(
    self,
    *input_iterators: typing.Union[
        typing.Iterable[Any], typing.AsyncIterable[Any]
    ],  # one input iterator per argument in the mapped-over function/generator
    kwargs={},  # any extra keyword arguments for the function
    order_outputs: bool = True,  # return outputs in order
    return_exceptions: bool = False,  # propagate exceptions (False) or aggregate them in the results list (True)
) -> typing.AsyncGenerator[Any, None]:
    """mdmd:hidden
    This runs in an event loop on the main thread

    It concurrently feeds new input to the input queue and yields available outputs
    to the caller.
    Note that since the iterator(s) can block, it's a bit opaque how often the event
    loop decides to get a new input vs how often it will emit a new output.
    We could make this explicit as an improvement or even let users decide what they
    prefer: throughput (prioritize queueing inputs) or latency (prioritize yielding results)
    """
    raw_input_queue: Any = SynchronizedQueue()  # type: ignore
    raw_input_queue.init()

    async def feed_queue():
        # This runs in a main thread event loop, so it doesn't block the synchronizer loop
        async with stream.zip(*[stream.iterate(it) for it in input_iterators]).stream() as streamer:
            async for args in streamer:
                await raw_input_queue.put.aio((args, kwargs))
        await raw_input_queue.put.aio(None)  # end-of-input sentinel

    feed_input_task = asyncio.create_task(feed_queue())

    try:
        # note that `map()` and `map.aio()` are not synchronicity-wrapped, since
        # they accept executable code in the form of
        # iterators that we don't want to run inside the synchronicity thread.
        # Instead, we delegate to `._map()` with a safer Queue as input
        async for output in self._map.aio(raw_input_queue, order_outputs, return_exceptions):  # type: ignore[reportFunctionMemberAccess]
            yield output
    finally:
        feed_input_task.cancel()  # should only be needed in case of exceptions


@warn_if_generator_is_not_consumed(function_name="Function.starmap")
async def _starmap_async(
    self,
    input_iterator: typing.Union[typing.Iterable[typing.Sequence[Any]], typing.AsyncIterable[typing.Sequence[Any]]],
    kwargs={},
    order_outputs: bool = True,
    return_exceptions: bool = False,
) -> typing.AsyncIterable[Any]:
    raw_input_queue: Any = SynchronizedQueue()  # type: ignore
    raw_input_queue.init()

    async def feed_queue():
        # This runs in a main thread event loop, so it doesn't block the synchronizer loop
        async with stream.iterate(input_iterator).stream() as streamer:
            async for args in streamer:
                await raw_input_queue.put.aio((args, kwargs))
        await raw_input_queue.put.aio(None)  # end-of-input sentinel

    feed_input_task = asyncio.create_task(feed_queue())
    try:
        async for output in self._map.aio(raw_input_queue, order_outputs, return_exceptions):  # type: ignore[reportFunctionMemberAccess]
            yield output
    finally:
        feed_input_task.cancel()  # should only be needed in case of exceptions
