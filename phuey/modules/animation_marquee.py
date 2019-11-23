"""Marquee

"""
import time
import random

import redis

class AnimationMarquee(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        self.stored_options = ['phuey_animation_marquee_delay']
        self.phuey.set_global_delay('phuey_animation_marquee_delay')
        self.phuey.set_global_brightness('phuey_animation_marquee_brightness')
        self.phuey.print_args()
        self.delta = {
            'sat': 234,
            'transitiontime': 1,
            'bri': self.phuey.brightness,
            'on': True,
        }
        self.hues = [
            0,      # red
            45925,  # blueish purple
            48199,  # light blue
            43470,  # orange
            23748,  # bright green
            55760,  # yellow
            55686,  # pinkish
            ]
        self.hue_history = []

    def run(self):
        """
        Kick off for the animation.

        """
        self.phuey.capture_initial_state()
        self.phuey.bridge.set_light(self.phuey.selected_lights, {'on': False})
        # self.phuey.bridge.set_light(self.phuey.selected_lights, 'on', True)
        print('Press Ctrl+C To exit')
        self.run_primary_loop()

    def run_primary_loop(self):
        """
        Cycles through the hue range of 0 - 65535, setting all lights to the same color, with
        variable delay available.

        """
        # self.phuey.selected_lights
        # self.phuey.bridge.set_light(self.phuey.selected_lights, 'bri', 0)
        # time.sleep(1)
        # self.phuey.bridge.set_light(self.phuey.selected_lights, 'bri', 255)
        # time.sleep(1)
        hue = 0
        # self.delta['transitiontime'] = self.phuey.delay_to_hue_transition_time(self.delay)
        print(self.phuey.selected_lights)
        print('delay: %s' % self.phuey.delay)
        last_light = None
        command = self.delta
        command['hue'] = self.hues[0]

        cycle = 0
        while True:
            self.hue_history.append(command['hue'])
            for light_id in self.phuey.selected_lights:
                print('Turning on: %s' % self.phuey.light_digest[light_id])
                self.phuey.bridge.set_light(light_id, command)
                if last_light:
                    print('turning off light: %s' % self.phuey.light_digest[last_light])
                    self.phuey.bridge.set_light(last_light, {'on': False})
                print('\n')
                time.sleep(self.phuey.delay)
                last_light = light_id
                # off_lights = self.phuey.selected_lights
            print('\ncycle complete')
            cycle += 1
            hue_val = self._set_new_color(command['hue'], cycle)
            command['hue'] = hue_val
            print('set new hue: %s\n' % hue_val)

    def _set_new_color(self, current_hue, count):
        """
        """
        if count > len(self.hues):
            count = 0
        rand_hue = self.hues[random.randrange(0, len(self.hues))]

        if len(self.hue_history) > 20:
            print('Purging some history items')
            self.hue_history.pop(0)
            self.hue_history.pop(1)
            self.hue_history.pop(2)
            self.hue_history.pop(3)
            self.hue_history.pop(4)
            self.hue_history.pop(5)
            self.hue_history.pop(6)
            self.hue_history.pop(7)
            self.hue_history.pop(8)
            self.hue_history.pop(9)
            self.hue_history.pop(10)

        last_two_histories = self.hue_history[2:]

        # if rand_hue in last_two_histories:
        #     return self._set_new_color(current_hue, count)


        return rand_hue

# End File: phuey/phuey/modules/animation_marquee.py
