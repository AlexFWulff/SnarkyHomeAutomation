import configparser
from threading import Thread
import xmltodict
from lifxlan import LifxLAN
import textdistance

class AutomationManager:
    def __init__(self, logger, config_file, display_man):
        self.l = logger
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.parse_config()        
        self.display_man = display_man

        if self.enable_lifx:
            self.lifx = LifxLAN()
            self.lifx_devices = self.lifx.get_lights()

            # Make sure every device in the XML file has a LIFX
            # device that matches it
            for device in self.device_setup["devices"]["device"]:
                if device["type"] != "LIFX": continue
                found_match = False
                for lifx_dev in self.lifx_devices:
                    if device["MAC"] == lifx_dev.mac_addr: found_match = True
                if not found_match:
                    dev_name = device["MAC"]
                    self.l.log(f"Couldn't find MAC match for {dev_name}",
                               "DEBUG")        

    def parse_config(self):
        setup_filename = self.config["Automation"]["setup_filename"]
        info_xml = open(setup_filename, "r").read()
        self.device_setup = xmltodict.parse(info_xml)        
        self.enable_lifx = self.config["Automation"]["enable_lifx"]=="True"
        self.imperfect_matching = \
            self.config["Automation"]["allow_imperfect_matching"]=="True"

    def handle_command(self, command):
        async_thread = Thread(target = self.handle_command_async,
                              args=(command,))
        async_thread.start()

    def handle_command_async(self, command):
        similarities = {}
        
        for device in self.device_setup["devices"]["device"]:
            # perfect match?
            dev_name = device["name"]
            if device["name"] == command["object"]:
                self.find_handler(device, command)
                return
            else:
                # Maybe some text algorithms geek can tell me a better
                # text similarity algorithm to use here?
                simi = textdistance.jaro_winkler(dev_name, command["object"])
                similarities[dev_name] = simi

        # We can only get here if we didn't find a perfect name match
        if self.imperfect_matching:
            closest_dev_name = max(similarities, key=similarities.get)
            for device in self.device_setup["devices"]["device"]:
                if device["name"] == closest_dev_name:
                    self.find_handler(device, command)
                    return
            # Should never get here
            assert False
        else:
            object = command["object"]
            self.l.log(f"No suitable device found for object {object}",
                       "RUN")

    def find_handler(self, device, command):
        if device["type"] == "LIFX":
            self.handle_lifx(device, command)
        else:
            self.l.log(f"No Handler found for {dev_name}",
                       "RUN")
        return
        
    def handle_lifx(self, device, command):
        if not self.enable_lifx:
            self.l.log(f"LIFX not enabled but LIFX device requested",
                       "DEBUG")
            return

        dev_name = device["name"]
        
        for device in self.device_setup["devices"]["device"]:
            if device["type"] != "LIFX": continue

            for lifx_dev in self.lifx_devices:
                if device["MAC"] == lifx_dev.mac_addr:
                    if command["state"] == "0":
                        lifx_dev.set_power("off")
                    elif command["state"] == "1":
                        lifx_dev.set_power("on")
                    else:
                        self.l.log(f"Invalid state for LIFX {dev_name}",
                                   "DEBUG")
                    return

        self.l.log(f"Should have found match for {dev_name}, but didn't!",
                   "RUN")
        
