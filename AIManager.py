import configparser
from os import path
import openai
import re
from queue import Queue
from threading import Thread

class AIManager:
    l = None
    def __init__(self, logger, config_file, display_man, sound_man):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()
        self.display_man = display_man
        self.sound_man = sound_man
        self.result_outputs = Queue()

    # This is called from the main thread, so we want to pass it off
    # to a separate thread to not hang the program
    def handle_command(self, text):
        async_thread = Thread(target = self.handle_command_async,
                              args=(text,))
        async_thread.start()

    def handle_command_async(self, text):
        prompt = self.prompt_text

        # Could add separate handlers for different prompts if desired...
        if self.prompt_name == "prompt1":
            prompt = prompt+text+"\n"+"Object:"

        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.resp_len,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=[self.stop_token]
        )

        result = {}
        if self.prompt_name == "prompt1":
            result = self.parse_prompt1_response(response)

        if result is None:
            self.sound_man.play_blocking("ai failed")
        else:
            self.display_man.got_ai_result(result)
            self.result_outputs.put(result)
            self.l.log(f"Response: {result}", "DEBUG")

    def parse_prompt1_response(self, response):
        # There's lots of weird stuff that GPT-3 could return, so
        # we'll try and filter out as many of these errors as possible
        # before attempting to parse the command
        try:
            reason = response["choices"][0]["finish_reason"]
            text = response["choices"][0]["text"]
            if reason != "stop":
                self.l.log(f"Response didn't stop: {response}", "RUN")
                raise ValueError
            elif "State" not in text or "Response" not in text:
                self.l.log(f"Bad response text: {response}", "RUN")
                raise ValueError

            # Sometimes this can help it if it's slightly wrong
            if text[-1] != "\n": text = text+"\n"
            
            # Response looks halfway decent; let's parse
            result = {}
            result["prompt_name"] = self.prompt_name
            result["object"] = self.between_strings(" ", "\n", text).lower()
            result["state"] = \
                self.between_strings("\nDesired State: ", "\n", text).lower()
            result["quip"] = \
                self.between_strings("\nResponse: ", "\n", text)
            return result
                
        except KeyError:
            self.l.log(f"KeyError in Response",
                       "DEBUG")
        except AttributeError:
            self.l.log(f"AttributeError in Response",
                       "DEBUG")
        except ValueError:
            self.l.log(f"ValueError in Response",
                       "DEBUG")

        self.l.log(f"Error parsing response: {response}",
                   "RUN")
        self.display_man.ai_result_failed(response)
        return None
            
    def parse_config(self):
        prompt_file = self.config["AI"]["prompt_file_path"]
        f = open(prompt_file, "r")
        prompt = f.read()
        # Emacs adds a newline on save
        if prompt[-1] == "\n": prompt = prompt[:-1]
        self.prompt_text = prompt

        # From test/val1.txt grabs val1
        prompt_name = path.split(prompt_file)[-1].split(".")[0]
        self.temperature = float(self.config[prompt_name]["temperature"])
        self.resp_len = int(self.config[prompt_name]["response_length"])
        self.stop_token = self.config[prompt_name]["stop_token"]
        self.prompt_name = prompt_name

        # You'll get an error here if the key file doesn't exist
        f = open(self.config["AI"]["key_path"], "r")
        key_text = f.read()
        if key_text[-1] == "\n": key_text = key_text[:-1]
        openai.api_key = key_text

    # Get text between two strings
    def between_strings(self, start, end, text):
        search_re = start+"(.*)"+end
        return re.search(search_re, text).group(1)
        
