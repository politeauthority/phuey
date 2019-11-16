#!/usr/bin/env python
"""
"""

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import random
import sys
import time

import redis
from phue import Bridge

from .modules.animation_vapor import AnimationVapor
from .modules.animation_cycle_colors import AnimationCycleColors
from .modules.animation_marquee import AnimationMarquee
from .modules.animation_breathe import AnimationBreathe

__version__ = '0.0.1'


class Phuey(object):

    def __init__(self, animation=None):
        self.args = self._parse_args()
        self.redis = redis.Redis()
        self.config = self._load_config()
        self.bridge = Bridge(self.config['bridge_ip'])
        self.selected_lights = self.config['light_ids']
        self.lights = self.bridge.get_light_objects('id')       # All lights in the Hue network
        self.brightness = self._set_global_brightness()
        self.delay = self._set_global_delay()
        self.initial_state = {}

        self.list_lights()

    def connect(self):
        """
        Connects to the hue bridge.

        """
        self.bridge.connect()

    def _print_selected_lights(self):
        """
        Prints all living room lights id and name

        """
        for light_id, light in self.lights.items():
            if light.light_id in self.selected_lights:
                print("%s\t%s" % (light_id, light.name))

    def reset_lights(self):
        """
        Sets all living room lights off, then turns red

        """
        command = {
            'hue': 0,
            'sat': 0,
            'bri': 0,
            'transitiontime': 0,
            'on': False

        }
        self.bridge.set_light(self.selected_lights, command)

    def run(self):
        """
        Main run of script

        """
        self._print_welcome()

        if self.args.pattern == 'cycle-color':
            print('Running:\t Cycle Colors')
            AnimationCycleColors(self).run()

        elif self.args.pattern == 'marquee':
            print('Running:\t Marquee')
            AnimationMarquee(self).run()

        elif self.args.pattern == 'vapor':
            print('Running:\tplay_vapor')
            AnimationVapor(self).run()

        elif self.args.pattern == 'breathe':
            print('Running:\t Breathe')
            AnimationBreathe(self).run()


        elif self.args.pattern == 'list-lights':
            print('Running:\tlist_lights')
            self.cli_list_lights()

        elif self.args.pattern == 'h':
            print('vapor')
            print('mark')
            print('mark-color')
            print('mark-random\t marquee random color')
            print('vapor\t\t beta vapor wave')
            print('h\t\t help')

        else:
            print("No playbook for: %s" % self.args.pattern)
            exit(1)

    def play_random_color_play(self):
        """
        Grabs random colors and sets all light to that color, then changes.

        """
        living_room = [11, 12, 22, 23]

        self.bridge.set_light(living_room, 'bri', 0)
        time.sleep(2)
        self.bridge.set_light(living_room, 'bri', 255)
        time.sleep(2)
        while True:
            for light_id in living_room:
                rand_x = random.random()
                rand_y = random.random()
                self.bridge.set_light(
                    living_room,
                    'xy',
                    [
                        rand_x,
                        rand_y],
                    transitiontime=100)
            print('%s\t%s' % (rand_x, rand_y))
            time.sleep(1)

    def play_marquee_around_the_room_random_color(self):
        """
        Cycles through lights IN ORDER to turn on one in at a random color
        :: CLI TRIGGER: mark-random

        """
        self._reset_lights()
        self.bridge.set_light(self.living_room, 'on', True)

        colors = [0, 10000, 20000, 30000, 40000, 50000]
        count = 0
        active_light = self.living_room[count]

        while True:
            # print('cycle %s' % count)
            the_color = colors[random.randint(0, len(colors) - 1)]
            for light_id in self.living_room:
                if light_id == active_light:
                    print("%s\t%s" % (light_id, self.lights[light_id].name))
                    self.bridge.set_light(light_id, 'on', True)
                    self.bridge.set_light(
                        light_id,
                        'hue',
                        the_color,
                        transitiontime=100)
                    self.bridge.set_light(light_id, 'bri', 255)
                else:
                    self.bridge.set_light(light_id, 'on', False)

            count += 1
            if count > len(self.living_room) - 1:
                count = 0

            active_light = self.living_room[count]
            time.sleep(.5)

    def play_marquee_around_the_room(self):
        """
        Cycles through lights in order with one color until cycle is complete, then changes color
        :: CLI TRIGGER: mark

        """
        self._reset_lights()
        self.bridge.set_light(self.living_room, 'on', True)

        colors = [0, 10000, 20000, 30000, 40000, 50000]
        count = 0
        color_count = 0
        active_light = self.living_room[count]

        while True:
            # print('cycle %s' % count)
            # the_color = colors[random.randint(0, len(colors) - 1)]
            for light_id in self.living_room:
                cmd = {
                    'on': True,
                    'hue': colors[color_count],
                    'bri': 254,
                    'transitiontime': 100
                }
                if light_id == active_light:
                    print("%s\t%s\t%s" % (
                        light_id,
                        self.lights[light_id].name,
                        colors[color_count]))
                    self.bridge.set_light(light_id, cmd)

                else:
                    self.bridge.set_light(light_id, 'on', False)

            count += 1
            if count > len(self.living_room) - 1:
                count = 0

                # Change color after all lights have run the color
                color_count += 1
                if color_count > len(colors) - 1:
                    color_count = 0

            active_light = self.living_room[count]
            time.sleep(2)

    def play_breath(self):
        """
        Cycles through lights IN ORDER to turn on one in at a random color
        :: CLI TRIGGER: breath

        """
        self._reset_lights()
        self.bridge.set_light(self.living_room, 'on', True)

        print('color set')
        self.bridge.set_light(self.living_room, 'hue', 50000)
        while True:
            self.bridge.set_light(self.living_room, 'on', True)
            self.bridge.set_light(self.living_room, 'bri', 254, transitiontime=1000)
            print('bright set')
            time.sleep(5)
            self.bridge.set_light(self.living_room, 'bri', 0, transitiontime=100)
            self.bridge.set_light(self.living_room, 'on', False)
            print('dim set\n')
            time.sleep(3)

    def play_set_color(self):
        """
        Sets all living room lights to <color>
        :: CLI TRIGGER: color <color>

        """
        self._reset_lights()
        self.bridge.set_light(self.living_room, 'hue', int(self.args.color))

    def cli_list_lights(self):
        """
        Lists all lights currently connected to the hue bridge.

        """
        for light_id, light in self.bridge.get_api()['lights'].items():
            print("%s -\t%s" % (light_id, light['name']))

    def list_lights(self):
        """
        Lists all lights currently connected to the hue bridge, for non CLI usage

        """
        self.light_digest = {}
        for light_id, light in self.bridge.get_api()['lights'].items():
            self.light_digest[int(light_id)] = light['name']

        return self.light_digest

    def handle_exit(self):
        """
        Handles exiting with lighting restore and proper exit codes.

        """
        if self.restore_from_intial_state():
            print('Exiting - Successfully')
            sys.exit(0)
        else:
            print('Exiting - Error')
            sys.exit(1)

    def capture_initial_state(self):
        """
        Captures and stores all listed lights state and stores it in the intial_state var.

        """
        for light_id, light in self.bridge.get_api()['lights'].items():
            self.initial_state[int(light_id)] = light['state']

    def restore_from_intial_state(self):
        """
        Restores lights back to the state they were in when script was initially ran.

        """
        if not self.initial_state:
            print('No initial state recorded')
            return False

        if self.args.no_restore:
            print('Not returning to initial state, --no-restore used')
            return True

        print('Returning lights to initial state')
        for light_id, light_state in self.initial_state.items():
            new_old_state = {
                'on': light_state['on'],
                'xy': light_state['xy'],
                'sat': light_state['sat'],
                'bri': light_state['bri'],
                'transitiontime': 0,
            }

            self.bridge.set_light(light_id, new_old_state)

        return True

    def delay_to_hue_transition_time(self, delay) -> int:
        """
        Hue 'transitiontime' is based on milliseconds, but takes the milliseconds / 100.
        IE 400 milliseconds needs to be sent to the API as 4.
        This function takes seconds (fractional seconds if need be) and translates them to something
        hue's API will accept.

        """
        hue_transition = int((delay * 1000) / 100)
        return hue_transition

    def _load_config(self):
        """
        Loads a configuration file from ~/.phuey/config.json or the --config argument
        """
        config_location = None
        if self.args.config:
            config_location = self.args.confg
        elif os.path.exists("%s/.phuey/config.json" % str(Path.home())):
            config_location = "%s/.phuey/config.json" % str(Path.home())

        if not config_location:
            print("Error - No confguration set.")
            sys.exit(1)

        if not os.path.exists(config_location):
            print("Error - Could not find config file: %s" % config_location)
            sys.exit(1)

        with open(config_location) as config_file:
            data = json.load(config_file)

        return data

    def _set_global_brightness(self) -> int:
        """
        Sets global baseline brightness.
        Attempts to grab setting from redis key `phuey_global_brightness`, but if not available sets
        global brightness to 254, or full bore.

        """
        redis_bright = self.redis.get('phuey_global_brightness')
        if not redis_bright:
            return 254
        return int(redis_bright)

    def _set_global_delay(self) -> float:
        """
        Sets global baseline delay.
        Attempts to grab setting from CLI, then redis key `phuey_global_delay`, but if not neither
        are available sets the value to 3.
        This value should always be in seconds, but represented as a float.

        """
        delay = 0
        redis_delay = self.redis.get('phuey_global_delay')
        if self.args.delay:
            delay = float(self.args.delay)
        elif redis_delay:
            delay = float(redis_delay)

        if delay < .01:
            delay = 3

        return delay

    def _parse_args(self):
        """
        Parsers CLI args

        :returns: Parsed arguments
        :rtype: <Namespace>
        """
        parser = ArgumentParser()
        parser.add_argument(
            "pattern",
            nargs='?',
            default='',
            help="")

        parser.add_argument(
            "color",
            nargs='?',
            default='',
            help=".")

        parser.add_argument(
            "--delay",
            nargs='?',
            default=False,
            help="Sets the delay between animations shifts for some animations.")

        parser.add_argument(
            "--no-restore",
            default=False,
            help="Restores lights to their previous settings after animation stopped.",
            action='store_true')

        parser.add_argument(
            "--config",
            nargs='?',
            default=False,
            help="Location of the config file to use.")

        parser.add_argument(
            "-v",
            default=False,
            action='store_true',
            help="Run script in high verbosity mode.")

        args = parser.parse_args()
        return args

    def _print_welcome(self):
        if not self.args.v:
            return
        phuey_txt = """
 ____  __ __  __ __    ___  __ __
|    \|  |  ||  |  |  /  _]|  |  |
|  o  )  |  ||  |  | /  [_ |  |  |
|   _/|  _  ||  |  ||    _]|  ~  |
|  |  |  |  ||  :  ||   [_ |___, |
|  |  |  |  ||     ||     ||     |
|__|  |__|__| \__,_||_____||____/
phuey %s\n\n""" % __version__
        print(phuey_txt)


if __name__ == '__main__':
    Phuey().run()

# End File: phuey/phuey/__init__.py
