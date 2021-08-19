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

    # Manages the display. All modules call various event functions to
    # make different things happen on the display
    display_man = DisplayManager(l, config_file)
    # Plays various beeps and boops in response to events
    sound_man = SoundManager(l, config_file)
    # Waits for a wakeword, collects the user's voice, and transcribes it
    audio_man = AudioManager(l, config_file, display_man, sound_man)
    # Passes transcribed audio to GPT-3, and parses the response
    ai_man = AIManager(l, config_file, display_man, sound_man)
    # Handles home automation tasks request by AIManager
    auto_man = AutomationManager(l, config_file, display_man)
    # Speaks the output from GPT-3
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
                # The display needs to update on the main thread, so this
                # handle_gui_events function needs to be called frequently
                # to make animations look good.
                if config["Display"]["use_display"] == "True":
                    display_man.handle_gui_events()
                time.sleep(0.01)
                
    except KeyboardInterrupt:
        # AudioManager is the only module with a separate loop that needs
        # to stop in order to have a clean exit
        audio_man.stop()
