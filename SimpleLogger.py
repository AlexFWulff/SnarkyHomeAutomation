# Levels
levels = ["DEBUG", "RUN"]

class SimpleLogger:
    _level = ""
    
    def __init__(self, level):
        if level not in levels:
            print("ERROR: Unknown Logger Level")
            return None
        else:
            self._level = level

    def log(self, message, level):
        if level not in levels:
            print(f"ERROR for msg {message}: Unknown Logger Level")
            return

        if levels.index(level) >= levels.index(self._level):
            print(f"{level}: {message}")
