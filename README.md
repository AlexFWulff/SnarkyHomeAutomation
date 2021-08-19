# Snarky AI - The Meanest Voice Assistant
[![YouTube banner](https://img.youtube.com/vi/p1eTp-xPUeU/mqdefault.jpg)](https://youtu.be/p1eTp-xPUeU)

https://img.youtube.com/vi/p1eTp-xPUeU/mqdefault.jpg

Create an extremely snarky GPT-3-powered voice assistant to turn on and off your smart home devices. Build instructions are [here](https://www.hackster.io/AlexWulff/the-meanest-home-automation-ai-with-gpt-3-859116).

This code is currently only compatible with LIFX smart bulbs, but it should be a piece of cake to extend this to handle any other smart device that has a Python API.

## Extending this Software
I wrote this voice assistant software in a modular manner, so you can easily extend this package to handle other voice assistant functions. For example, in addition to handling smart lights, you could also give this voice assistant the ability to add items to a to-do list.

This package is broken up into a variety of modules. Check `Run.py` to see a general overview of how data is delivered between modules and the general flow of the program. There are comments throughout describing some of the basic behaviors.
