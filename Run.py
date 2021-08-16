from SimpleLogger import SimpleLogger
from AudioManager import AudioManager
from DisplayManager import DisplayManager
from AIManager import AIManager

import time

if __name__ == "__main__":
    config = "config.ini"
    
    l = SimpleLogger("DEBUG")
    if l is None:
        exit()

    display_man = DisplayManager(l)
    audio_man = AudioManager(l, config, display_man)
    ai_man = AIManager(l, config, display_man)
    
    try:
        while True:
            if not audio_man.output_queue.empty():
                transcription = audio_man.output_queue.get()
                ai_man.handle_command(transcription)
            if not ai_man.result_outputs.empty():
                print(ai_man.result_outputs.get())
            else:
                time.sleep(0.01)
                
    except KeyboardInterrupt:
        audio_man.stop()
