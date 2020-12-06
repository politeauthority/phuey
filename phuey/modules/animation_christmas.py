"""Vapor
A vapor wave animation.

"""
from datetime import datetime
import time

# from phuey import Phuey


class AnimationChristmas(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        self.red = {
            'xy': [0.6547, 0.3069],
            'sat': 235,
            'transitiontime': 50,
            'bri': self.phuey.brightness
        }
        self.green = {
            'xy': [0.2128, 0.6992],
            'sat': 235,
            'transitiontime': 50,
            'bri': self.phuey.brightness
        }
        self.vapor_lights = {}

    def run(self):
        """
        Kick off for the animation.

        """
        self.phuey.capture_initial_state()
        self.phuey.reset_lights()
        self.phuey.bridge.set_light(self.phuey.selected_lights, 'on', True)

        print('Press Ctrl+C To exit')
        self.run_init()
        self.run_primary_loop()

    def run_init(self):
        """
        Initial setup, sets every other light to one of the initial colors.

        """
        c = 1
        for light_id in self.phuey.selected_lights:
            if (c % 2) == 0:
                self.vapor_lights[light_id] = 'red'
                self.phuey.bridge.set_light(light_id, self.red)
            else:
                self.vapor_lights[light_id] = 'green'
                self.phuey.bridge.set_light(light_id, self.green)
            c += 1
        time.sleep(3)

    def run_primary_loop(self):
        """
        Cycles lights between the teal and pink colors on the cadence of self.delay

        """
        try:
            while True:
                print('Cycling -\t%s' % datetime.now())
                for light_id in self.phuey.selected_lights:
                    if self.vapor_lights[light_id] == 'red':
                        self.phuey.bridge.set_light(light_id, 'xy', self.green['xy'])
                        self.vapor_lights[light_id] = 'green'
                    else:
                        self.phuey.bridge.set_light(light_id, 'xy', self.red['xy'])
                        self.vapor_lights[light_id] = 'red'
                time.sleep(self.phuey.delay)
        except KeyboardInterrupt:
            self.phuey.handle_exit()

# End File: phuey/phuey/modules/animation_christmas.py
