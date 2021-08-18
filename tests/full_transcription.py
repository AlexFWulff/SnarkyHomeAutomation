import numpy as np
import pvporcupine
import pyaudio
import speech_recognition as sr
import struct
# Temp
import sounddevice as sd
import simpleaudio as sa

transcription_buffer_time = 0.5
rms_deviation_thresh = 1.5
initial_thresh_time = 0.5

def rms(samps):
    larger = np.array(samps, dtype=np.int64)
    return np.sqrt(np.mean(larger**2))

def run():
    porc = pvporcupine.create(keywords=["computer"])
    pa = pyaudio.PyAudio()
    r = sr.Recognizer()

    # Computed Params
    transcription_nsamp = int(porc.sample_rate*transcription_buffer_time)
    
    audio_stream = pa.open(
        rate=porc.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porc.frame_length)

    # Baseline audio level for a second
    samps = audio_stream.read(porc.frame_length)
    samps = np.frombuffer(samps, dtype=np.int16)
    base_level = rms(samps)
    print(f"Avg Level: {base_level}")
    
    while True:
        samps = audio_stream.read(porc.frame_length)
        pcm = struct.unpack_from("h" * porc.frame_length, samps)
        keyword_index = porc.process(pcm)
        
        if keyword_index >= 0:
            print("Wakeword Detected. Listening...")
            # Continuously read samples until RMS value goes to baseline
            to_transcribe = []
            still_quiet = True
            while True:
                samps = audio_stream.read(transcription_nsamp)
                samps = np.frombuffer(samps, dtype=np.int16)
                if rms(samps) < 1.5*base_level and still_quiet:
                    continue
                elif rms(samps) < 1.5*base_level:
                    break

                if still_quiet:
                    print("You started talking!")
                    still_quiet = False

                to_transcribe.append(samps)

            to_transcribe = np.hstack(to_transcribe)
            
            #sd.play(to_transcribe, porc.sample_rate)
            print("Transcribing...")
            audio = sr.AudioData(to_transcribe, porc.sample_rate, 2)
            try:
                print(r.recognize_sphinx(audio))
            except sr.UnknownValueError:
                print("Sphinx could not understand audio")

            audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()
            break
            
        else:
            # Eventually implement continuous RMS updating here
            # with a list of past RMS values that gets averaged
            pass
        
if __name__=="__main__":
    run()
