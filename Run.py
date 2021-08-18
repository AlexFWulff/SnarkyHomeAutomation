from SimpleLogger import SimpleLogger
from AudioManager import AudioManager
from DisplayManager import DisplayManager
from AIManager import AIManager
from AutomationManager import AutomationManager
from VoiceOutputManager import VoiceOutputManager
from SoundManager import SoundManager

import configparser

import time

if __name__ == "__main__":
    config_file = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    
    l = SimpleLogger("DEBUG")
    if l is None:
        exit()

    display_man = DisplayManager(l, config_file)
    sound_man = SoundManager(l, config_file)
    audio_man = AudioManager(l, config_file, display_man, sound_man)
    ai_man = AIManager(l, config_file, display_man, sound_man)
    auto_man = AutomationManager(l, config_file, display_man)
    voice_man = VoiceOutputManager(l, config_file, display_man)
    
    try:
        while True:
            if not audio_man.output_queue.empty():
                transcription = audio_man.output_queue.get()
                ai_man.handle_command(transcription)
            if not ai_man.result_outputs.empty():
                command = ai_man.result_outputs.get()
                auto_man.handle_command(command)
                voice_man.handle_command(command)
            else:
                if config["Display"]["use_display"] == "True":
                    display_man.handle_gui_events()
                time.sleep(0.01)
                
    except KeyboardInterrupt:
        audio_man.stop()
