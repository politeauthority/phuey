"""Vapor
A vapor wave animation.

"""
from datetime import datetime
import time

# from phuey import Phuey


class AnimationVapor(object):

    def __init__(self, Phuey):
        self.phuey = Phuey

    def run(self):
        """
        Kick off for the animation.

        """
        self._set_delay()
        self.phuey.capture_initial_state()
        self.phuey.reset_lights()
        self.phuey.bridge.set_light(self.phuey.selected_lights, 'on', True)

        pink = {
            'xy': [0.4176, 0.1868],
            'sat': 241,
            'transitiontime': 50,
            'bri': 254
        }
        teal = {
            'xy': [0.18, 0.4214],
            'sat': 234,
            'transitiontime': 50,
            'bri': 254
        }
        lights = {}

        # Initial Setup
        c = 1
        for light_id in self.phuey.selected_lights:
            if (c % 2) == 0:
                lights[light_id] = 'pink'
                self.phuey.bridge.set_light(light_id, pink)
            else:
                lights[light_id] = 'teal'
                self.phuey.bridge.set_light(light_id, teal)
            c += 1
        time.sleep(3)

        print('Press Ctrl+C To exit')
        try:
            while True:
                print('Cycling -\t%s' % datetime.now())
                for light_id in self.phuey.selected_lights:
                    if lights[light_id] == 'pink':
                        self.phuey.bridge.set_light(light_id, 'xy', teal['xy'])
                        lights[light_id] = 'teal'
                    else:
                        self.phuey.bridge.set_light(light_id, 'xy', pink['xy'])
                        lights[light_id] = 'pink'
                time.sleep(self.delay)

        except KeyboardInterrupt:
            self.phuey.handle_exit()

    def _set_delay(self):
        """
        Sets the delay from CLI args or default.

        """
        if self.phuey.args.delay:
            self.phuey.delay = int(self.phuey.args.delay)
            if self.delay > 2:
                self.delay = 2
        else:
            self.delay = 5

        return True

# End File: phuey/phuey/modules/animation_vapor.py
