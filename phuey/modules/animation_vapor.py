"""Vapor
A vapor wave animation.

"""
from datetime import datetime
import time

# from phuey import Phuey


class AnimationVapor(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        self.pink = {
            'xy': [0.4176, 0.1868],
            'sat': 241,
            'transitiontime': 50,
            'bri': self.phuey.brightness
        }
        self.teal = {
            'xy': [0.18, 0.4214],
            'sat': 234,
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
                self.vapor_lights[light_id] = 'pink'
                self.phuey.bridge.set_light(light_id, self.pink)
            else:
                self.vapor_lights[light_id] = 'teal'
                self.phuey.bridge.set_light(light_id, self.teal)
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
                    if self.vapor_lights[light_id] == 'pink':
                        self.phuey.bridge.set_light(light_id, 'xy', self.teal['xy'])
                        self.vapor_lights[light_id] = 'teal'
                    else:
                        self.phuey.bridge.set_light(light_id, 'xy', self.pink['xy'])
                        self.vapor_lights[light_id] = 'pink'
                time.sleep(self.phuey.delay)
        except KeyboardInterrupt:
            self.phuey.handle_exit()

# End File: phuey/phuey/modules/animation_vapor.py
