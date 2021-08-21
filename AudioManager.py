import numpy as np
import pvporcupine
import pyaudio
import speech_recognition as sr
import struct
from threading import Thread
import time
import configparser
from queue import Queue, Empty

class AudioManager:
    l = None
    stop_rec = False
    display_man = None
    
    samps_stale = True
    current_samps = None

    wakeword_detected = False
    
    output_queue = Queue()

    def __init__(self, logger, config_file, display_man, sound_man, wake_man):        
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()
        self.display_man = display_man
        self.sound_man = sound_man

        self.wake_man = wake_man
        self.fs = self.wake_man.fs
        self.refresh_nsamp = int(self.buf_refresh_time*self.fs)
        
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(
            rate=self.fs,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.refresh_nsamp
        )

        # let audio settle then baseline audio level for a bit
        self.audio_stream.read(int(self.fs/2),
                               exception_on_overflow=False)
        baseline_samps = int(self.initial_thresh_time*self.fs)
        samps = self.audio_stream.read(baseline_samps,
                                       exception_on_overflow=False)
        samps = np.frombuffer(samps, dtype=np.int16)
        self.base_level = self.rms(samps)
        self.l.log(f"Base RMS Level: {self.base_level}", "DEBUG")
        
        sample_thread = Thread(target = self.feed_wakeword)
        sample_thread.start()

        # Continuously wait for wakeword in this thread
        run_thread = Thread(target = self.run)
        run_thread.start()
        
    def feed_wakeword(self):
        cur_samps = np.random.normal(0,1000,self.wake_man.nsamp)
        nsamp = self.wake_man.nsamp
        
        while not self.stop_rec:
            if self.wakeword_detected:
                try: self.wake_man.output_queue.get_nowait()
                except Empty: pass
                cur_samps = np.random.normal(0,1000,self.wake_man.nsamp)
                time.sleep(0.1)
                continue

            try:
                self.wake_man.output_queue.get_nowait()
                self.wakeword_detected = True
            except Empty:
                pass
            
            samps = self.audio_stream.read(self.refresh_nsamp,
                                           exception_on_overflow=False)
            samps = np.frombuffer(samps, dtype=np.int16)
            cur_samps[:nsamp-self.refresh_nsamp] = cur_samps[self.refresh_nsamp:]
            cur_samps[nsamp-self.refresh_nsamp:] = samps
            self.wake_man.input_queue.put(np.array(cur_samps))

        self.audio_stream.stop_stream()
        self.audio_stream.close()

    def run(self):
        r = sr.Recognizer()

        wait_speech_nsamp = int(self.fs*self.wait_speech_buffer_time)
        transcription_nsamp = int(self.fs*self.transcription_buffer_time)
        current_nsamp = wait_speech_nsamp
        
        while not self.stop_rec:
            # If the wakeword was detected...
            if self.wakeword_detected:
                self.display_man.wakeword_detected()
                self.l.log("Wakeword Detected. Waiting for speech.", "RUN")
                self.sound_man.play_blocking("wakeword")
                
                # Continuously read samples until RMS value goes to baseline
                to_transcribe = []
                still_quiet = True
                while True:
                    samps = self.audio_stream.read(current_nsamp,
                                              exception_on_overflow=False)
                    samps = np.frombuffer(samps, dtype=np.int16)
                    
                    if self.rms(samps) < self.dev_thresh*self.base_level \
                       and still_quiet:
                        continue
                    elif self.rms(samps) < self.dev_thresh*self.base_level:
                        current_nsamp = wait_speech_nsamp
                        break
    
                    if still_quiet:
                        current_nsamp = transcription_nsamp
                        self.display_man.talking_started()
                        self.l.log("You started talking!", "DEBUG")
                        still_quiet = False
                    
                    to_transcribe.append(samps)
    
                to_transcribe = np.hstack(to_transcribe)

                self.display_man.talking_finished()
                self.l.log("Done talking. Transcribing...", "DEBUG")
                audio = sr.AudioData(to_transcribe, self.fs, 2)
                try:
                    transcription = r.recognize_google(audio)
                    self.l.log(f"You said: {transcription}", "RUN")
                    self.output_queue.put(transcription)
                    self.display_man.transcription_finished(transcription)
                    self.sound_man.play_blocking("transcription success")
                except sr.UnknownValueError:
                    self.l.log("No audio found in segment", "DEBUG")
                    self.display_man.transcription_finished("")
                    self.sound_man.play_blocking("transcription failed")
                
                self.wakeword_detected = False
            else:
                time.sleep(0.01)
                # Eventually implement continuous RMS updating here
                # with a list of past RMS values that gets averaged

    def stop(self):
        self.stop_rec = True
    
    def rms(self, samps):
        # We're using 16-bit integers, so want to cast to 64-bit before rms.
        # This caused me lots of headaches before realizing that the values
        # were overflowing...
        larger = np.array(samps, dtype=np.int64)
        return np.sqrt(np.mean(larger**2))

    def parse_config(self):
        self.transcription_buffer_time = \
            float(self.config["Audio"]["transcription_buffer_time"])
        self.wait_speech_buffer_time = \
            float(self.config["Audio"]["wait_speech_buffer_time"])
        self.dev_thresh = float(self.config["Audio"]["rms_deviation_thresh"])
        self.initial_thresh_time = \
            float(self.config["Audio"]["initial_thresh_time"])
        self.buf_refresh_time = \
            float(self.config["Audio"]["buf_refresh_time"])

