"""Vapor
A vapor wave animation.

"""
from datetime import datetime
import time

from phuey import Phuey


class AnimationVapor(Phuey):

    def run(self):
        """
        Kick off for the animation.

        """
        self._set_delay()
        self.capture_initial_state()
        self.reset_lights()
        self.bridge.set_light(self.selected_lights, 'on', True)

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
        for light_id in self.selected_lights:
            if (c % 2) == 0:
                lights[light_id] = 'pink'
                self.bridge.set_light(light_id, pink)
            else:
                lights[light_id] = 'teal'
                self.bridge.set_light(light_id, teal)
            c += 1
        time.sleep(3)

        print('Press Ctrl+C To exit')
        try:
            while True:
                print('Cycling -\t%s' % datetime.now())
                for light_id in self.selected_lights:
                    if lights[light_id] == 'pink':
                        self.bridge.set_light(light_id, 'xy', teal['xy'])
                        lights[light_id] = 'teal'
                    else:
                        self.bridge.set_light(light_id, 'xy', pink['xy'])
                        lights[light_id] = 'pink'
                time.sleep(self.delay)

        except KeyboardInterrupt:
            self.handle_exit()

    def _set_delay(self):
        """
        Sets the delay from CLI args or default.

        """
        if self.args.delay:
            self.delay = int(self.args.delay)
            if self.delay > 2:
                self.delay = 2
        else:
            self.delay = 5

        return True

# End File: phuey/phuey/modules/animation_vapor.py
