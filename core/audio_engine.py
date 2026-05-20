import queue
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf

from core.enums import PlayerState


class AudioEngine:
    """Real-time audio engine."""

    SAMPLERATE = 48000
    BLOCKSIZE = 512
    CHANNELS = 1

    def __init__(self):
        self.mic_device = None
        self.out_device = None
        self.monitor_device = None

        self.running = False

        self.mic_volume = 1.0
        self.sfx_volume = 1.0

        self.mic_muted = False
        self.sidetone = False

        # SFX playback state
        self._sfx_state = PlayerState.STOPPED
        self._sfx_data = None
        self._sfx_pos = 0

        self._sfx_lock = threading.Lock()

        self._stream_in = None
        self._stream_out = None
        self._stream_monitor = None

        self._mic_queue = queue.Queue(maxsize=8)
        self._sfx_monitor_q = queue.Queue(maxsize=64)

    @property
    def sfx_state(self):
        return self._sfx_state

    @staticmethod
    def list_devices():
        devices = sd.query_devices()

        inputs = []
        outputs = []

        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                inputs.append((i, d["name"]))

            if d["max_output_channels"] > 0:
                outputs.append((i, d["name"]))

        return inputs, outputs

    @staticmethod
    def find_vbcable():
        _, outputs = AudioEngine.list_devices()

        for idx, name in outputs:
            if (
                "cable input" in name.lower()
                or "vb-audio" in name.lower()
            ):
                return idx

        return None

    def start(self):
        if self.running:
            return

        if self.mic_device is None or self.out_device is None:
            raise RuntimeError(
                "Select microphone and VB-Cable before starting."
            )

        self.running = True

        self._stream_in = sd.InputStream(
            device=self.mic_device,
            channels=self.CHANNELS,
            samplerate=self.SAMPLERATE,
            blocksize=self.BLOCKSIZE,
            dtype="float32",
            latency="low",
            callback=self._input_cb,
        )

        self._stream_out = sd.OutputStream(
            device=self.out_device,
            channels=self.CHANNELS,
            samplerate=self.SAMPLERATE,
            blocksize=self.BLOCKSIZE,
            dtype="float32",
            latency="low",
            callback=self._output_cb,
        )

        self._stream_in.start()
        self._stream_out.start()

    def stop(self):
        self.running = False

        for attr in (
            "_stream_in",
            "_stream_out",
            "_stream_monitor",
        ):
            stream = getattr(self, attr, None)

            if stream:
                try:
                    stream.stop()
                    stream.close()
                except Exception:
                    pass

            setattr(self, attr, None)

    def _input_cb(self, indata, frames, time, status):
        chunk = indata[:, 0].copy()

        if self.mic_muted:
            chunk[:] = 0.0
        else:
            chunk *= self.mic_volume

        if self._mic_queue.full():
            try:
                self._mic_queue.get_nowait()
            except queue.Empty:
                pass

        try:
            self._mic_queue.put_nowait(chunk)
        except queue.Full:
            pass

    def _output_cb(self, outdata, frames, time, status):
        try:
            mic = self._mic_queue.get_nowait()
        except queue.Empty:
            mic = np.zeros(frames, dtype=np.float32)

        sfx = self._next_sfx_chunk(frames)

        mixed = mic + sfx * self.sfx_volume

        outdata[:, 0] = np.tanh(mixed)

    def _next_sfx_chunk(self, frames):
        with self._sfx_lock:
            if (
                self._sfx_state != PlayerState.PLAYING
                or self._sfx_data is None
            ):
                return np.zeros(frames, dtype=np.float32)

            data = self._sfx_data
            pos = self._sfx_pos
            end = pos + frames

            if end >= len(data):
                chunk = np.pad(
                    data[pos:],
                    (0, frames - (len(data) - pos)),
                )

                self._sfx_state = PlayerState.STOPPED
                self._sfx_pos = 0
            else:
                chunk = data[pos:end].copy()
                self._sfx_pos = end

            return chunk

    def sfx_load_and_play(self, filepath):
        thread = threading.Thread(
            target=self._load_worker,
            args=(filepath,),
            daemon=True,
        )

        thread.start()

    def _load_worker(self, filepath):
        try:
            data, sr = sf.read(
                filepath,
                dtype="float32",
                always_2d=False,
            )
        except Exception as e:
            print(f"[SFX] Read error: {e}")
            return

        if data.ndim == 2:
            data = data.mean(axis=1)

        if sr != self.SAMPLERATE:
            new_len = int(
                len(data) * self.SAMPLERATE / sr
            )

            data = np.interp(
                np.linspace(
                    0,
                    len(data) - 1,
                    new_len,
                ),
                np.arange(len(data)),
                data,
            ).astype(np.float32)

        with self._sfx_lock:
            self._sfx_data = data
            self._sfx_pos = 0
            self._sfx_state = PlayerState.PLAYING

    def sfx_pause(self):
        with self._sfx_lock:
            if self._sfx_state == PlayerState.PLAYING:
                self._sfx_state = PlayerState.PAUSED
            elif self._sfx_state == PlayerState.PAUSED:
                self._sfx_state = PlayerState.PLAYING

    def sfx_stop(self):
        with self._sfx_lock:
            self._sfx_state = PlayerState.STOPPED
            self._sfx_pos = 0
