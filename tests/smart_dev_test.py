import sys
sys.path.append("..")
from DisplayManager import DisplayManager
from SimpleLogger import SimpleLogger
from AutomationManager import AutomationManager
import time

def run():
    l = SimpleLogger("DEBUG")
    if l is None:
        exit()
    
    display = DisplayManager(l, "../config.ini")
    auto_man = AutomationManager(l, "../config.ini", display)
    
    command1 = {
        "prompt_name": "prompt1",
        "object": "bedroom lamp",
        "state": "0",
        "quip": "Fine, fatty. I'll do it."
    }
    command2 = {
        "prompt_name": "prompt1",
        "object": "bedroom lamp",
        "state": "1",
        "quip": "Fine, fatty. I'll do it."
    }
    command3 = {
        "prompt_name": "prompt1",
        "object": "kitchen light",
        "state": "0",
        "quip": "Fine, fatty. I'll do it."
    }
    command4 = {
        "prompt_name": "prompt1",
        "object": "kitchen light",
        "state": "1",
        "quip": "Fine, fatty. I'll do it."
    }
    
    auto_man.handle_command(command1)
    time.sleep(1)
    auto_man.handle_command(command2)
    time.sleep(1)
    auto_man.handle_command(command3)
    time.sleep(1)
    auto_man.handle_command(command4)

if __name__ == "__main__":
    run()

