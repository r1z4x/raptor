#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import sys
from itertools import permutations

class Wordlist:

    def __init__(self, path, cluster_count, subdomain_depth):
        self.path = path
        self.cluster_count = cluster_count
        self.file = None
        self.subdomain_depth = subdomain_depth
        self.tmp_file = "./wordlists/tmp.txt"

    def check(self):
        return os.path.isfile(self.path)

    def load(self, calc_result=False):
        if not self.check():
            print("File not found!")
            sys.exit()

        self.file = open(self.path, 'r')
        with self.file as infile:
            wlists = infile.read().split('\n')
            infile.close()

        wlists=list(filter(None, wlists))

        if self.subdomain_depth > 1 and calc_result == False:

            print("Temporary data set is being created...", end='\r')

            with open(self.tmp_file, 'w+') as infile:
                for depth in range(0, self.subdomain_depth):
                    for p in permutations(wlists, r=depth+1):
                        infile.write("{0}\n".format('.'.join(p)))

                infile.close()

            return open(self.tmp_file, 'r')

        return wlists
