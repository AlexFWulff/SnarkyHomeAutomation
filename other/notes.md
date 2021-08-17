# Random Notes
* I couldn't just install `pocketsphinx` on macOS via Pip. Had to follow the instructions linked here: https://github.com/bambocher/pocketsphinx-python/issues/28#issuecomment-597794252 (except my AL version number was different), and then use the pip install command here: https://github.com/bambocher/pocketsphinx-python/issues/28#issuecomment-849265015

# Packages I don't need
* sounddevice
* simpleaudio
* pocketsphinx

# Packages I installed
* pvporcupine
* SpeechRecognition
* openai
* gtts
* audio2numpy
* pyaudio
* simpleaudio

# RPI Setup
First error was ImportError: libportaudio.so.2: cannot open shared object file: No such file or directory
So, I installed libportaudio2 via apt
