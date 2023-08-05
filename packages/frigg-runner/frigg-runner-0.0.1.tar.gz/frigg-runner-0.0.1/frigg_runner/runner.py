# -*- coding: utf8 -*-

import os.path
import sys

import yaml
from invoke import run as cmd_run
from invoke.exceptions import Failure
from yaml.error import YAMLError

DEFAULT_CONFIG_FILES = ['.frigg.yml', '.frigg.yaml']
HEADER = '\033[95m'
OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'


class Runner(object):

    def __init__(self, config_file, full_run):
        self.config_file = config_file
        self.full_run = full_run
        self.config = {}

    def run(self):
        self.read_config()

        tasks = self.config.get('tasks', [])
        print('Detcted following tasks:')
        for task in tasks:
            print('* %s' % task)

        success_list = []
        error_list = []

        for task in tasks:
            status, command = self.run_task(task)
            if status:
                success_list.append(command)
            else:
                error_list.append(command)

        print('\n\n\n\n')

        if len(error_list) > 0:
            print(FAIL + ''.join(['#' for x in range(100)]) + ENDC)
            print(FAIL + 'Failure!' + ENDC)
            for fail in error_list:
                print(FAIL + '* %s' % fail + ENDC)
        else:
            print(OKGREEN + ''.join(['#' for x in range(100)]) + ENDC)
            print(OKGREEN + 'Success' + ENDC)

    def get_config_file_name(self):
        if self.config_file:
            if os.path.isfile(self.config_file):
                return self.config_file

        for file in DEFAULT_CONFIG_FILES:
            if os.path.isfile(file):
                return file

        return None

    def read_config(self):
        filename = self.get_config_file_name()
        if not filename:
            print('Could not find a config file.')
            sys.exit(1)
        try:
            with open(filename) as file:
                content = file.read()
                config = yaml.load(content)
        except (IOError, YAMLError):
            print('Could not parse the configfile as YAML')
            sys.exit(1)

        self.config = config

    def run_task(self, command):
        def print_header():
            print(HEADER + '\n\n%s\n%s\n%s' % (''.join(['#' for x in range(100)]),
                                               ('# %s ' % command) +
                                               ''.join([' ' for x in range((100-len(command))-4)]) +
                                               '#', ''.join(['#' for x in range(100)])) + ENDC)

        print_header()

        try:
            cmd_run(command)
            return True, command
        except (SystemExit, Failure):
            print(FAIL + '\n\n%s\n%s\n%s' % (''.join(['#' for x in range(100)]),
                                             ('# %s ' % 'Error when executing %s' % command) +
                                             ''.join(
                                                 [' ' for x in
                                                  range((100-len('Error when executing %s'
                                                                 % command))-4)]) +
                                             '#', ''.join(['#' for x in range(100)])) + ENDC)

            if not self.full_run:
                sys.exit(1)

            return False, command
