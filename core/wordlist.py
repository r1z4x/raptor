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

    def tmp_check(self):
        return os.path.isfile(self.tmp_file)

    def load(self, calc_result=False):
        if not self.check():
            print('Wordlist Not Found!')
            sys.exit(0)

        if self.tmp_check() and calc_result == False:
            return open(self.tmp_file, 'r')

        self.file = open(self.path, 'r')

        wlists = []
        with self.file as infile:
            for f in infile:
                wlists.append(f.strip())
            infile.close()

        if self.subdomain_depth > 1 and calc_result == False:

            print("Temporary data set is being created...", end='\r')

            try:

                with open(self.tmp_file, 'w+') as infile:
                    for depth in range(0, self.subdomain_depth):
                        for p in permutations(wlists, r=depth+1):
                            infile.write("{0}\n".format('.'.join(p)))

                    infile.close()
            except OSError as e:
                print(e)
                sys.exit(0)

            return open(self.tmp_file, 'r')

        elif self.subdomain_depth == 1 and calc_result == False:

            return open(self.path, 'r')

        return wlists
