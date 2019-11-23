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
from .modules.animation_popo import AnimationPopo

__version__ = '0.0.1'



class Phuey(object):

    def __init__(self, animation=None):
        self.args = self._parse_args()
        self.redis = redis.Redis()
        self.config = self._load_config()
        self.bridge = Bridge(self.config['bridge_ip'])
        self.set_selected_lights()
        self.lights = self.bridge.get_light_objects('id')       # All lights in the Hue network
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

        elif self.args.pattern == 'popo':
            print('Running:\popo')
            AnimationPopo(self).run()

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

    def cli_list_lights(self):
        """
        Lists all lights currently connected to the hue bridge, for non CLI usage

        """
        self.light_digest = {}
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

    def get_local_config(self, value: str) -> str:
        """
        """
        value = redis_client.get(key)
        if not value:
            return ''
        return value.decode('ascii')

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

    def set_global_brightness(self, animation: str=None) -> int:
        """
        Sets global baseline brightness.
        Attempts to grab setting from redis key `phuey_global_brightness`, but if not available sets
        global brightness to 254, or full bore.

        """
        default = 254
        redis_bright = self._get_global_or_specific_generic_animation_option('brightness', animation)
        if redis_bright:
            brightness = redis_bright
        else:
            brightness = default

        self.brightness = brightness


        return brightness

    def set_global_delay(self, redis_key: str=None) -> float:
        """
        Sets global baseline delay.
        Attempts to grab setting from CLI, then redis key `phuey_global_delay`, but if not neither
        are available sets the value to 3.
        This value should always be in seconds, but represented as a float.

        """
        delay = 0
        # Attempt to grab the requested animation delay
        if redis_key:
            redis_delay = self.redis.get(redis_key)

        if not redis_delay:
            redis_delay = self.redis.get('phuey_global_delay')
        if self.args.delay:
            delay = float(self.args.delay)
        elif redis_delay:
            delay = float(redis_delay)

        if delay < .01:
            delay = 3
        self.delay = delay

        return True

    def _get_global_or_specific_generic_animation_option(self, option_type, animation: str=''):
        """
        """
        redis_key = 'phuey_animation_%s' % option_type
        if animation:
            redis_key = '%s_%s' % (redis_key, animation)
            redis_result = self._get_str_redis(redis_key)
            if redis_result:
                return redis_result

        redis_key = redis_key.replace('animation', 'global')
        redis_global = self._get_str_redis(redis_key)
        if redis_global:
            return redis_globalget

        return None

    def set_selected_lights(self) -> list:
        """
        """
        self.selected_lights = None
        selected_lights = None
        if 'light_ids' in self.config:
            self.selected_lights = self.config['light_ids']
            if self.args.v:
                print('Settings lights on file config %s:' % selected_lights)
        else:
            redis_lights = self._get_str_redis('phuey_light_ids')
            if redis_lights:
                redis_lights = redis_lights.replace(' ', '')
                if ',' in redis_lights:
                    redis_lights = redis_lights.split(',')
                else:
                    redis_lights = [redis_lights]

                clean_lights = []
                for light in redis_lights:
                    if light.isdigit():
                        clean_lights.append(int(light))
                    else:
                        print('cannot interperate %s as a light id' % light)
                redis_lights = clean_lights

            selected_lights = redis_lights
            if self.args.v:
                print('Settings lights on redis config %s:' % selected_lights)

        self.selected_lights = selected_lights
        if not self.selected_lights:
            print('ERROR NO SELECTED LIGHTS')
            exit(1)

        return self.selected_lights

    def _get_str_redis(self, key: str) -> str:
        """
        Gets a JSONable string from redis.

        """
        value = self.redis.get(key)
        if not value:
            return None
        return value.decode('ascii')


    def print_args(self):
        if self.args.v:
            print('\nDELAY: %s' % self.delay)
        if self.args.v:
            print('\nBRIGHTNESS: %s\n\n' % self.brightness)

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
