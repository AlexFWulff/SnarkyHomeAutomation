import simpleaudio as sa
import pyaudio

fs = 16000
samp_time = 3

pa = pyaudio.PyAudio()

audio_stream = pa.open(
    rate=fs,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=1000
)


while True:
    print("Recording...")
    samps = audio_stream.read(fs*samp_time, exception_on_overflow=False)
    print("Playing...")
    play_obj = sa.play_buffer(samps, 1, 2, fs)
    # Wait for playback to finish before exiting
    play_obj.wait_done()
