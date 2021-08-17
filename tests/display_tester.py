import sys
sys.path.append("..")
from DisplayManager import DisplayManager
from SimpleLogger import SimpleLogger
from time import sleep
from threading import Thread

def run():
    l = SimpleLogger("DEBUG")
    if l is None:
        exit()
    
    display = DisplayManager(l, "../config.ini")
    event_thread = Thread(target=event_loop, args=(display,))
    event_thread.start()
    
    while True:
        display.handle_gui_events()
        sleep(0.01)

def event_loop(display):
    input_text = "Would you pretty please turn off the kitchen light"
    result = {
        "prompt_name": "prompt1",
        "object": "kitchen light",
        "state": 0,
        "quip": "Fine, fatty. I'll do it."
    }
    
    try:
        while True:
            sleep(1)
            display.wakeword_detected()
            sleep(1)
            display.talking_started()
            sleep(1)
            display.talking_finished()
            sleep(1)
            display.transcription_finished(input_text)
            sleep(5)
            display.got_ai_result(result)
            sleep(5)
            display.output_speaking_finished()
            sleep(5)
            
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    run()
