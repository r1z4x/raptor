#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A faster sudomain finder -- main driver program."""

__author__  = 'Rizacan Tufan <rizacantufan@gmail>'
__version__ = '1.0.0'
__url__     = ''
__description__ = ''

# TODO:
# - Add arguments to specify TLS settings (e.g. cert/key files).

import argparse
import asyncio
import logging
import sys
import os
import re
import signal
import time
import threading
import core.worker as worker
import utils.colors as colors
from concurrent.futures import ThreadPoolExecutor

ARGS = argparse.ArgumentParser(description="DNS-based subdomain finder")

ARGS.add_argument(
    '-t', '--max_threads', action='store', type=int, metavar='N',
    default=500, help='Limit concurrent connections')

ARGS.add_argument(
    '-c', '--cluster_count', action='store', type=int, metavar='N',
    default=500, help='Limit cluster')

ARGS.add_argument(
    '-d', '--subdomain_depth', action='store', type=int, metavar='N',
    default=1, help='Subdomain Depth Length')

ARGS.add_argument(
    '-w', '--wordlist', action='store', metavar='N', help='Specific path to wordlist file')

ARGS.add_argument(
    'roots', nargs='*',
    default=[], help='Domains')

ARGS.add_argument(
    '-v', '--verbose', action='count', dest='level',
    default=2, help='Verbose logging (repeat for more verbose)')

def print_header():
    print(colors.bcolors.OKBLUE + """

,-.----.                             ___
\    /  \              ,-.----.    ,--.'|_
;   :    \             \    /  \   |  | :,'   ,---.    __  ,-.
|   | .\ :             |   :    |  :  : ' :  '   ,'\ ,' ,'/ /|
.   : |: |   ,--.--.   |   | .\ :.;__,'  /  /   /   |'  | |' |
|   |  \ :  /       \  .   : |: ||  |   |  .   ; ,. :|  |   ,'
|   : .  / .--.  .-. | |   |  \ ::__,'| :  '   | |: :'  :  /
;   | |  \  \__\/: . . |   : .  |  '  : |__'   | .; :|  | '
|   | ;\  \ ," .--.; | :     |`-'  |  | '.'|   :    |;  : |
:   ' | \.'/  /  ,.  | :   : :     ;  :    ;\   \  / |  , ;
:   : :-' ;  :   .'   \|   | :     |  ,   /  `----'   ---'
|   |.'   |  ,     .-./`---'.|      ---`-'
`---'      `--`---'      `---`


""" + colors.bcolors.ENDC + """Raptor v""" + __version__ + ", by " + __author__)

def valid_domain(domain):
    #Valid Hostname
    return re.match(r'^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$', domain)

def main():

    signal.signal(signal.SIGINT, sigint_handler)

    global data_lists, threads

    print_header()

    args = ARGS.parse_args()
    if not args.roots:
        print('Use --help for command line help')
        return

    _ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

    if args.wordlist:
        wordlist = os.path.join(args.wordlist)
    else:
        wordlist = os.path.join(_ROOT_DIR, 'wordlists', 'wordlist.txt')

    if not os.path.isfile(wordlist):
        print(colors.bcolors.WARNING + "File not found : " + wordlist + colors.bcolors.ENDC)
        sys.exit(0)

    print(colors.bcolors.WARNING + "Default Wordlist : " + wordlist + colors.bcolors.ENDC)

    print()

    '''
        İşlem süreci Başlatılıyor.
    '''

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels)-1)])

    #loop = asyncio.SelectorEventloop()
    #loop = asyncio.get_event_loop()
    #loop.add_signal_handler(signal.SIGINT, my_handler)

    #loop.set_default_executor(ThreadPoolExecutor(max_workers=20))

    roots = {root for root in args.roots if valid_domain(root) is not None}

    w = worker.Worker(roots,
       max_threads=args.max_threads,
       cluster_count=args.cluster_count,
       subdomain_depth=args.subdomain_depth,
       wordlist=wordlist)

    w.start()

def sigint_handler(signal, frame):
    sys.stdout.write('\nStopping threads... ')
    sys.stdout.flush()

    try:

        for w in threads:
            w.stop()

    except NameError:
        pass

    time.sleep(1)

    sys.stdout.write('Done\n')
    sys.exit(0)


if __name__ == '__main__':
    main()
