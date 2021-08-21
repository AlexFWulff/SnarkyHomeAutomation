import configparser
from threading import Thread
from queue import Queue, Empty
import time
import tensorflow as tf
from scipy.signal import spectrogram, get_window
import numpy as np
from PIL import Image

class WakewordDetector:
    model = None
    last_detect_time = 0
    stop_rec = False
    
    def __init__(self, logger, config_file, display_man):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()
        self.display_man = display_man
        self.input_queue = Queue()
        self.output_queue = Queue()

        process_thread = Thread(target = self.process_loop)
        process_thread.start()

    def parse_config(self):
        self.model = tf.keras.models.load_model(self.config["Wakeword"]["model_path"])
        self.cooldown_time = float(self.config["Wakeword"]["cooldown_time"])
        self.fs = int(self.config["Wakeword"]["fs"])
        self.sample_len = float(self.config["Wakeword"]["sample_len"])
        self.nsamp = int(self.sample_len*self.fs)
        self.fft_size = int(np.sqrt(self.nsamp*2))
        input_shape = int(self.config["Wakeword"]["model_input_size"])
        self.input_shape = (input_shape, input_shape)
        self.detect_thresh = float(self.config["Wakeword"]["detect_thresh"])

    def stop(self):
        self.stop_rec = True

    def process_loop(self):
        while not self.stop_rec:
            try:
                to_process = self.input_queue.get(timeout=0.1)
            except Empty:
                continue
            if len(to_process.shape) != 1:
                self.l.log("Samples must be 1D", "RUN")
                continue
            if to_process.size != self.nsamp:
                self.l.log("Invalid sample time", "RUN")
                continue

            f,t,spectro = self.get_spectro(to_process, self.fft_size, 1)
            resized = self.resize_spectro(spectro, self.input_shape)
            resized = (resized-np.min(resized))/(np.max(resized)-np.min(resized))*2-1
            resized = np.expand_dims(resized, axis=2)
            resized = np.expand_dims(resized, axis=0)
            output = self.model.predict(resized)

            if output[0][0] > self.detect_thresh and \
               time.time()-self.last_detect_time > self.cooldown_time:
                self.last_detect_time = time.time()
                self.output_queue.put("Detected")

    def get_spectro(self, data, fft_size, sample_rate):
        # TODO - sample rate might need to be multiplied by two. Idk if the freqs
        # are correct yet
        window = get_window("hamming", fft_size)
        f, t, spectro = spectrogram(data, fs=sample_rate, window=window,
                                    nperseg=fft_size, return_onesided=False,
                                    scaling="density", mode="magnitude", noverlap=0)
        
        # I don't like multiplying by arbitrary numbers,
        # but this seems to work well to produce good results
        spectro = np.log10(spectro)
        np.nan_to_num(spectro, 0)

        spectro = spectro[:int(fft_size/2),:]
    
        return f, t, spectro

    def resize_spectro(self, spectro, shape):
        real_shape = (shape[1],shape[0])
        resized = np.array(Image.fromarray(spectro).resize(real_shape))
        if not resized.shape == shape:
            print("Resize failed")
        
        return resized

            
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
