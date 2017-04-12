#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import sys

class Wordlist:

    def __init__(self, path, cluster_count):
        self.path = path
        self.cluster_count = cluster_count
        self.tmp_file = None

    def check(self):
        return os.path.isfile(self.path)


    def load(self):
        if not self.check():
            print("File not found!")
            sys.exit()

        self.tmp_file = open(self.path, 'r')
        with self.tmp_file as infile:
            wlist = self.tmp_file.read().split('\n')
        self.close()

        return list(filter(None, wlist))

    def close(self):
        if not self.tmp_file is None:
            self.tmp_file.close()
