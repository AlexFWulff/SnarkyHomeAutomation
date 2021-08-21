import sys
sys.path.append("..")
from DisplayManager import DisplayManager
from SimpleLogger import SimpleLogger
from AutomationManager import AutomationManager
from WakewordDetector import WakewordDetector
import pyaudio
import time
from threading import Thread
import numpy as np
from queue import Queue, Empty

buffer_add_time = 0.1
cur_samps = None
fresh_samps = False

def get_samps(fs, nsamp):
    global cur_samps, fresh_samps
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=fs,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1000
    )

    samps = audio_stream.read(nsamp, exception_on_overflow=False)
    cur_samps = np.frombuffer(samps, dtype=np.int16)
    fresh_samps = True
    
    incr_samps = int(fs*buffer_add_time)
    while True:
        samps = audio_stream.read(incr_samps, exception_on_overflow=False)
        samps = np.frombuffer(samps, dtype=np.int16)
        samps_copy = np.array(cur_samps)
        samps_copy[:nsamp-incr_samps] = cur_samps[incr_samps:]
        samps_copy[nsamp-incr_samps:] = samps
        cur_samps = samps_copy
        fresh_samps = True

def run():
    global fresh_samps, cur_samps
    l = SimpleLogger("DEBUG")
    if l is None:
        exit()
    
    display = DisplayManager(l, "../config.ini")
    wakeword = WakewordDetector(l, "../config.ini", display)

    samps_thread = Thread(target=get_samps, args=(wakeword.fs, wakeword.nsamp,))
    samps_thread.start()

    print("Running...")
    while True:
        try:
            result = wakeword.output_queue.get(block=False)
            print("Detected!!")
        except Empty:
            pass
            
        if fresh_samps:
            fresh_samps = False
            wakeword.input_queue.put(np.array(cur_samps))
        else:
            time.sleep(0.001)
        
    
if __name__ == "__main__":
    run()

