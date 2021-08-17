import configparser
from threading import Thread

class AutomationManager:
    def __init__(self, logger, config_file, display_man):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()
        self.display_man = display_man

    def parse_config(self):
        pass

    def handle_command(self, command):
        async_thread = Thread(target = self.handle_command_async,
                              args=(command,))
        async_thread.start()

    def handle_command_async(self, command):
        pass
