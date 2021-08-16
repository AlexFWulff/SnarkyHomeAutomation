import speech_recognition as sr
import soundfile as sf
import simpleaudio as sa

AUDIO_FILE = "/Users/alex/Downloads/audiosample.wav"

data, fs = sf.read(AUDIO_FILE, dtype='int16')
data = data[:,0]
data = data.copy(order='C')

play_obj = sa.play_buffer(data, 1, 2, fs)
# Wait for playback to finish before exiting
play_obj.wait_done()

audio = sr.AudioData(data, fs, 2)
r = sr.Recognizer()
# recognize speech using Sphinx
try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
