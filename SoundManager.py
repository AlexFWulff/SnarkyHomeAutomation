import configparser
from threading import Thread
import audio2numpy as a2n
import simpleaudio as sa
import time

class SoundManager:
    def __init__(self, logger, config_file):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()

    def parse_config(self):
        pass

    def play_blocking(self, event):
        if event == "wakeword":
            self.play_file_blocking("sounds/beep-hightone.aif")
            time.sleep(0.2)
        elif event == "transcription success":
            self.play_file_blocking("sounds/beep-hightone.aif")
        elif event == "transcription failed":
            self.play_file_blocking("sounds/beep-horn.aif")
        elif event == "ai failed":
            self.play_file_blocking("sounds/beep-horn.aif")
        else:
            self.l.log(f"Unknown sound event {event}", "RUN")
    
    def play_file_blocking(self, filename):
        x, fs = a2n.audio_from_file(filename)
        play_obj = sa.play_buffer(x, 1, 4, fs)
        play_obj.wait_done()
