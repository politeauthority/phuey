"""Cycle Colors
Sets all selected lights to the same color, cycling all colors via `hue`.
Has the options of delay.

"""
import time


class AnimationCycleColors(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        self.delta = {
            'sat': 234,
            'transitiontime': 4,
            'bri': 254
        }

    def run(self):
        """
        Kick off for the animation.

        """
        self.phuey.capture_initial_state()
        self._set_delay()
        self.phuey.bridge.set_light(self.phuey.selected_lights, 'on', True)
        print('Press Ctrl+C To exit')
        self.run_primary_loop()

    def run_primary_loop(self):
        """
        Cycles through the hue range of 0 - 65535, setting all lights to the same color, with
        variable delay available.

        """
        self.phuey.bridge.set_light(self.phuey.selected_lights, 'bri', 0)
        time.sleep(1)
        self.phuey.bridge.set_light(self.phuey.selected_lights, 'bri', 255)
        time.sleep(1)
        hue = 0
        self.delta['transitiontime'] = self.phuey.delay_to_hue_transition_time(self.delay)
        while True:
            if hue >= 65535:
                hue = 0
            command = self.delta
            command['hue'] = hue
            self.phuey.bridge.set_light(self.phuey.selected_lights, command)
            if self.phuey.args.v:
                print('Set hue %s' % hue)
            hue = hue + 100
            time.sleep(self.delay)

    def _set_delay(self):
        """
        Sets the delay from CLI args or default.

        """
        if self.phuey.args.delay:
            self.delay = float(self.phuey.args.delay)
            if self.delay > .01:
                self.delay = .1
        else:
            self.delay = .5

        return True

# End File: phuey/phuey/modules/animation_cycle_colors.py
