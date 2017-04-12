#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

FILE_EXTENSION = 'cfg'
PROFILE_DEFAULT_PATH = './profiles/'

class Profile:

    def __init__(self, filename, path=None):
        self.path = path is not None and "{0:s}/".format(path.rstrip('/')) or PROFILE_DEFAULT_PATH
        self.filename = '{0:s}.{1:s}'.format(filename.replace('.', '_'), FILE_EXTENSION)

    def check(self):
        return os.path.isfile(self.path)

    def create_directory(self):
        if os.path.isdir(self.path):
            return True

        try:
            os.makedirs(self.path, exist_ok=True)
            return True
        except OSError as exc:
            print("File and Directory could not be created.")
            sys.exit()

        return False

    def save(self, values):
        if self.create_directory():

            if not ( (isinstance(values, list) or isinstance(values, dict)) and len(values) > 0):
                return False

            with open('{0}/{1}'.format(self.path, self.filename), 'w') as outfile:
                json.dump(values, outfile, indent=4)

            return True

        return False

    def load(self):
        pass
