import configparser
from threading import Thread
from gtts import gTTS
import audio2numpy as a2n
import simpleaudio as sa
from scipy import signal

class VoiceOutputManager:
    def __init__(self, logger, config_file, display_man):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()
        self.display_man = display_man

    def parse_config(self):
        pass

    def handle_command(self, command):
        async_thread = Thread(target = self.handle_command_async,
                              args=(command,))
        async_thread.start()

    def handle_command_async(self, command):
        text = command["quip"]
        spoken = gTTS(text=text, lang="en", slow=False)
        spoken.save("/tmp/tempvoice.mp3")
        x, fs = a2n.audio_from_file("/tmp/tempvoice.mp3")

        # Unfortunately the speaker on my RPi cannot play at 24kHz,
        # so the entire Scipy package is required to resample down to 16 kHz.
        # You can shrink the total size needed by removing these lines and
        # just playing the original audio if your speaker supports it, and
        # you can remove the scipy dependency.
        desired_fs = 16000
        fs_ratio = desired_fs/fs
        desired_nsamp = int(len(x)*fs_ratio)
        downsampled = signal.resample(x, desired_nsamp)

        play_obj = sa.play_buffer(downsampled, 1, 4, desired_fs)
        play_obj.wait_done()
        self.display_man.output_speaking_finished()
