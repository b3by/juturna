"""
AudioDataset

@author: Antonio Bevilacqua
@email: abevilacqua@meetecho.com
@created_at: 2026-04-10 10:53:56

This node is to be intended as test node. It will read the entire dataset in
memory at the warmup.
"""

import pathlib
import typing

import numpy as np

from pydub import AudioSegment

from juturna.components import Node
from juturna.components import Message

from juturna.payloads import AudioPayload
from juturna.payloads import ControlSignal
from juturna.payloads import ControlPayload


class AudioDataset(Node[AudioPayload, AudioPayload]):
    """Node implementation class"""

    def __init__(
        self,
        source_dir: str,
        source_formats: list,
        chunk_size: int,
        out_channels: int,
        out_rate: int,
        interval: float,
        **kwargs,
    ):
        """
        Parameters
        ----------
        source_dir : str
            Source directory of audio files.
        source_formats : list
            Extensions of audio files.
        chunk_size : int
            Length of audio chunks, in seconds. If -1, files will be passed as
            single messages.
        out_channels : int
            Number of channels of the output audio.
        out_rate : int
            Sampling rate of the output audio.
        interval : float
            Interval time between each chunk is transmitted.
        kwargs : dict
            Supernode arguments.

        """
        super().__init__(**kwargs)

        self._source_dir = pathlib.Path(source_dir)
        self._source_formats = source_formats
        self._chunk_size = chunk_size
        self._out_channels = out_channels
        self._rate = out_rate
        self._interval = interval

        self._target_files = list()
        self._audio_chunks = dict()
        self._transmitted = 0

    def configure(self):
        """Configure the node"""
        ...

    def warmup(self):
        """Warmup the node"""
        for ext in self._source_formats:
            self._target_files += list(self._source_dir.glob(f'*.{ext}'))

        _chunk_size_ms = self._chunk_size * 1000

        for _audio_file in self._target_files:
            self.logger.info(f'reading {_audio_file}')
            chunks, _ = self._get_audio_chunks(_audio_file, _chunk_size_ms)

            self._audio_chunks[str(_audio_file)] = chunks

        self.set_source(self._fetch_chunks, by=self._interval, mode='pre')

    def set_on_config(self, prop: str, value: typing.Any):
        """Hot-swap node properties"""
        ...

    def start(self):
        """Start the node"""
        # after custom start code, invoke base node start
        super().start()

    def stop(self):
        """Stop the node"""
        # after custom stop code, invoke base node stop
        super().stop()

    def destroy(self):
        """Destroy the node"""
        ...

    def update(self, message: Message[AudioPayload]):
        """Receive data from upstream, transmit data downstream"""
        self.logger.info(
            f'chunk message ready to be sent: {len(message.payload.audio)}'
        )
        self.logger.info(message.meta)

        self.transmit(message)
        self._transmitted += 1

    def _fetch_chunks(self) -> Message[AudioPayload]:
        _remaining = list(self._audio_chunks.keys())

        if len(_remaining) == 0:
            self.logger.info('sending done, stopping source')

            return Message(
                creator=self.name,
                payload=ControlPayload(ControlSignal.STOP_PROPAGATE),
            )

        _k = _remaining[0]
        _m = Message[AudioPayload](
            creator=self.name,
            version=self._transmitted,
            payload=AudioPayload(
                audio=self._audio_chunks[_k][0],
                sampling_rate=self._rate,
                channels=self._out_channels,
                start=self._chunk_size * self._transmitted,
                end=self._chunk_size * self._transmitted + self._chunk_size,
            ),
        )

        _m.meta['source_file'] = _k
        _m.meta['origin'] = _k
        _m.meta['size'] = self._chunk_size

        del self._audio_chunks[_k][0]

        if len(self._audio_chunks[_k]) == 0:
            del self._audio_chunks[_k]

        return _m

    def _get_audio_chunks(self, file_path: str, chunk_length_ms: int):
        audio = (
            AudioSegment.from_file(file_path)
            .set_frame_rate(self._rate)
            .set_channels(self._out_channels)
            .set_sample_width(2)
        )
        chunks = list()

        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i : i + chunk_length_ms]
            data = np.frombuffer(chunk.raw_data, dtype=np.int16)

            if data.size > 0:
                chunks.append(data.astype(np.float32) / 32768.0)

        return chunks, audio.frame_rate

    # uncomment next_batch to design custom synchronisation policy
    # def next_batch(sources: dict[str, list[Message]]) -> dict[str, list[int]]:
    #     ...
