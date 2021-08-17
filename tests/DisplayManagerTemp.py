from threading import Thread
import tkinter as tk
import configparser

class DisplayManager:
    l = None
    stop_rec = False
    
    def __init__(self, logger, config_file):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()

        sg.theme(self.theme)
        self.start_window()
        
    def start_window(self):
        
        layout = [[sg.Text("Hello from PySimpleGUI")],
                  [sg.Button("OK")]]
        self.window = sg.Window("Demo", layout, size=(self.w,self.h))

    def handle_gui_events(self):
        event, values = self.window.read(timeout = 0)
        
        if event == "OK" or event == sg.WIN_CLOSED:
            self.window.close()

    def parse_config(self):
        self.w = int(self.config["Display"]["w"])
        self.h = int(self.config["Display"]["h"])
        self.theme = self.config["Display"]["theme"]
        
    def wakeword_detected(self):
        pass

    def talking_started(self):
        pass

    def talking_finished(self):
        pass
    
    def transcription_finished(self, text):
        pass

    def output_speaking_started(self):
        pass
    
    def got_ai_result(self, result):
        pass

    def ai_result_failed(self, response):
        pass
