"""Cycle Colors
Sets all selected lights to the same color, cycling all colors via `hue`.
Has the options of delay.

"""
import time


class AnimationBreathe(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        self.stored_options = ['phuey_animation_breathe_delay']
        self.delta = {
            'sat': 234,
            'transitiontime': 4,
            # 'bri': self.phuey.brightness,
            # 'hue': 0,
            # 'on': True,
        }

    def run(self):
        """
        Kick off for the animation.

        """
        self.phuey.capture_initial_state()
        self.phuey.reset_lights()
        # self.phuey.bridge.set_light(self.phuey.selected_lights, 'on', True)
        print('Press Ctrl+C To exit')
        self.run_primary_loop()

    def run_primary_loop(self):
        """
        Cycles through the hue range of 0 - 65535, setting all lights to the same color, with
        variable delay available.

        """
        dim = {}
        dim['transitiontime'] = 50
        dim['bri'] = 0
        dim['on'] = False
        dim['hue'] = 0
        inhale = {}
        inhale['transitiontime'] = 100
        inhale['hue'] = 0
        inhale['bri'] = self.phuey.brightness
        inhale['on'] = True

        # self.phuey.bridge.set_light(self.phuey.selected_lights, {'bri': 0})
        c = 0
        print(len(self.phuey.selected_lights))
        print(self.phuey.selected_lights)
        while True:

            for light_id in self.phuey.selected_lights:
                if c % 2:
                    self.phuey.bridge.set_light(light_id, inhale)
                    print("breathe\t%s\t%s" % (c, self.phuey.light_digest[light_id]))
                else:
                    print("dim\t%s\t%s" % (c, self.phuey.light_digest[light_id]))
                    self.phuey.bridge.set_light(light_id, dim)
                print('\n')
                c += 1
            print('\n\n\n\nNEW CYCLE\n\n\n\n')
            # c += 1
            time.sleep(10)


# End File: phuey/phuey/modules/animation_breathe.py
