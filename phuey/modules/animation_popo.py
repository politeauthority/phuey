"""Cycle Colors
Sets all selected lights to the same color, cycling all colors via `hue`.
Has the options of delay.

"""
import time


class AnimationPopo(object):

    def __init__(self, Phuey):
        self.phuey = Phuey
        # self.stored_options = ['phuey_animation_cycle_color_delay']
        self.phuey.set_global_delay('phuey_animation_popo_delay')
        self.phuey.set_global_brightness('phuey_animation_popo_brightness')
        self.phuey.print_args()
        self.delta = {
            'sat': 234,
            'transitiontime': 1,
            'bri': self.phuey.brightness
        }
        self.blue = {
            'hue': 45996,

        }
        self.red = {
            'hue': 950
        }

        self.white = {
            'hue': 41435
        }

    def run(self):
        """
        Kick off for the animation.

        """
        self.phuey.capture_initial_state()
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
        # self.delta['transitiontime'] = self.phuey.delay_to_hue_transition_time(self.phuey.delay)
        ani_iter = 0
        cycle_count = 0
        last_light = None
        while True:
            for light_id in self.phuey.selected_lights:
                command = self.delta
                if ani_iter % 2 == 0:
                    command['hue'] = self.red['hue']
                else:
                    command['hue'] = self.blue['hue']
                self.phuey.bridge.set_light(light_id, command)

                self.clear_white()

                ani_iter += 1
                if len(self.phuey.lights) % 2:
                    ani_iter += 1
            time.sleep(self.phuey.delay)
            cycle_count += 1

    def clear_white(self):
        """
        @NOTE: NOT WORKING.
        The idea is every x cycles run a bright white marquee, then return to red blue after.

        """
        if ani_iter % 100 == 0:
            print('Going White!')
            time.sleep(self.phuey.delay)
            command['hue'] = self.white['hue']
            for light_id in self.phuey.selected_lights:
                print('Turning on: %s' % self.phuey.light_digest[light_id])
                self.phuey.bridge.set_light(light_id, command)
                if last_light:
                    print('turning off light: %s' % self.phuey.light_digest[last_light])
                    self.phuey.bridge.set_light(last_light, {'on': False})
                last_light = light_id
            time.sleep(self.phuey.delay)

# End File: phuey/phuey/modules/animation_popo.py
