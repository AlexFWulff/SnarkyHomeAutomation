from threading import Thread
import tkinter as tk
import configparser
import DisplayHelpers
import time

class DisplayManager:
    l = None
    stop_rec = False
    states = ["waiting", "waiting for talking", "talking started",
              "talking finished", "transit to started", "started",
              "got response", "finished talking"]
    last_start_update_time = 0
    transition_state = {}
    input_label = None
    response_label = None
    action_label = None
    
    def __init__(self, logger, config_file):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()

        self.start_window()
        
    def start_window(self):
        self.root = tk.Tk()
        self.root.title("A simple GUI")
        self.root.minsize(width=self.w, height=self.h)

        self.start_window_frames, self.title_label =\
            DisplayHelpers.make_start_window(self.root,
                                             self.w, self.h)

        self.state = self.states[0]

    def handle_gui_events(self):
        state_idx = self.states.index(self.state)
        if self.state == self.states[0] or \
           self.state == self.states[1] or \
           self.state == self.states[2] or \
           self.state == self.states[3]:
            r = DisplayHelpers.do_start_updates(
                self.last_start_update_time,
                self.start_window_frames,
                state_idx
            )
            if r: self.last_start_update_time = time.time()
            DisplayHelpers.update_label_title(state_idx,
                                              self.title_label)
                
        elif self.state == self.states[4]:
            ret_state, finished = \
                DisplayHelpers.transition_to_started(
                    self.transition_state,
                    self.start_window_frames,
                    self.title_label
                )

            self.transition_state = ret_state
            if finished: self.state = self.states[5]

        elif self.state == self.states[5] or \
             self.state == self.states[6]:
            
            in_lab,res_lab,ac_lab = DisplayHelpers.draw_active_screen(
                self.root,
                self.input_txt,
                self.response_txt,
                self.action_txt,
                self.input_label,
                self.response_label,
                self.action_label,
                self.w,
                self.h
            )
            self.input_label = in_lab
            self.response_label = res_lab
            self.action_label = ac_lab

        if self.state == self.states[7]:
            self.input_label.place_forget()
            self.input_label = None
            self.response_label.place_forget()
            self.response_label = None
            self.action_label.place_forget()
            self.action_label = None
            
            self.title_label.config(fg = "white")
            self.state = self.states[0]
        
        self.root.update_idletasks()
        self.root.update()

    def parse_config(self):
        self.w = int(self.config["Display"]["w"])
        self.h = int(self.config["Display"]["h"])
        self.theme = self.config["Display"]["theme"]
        
    def wakeword_detected(self):
        if self.state != self.states[0]:
            self.l.log("Invalid state transition for wakeword",
                       "DEBUG")
            return
        self.state = self.states[1]

    def talking_started(self):
        if self.state != self.states[1]:
            self.l.log("Invalid state transition for start talking",
                       "DEBUG")
            return
        self.state = self.states[2]

    def talking_finished(self):
        if self.state != self.states[2]:
            self.l.log(
                "Invalid state transition for talking finished",
                "DEBUG")
            return
        self.state = self.states[3]
    
    def transcription_finished(self, text):
        if self.state != self.states[3]:
            self.l.log("Invalid state transition for finished",
                       "DEBUG")
            return
        
        self.transition_state = {}
        self.state = self.states[4]
        self.input_txt = text
        self.response_txt = ""
        self.action_txt = ""
    
    def got_ai_result(self, result):
        self.state = self.states[6]
        self.response_txt = result["quip"]
        self.action_txt = "Bla example"

    def output_speaking_finished(self):
        if self.state != self.states[6]:
            self.l.log("Invalid state transition for speaking done",
                       "DEBUG")
            return
        self.state = self.states[7]

        
    def ai_result_failed(self, response):
        pass
