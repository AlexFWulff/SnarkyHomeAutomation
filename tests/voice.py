from gtts import gTTS
import audio2numpy as a2n
import simpleaudio as sa

text = "Boop beep boop beep bop boop beep"

spoken = gTTS(text=text, lang="en", slow=False)
spoken.save("/tmp/tempvoice.mp3")
x, fs = a2n.audio_from_file("/tmp/tempvoice.mp3")
play_obj = sa.play_buffer(x, 1, 4, fs*2)
play_obj.wait_done()
