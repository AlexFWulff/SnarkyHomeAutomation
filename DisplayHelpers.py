import tkinter as tk
import numpy as np
import random
import time

# Display Constants (this is a bad place for this)
n_frames = 20
label_frame_w_pct = 0.55
label_frame_h_pct = 0.2
color_change_step_time = 0.1
transition_step_time = color_change_step_time/4
main_background_color = "#141414"
state_texts = ["Waiting...", "Listening...",
               "Keep talking...", "Transcribing..."]

label_w_pct = 0.9
input_label_h_pct = 0.4
response_label_h_pct = 0.4
action_label_h_pct = 1-input_label_h_pct-response_label_h_pct

def rand_hex():
    r = lambda: random.randint(0,255)
    return "#%02X%02X%02X" % (r(),r(),r())

def make_start_window(root, w, h):
    # Make default window
    label_frame_w = label_frame_w_pct*w
    label_frame_h = label_frame_h_pct*h
    label_frame_x = w/2-label_frame_w/2
    label_frame_y = h/2-label_frame_h/2
    frame_x_vals = np.linspace(0, label_frame_x, n_frames)
    frame_y_vals = np.linspace(0, label_frame_y, n_frames)
    frame_w_vals = np.linspace(label_frame_w, w, n_frames)
    frame_h_vals = np.linspace(label_frame_h, h, n_frames)
    frame_w_vals = np.flip(frame_w_vals)
    frame_h_vals = np.flip(frame_h_vals)
    
    window_frames = []

    for i in range(n_frames-1):
        frame = tk.Frame(root, bg=rand_hex())
        x = np.int(frame_x_vals[i])
        frame.place(x=int(frame_x_vals[i]),y=int(frame_y_vals[i]),
                    width=int(frame_w_vals[i]),
                    height=int(frame_h_vals[i]))
        window_frames.append(frame)

    title_label = tk.Label(root,
                           text = state_texts[0],
                           font=("Arial 35 bold"),
                           bg=main_background_color, fg="white")
    title_label.place(x=int(frame_x_vals[-1]),
                      y=int(frame_y_vals[-1]),
                      width=int(frame_w_vals[-1]),
                      height=int(frame_h_vals[-1]))

    return window_frames,title_label

def do_start_updates(last_update_time, window_frames, state_idx):
    if time.time() - last_update_time < color_change_step_time:
        return False

    last_color = ""
    for i, frame in enumerate(window_frames):
        if i == 0:
            last_color = frame.cget("background")
            frame.config(background = rand_hex())
        else:
            this_color = last_color
            last_color = frame.cget("background")
            frame.config(background = this_color)
    
    return True

def update_label_title(state_idx, title_label):
    current_txt = title_label.cget("text")
    desired_txt = state_texts[state_idx]
    if current_txt != state_texts[state_idx]:
        title_label.config(text = desired_txt)

def transition_to_started(state, window_frames, title_label):
    if len(state) == 0:
        state["last_step_time"] = 0
        state["remaining_steps"] = n_frames
    
    if time.time() - state["last_step_time"] < transition_step_time:
        return state, False

    state["last_step_time"] = time.time()

    last_color = ""
    for i, frame in enumerate(window_frames):
        if i == 0:
            last_color = frame.cget("background")
            frame.config(background = main_background_color)
        else:
            this_color = last_color
            last_color = frame.cget("background")
            frame.config(background = this_color)
    
    state["remaining_steps"] = state["remaining_steps"] - 1

    if state["remaining_steps"] == 0:
        title_label.config(fg = main_background_color)
        return state, True
    else:
        return state, False

def draw_active_screen(root, input_txt, response_txt, action_txt,
                       input_label, response_label, action_label,
                       w, h):

    label_w = label_w_pct*w
    label_x = int(w/2-label_w/2)
    input_h = int(input_label_h_pct*h)
    input_y = 0
    response_h = int(response_label_h_pct*h)
    response_y = input_h
    action_h = int(action_label_h_pct*h)
    action_y = input_h+response_h

    if input_label is None and input_txt != "":
        input_label = tk.Label(
            root,
            text = input_txt,
            font=("Arial 35 bold"),
            wraplength=label_w, justify="center",
            bg=main_background_color, fg="white")
        
        input_label.place(x=label_x,
                          y=input_y,
                          width=label_w,
                          height=input_h)

    if response_label is None and response_txt != "":
        response_label = tk.Label(
            root,
            text = response_txt,
            font=("Arial 35 bold"),
            wraplength=label_w, justify="center",
            bg=main_background_color, fg="#44ABFF")
        response_label.place(x=label_x,
                             y=response_y,
                             width=label_w,
                             height=response_h)

    if action_label is None and action_txt != "":
        action_label = tk.Label(
            root,
            text = action_txt,
            font=("Arial", 30),
            wraplength=label_w, justify="center",
            bg=main_background_color, fg="white")
        action_label.place(x=label_x,
                           y=action_y,
                           width=label_w,
                           height=action_h)
        


    return input_label, response_label, action_label
