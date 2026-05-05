import collections

from juturna.components import Message
from juturna.payloads import Batch
from juturna.components._buffer import Buffer


class SynchroniserStrategy:
    def has_data(self, buf: Buffer): ...
    def get_data(self) -> Message[Batch] | None: ...


class PassthroughSynchroniser(SynchroniserStrategy):
    def has_data(self, buf: Buffer):
        return any(map(lambda d: len(d), buf._data))

    def get_data(
        self, data: dict[str, collections.deque[Message]]
    ) -> Message[Batch]:
        for source in data:
            if len(data[source]):
                return Message[Batch](
                    creator=source,
                    payload=Batch(messages=(data[source.popleft()])),
                )

        return None


_SYNCHRONISERS: dict[str, collections.abc.Callable | None] = {
    'passthrough': PassthroughSynchroniser,
    'local': None,
}
