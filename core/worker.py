#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import sys, time, signal
import functools
import socket
from time import sleep

import utils.colors as colors
from core.threadpool import ThreadPool
from tabulate import tabulate
from collections import namedtuple
from concurrent.futures import ALL_COMPLETED
import random
import threading
import signal

import core.wordlist as wordlist
import core.profile as profile

try:
	import queue
except ImportError:
	import Queue as queue

try:
	import dns.resolver
	from dns.exception import DNSException
	MODULE_DNSPYTHON = True
except ImportError:
	MODULE_DNSPYTHON = False
pass

try:
	import dns.resolver, dns.query, dns.zone
except:
	exit('ImportError: No module named python-dnspython\npip install dnspython')

REQUEST_TIMEOUT_DNS = 5.0

class Worker:

	def __init__(self, roots, max_threads, cluster_count, subdomain_depth, wordlist=None):
		self.roots = roots
		self.session = dns.resolver.Resolver()
		self.session.lifetime = REQUEST_TIMEOUT_DNS
		self.session.timeout = REQUEST_TIMEOUT_DNS
		self.max_threads = max_threads
		self.cluster_count = cluster_count
		self._counter = 0
		self.wordlist = wordlist
		self.subdomain_depth = subdomain_depth <= 0 and 1 or subdomain_depth

	DEFAULT_TIMEOUT = 0.1

	def __blocks(files, size=65536):
		while True:
			b = files.read(size)
			if not b: break
			yield b

	def start(self):

		wordlist_info = wordlist.Wordlist(self.wordlist, self.cluster_count, self.subdomain_depth)

		wordlists = []
		wfile_o = wordlist_info.load()

		if isinstance(wfile_o, list):
			wordlists = wfile_o
		else:
			with wfile_o as wfile:
				for line in wfile:
					print(line)

			sys.exit()

		try:

			global data_lists
			data_lists = {}

			start_time = time.time()

			#pool = ThreadPool(self.max_threads)
			pool = ThreadPool(self.max_threads)

			tasks_count = 0
			for idx, root in enumerate(self.roots):
				data_lists.update({ root : [] })
				nlists = set(self.get_nameservers(root))
				for word in wordlists:
					tasks_count = tasks_count + 1;
					pool.add_task(self.fetch_dns, root, nlists, word)

			qperc = 0
			while not pool.tasks.empty():
				qcurr = 100 * (tasks_count - pool.tasks.qsize()) / tasks_count
				sys.stdout.write('Scanning {0:.2f}%\r'.format(round(qcurr, 2)))
				sys.stdout.flush()

				time.sleep(1)

			for t in pool.threads:
				while not t.is_alive():
					pass
				t.stop()



			end_time = time.time()
			print("Elapsed time was %g seconds" % (end_time - start_time))

			if len(data_lists) > 0:

				print(colors.bcolors.OKGREEN + "\nRESULTS :" + colors.bcolors.ENDC)

				for _root in data_lists:

					profile_info = profile.Profile(filename=_root)
					profile_info.save(data_lists[_root])

					output = []
					for out in data_lists[_root]:
						output.append([out['domain'], out['dns_check'], out['zone_check'], out['port_check'], out['service_check']])

					if len(output) > 0:
						print("\nDomain : {0}".format(_root))
						print(tabulate(output, headers=['Domain', 'DNS Check', 'Zone Check', 'Port Check', 'Service Check'], tablefmt="psql", stralign="left"))

			else:
				print(colors.bcolors.FAIL + "\nNO RESULT!\n" + colors.bcolors.ENDC)

		except KeyboardInterrupt:  # pragma: no cover
			pass
		except Exception as e:
			print(str(e))
			pass
		finally:
			self.shutdown()

	def shutdown(self, force=False):
		pass

	def get_nameservers(self, domain):
		response = yield from self.session.query(domain, 'NS')

		nslists = []
		if not (response is None):
			for name_server in response:
				if not (name_server is None):
					name_server = str(name_server).rstrip('.')
					#nslists.append(socket.gethostbyname(name_server))
					nslists.append(name_server)

		return nslists

	def fetch_dns(self, root, nlists, word):

		#Normal dns checking
		answer = False

		try:
			tmp_domain = "{0}.{1}".format(word, root)
			answer = self.session.query(tmp_domain)

			if answer:
				data_lists[root].append({
					'domain'        : tmp_domain,
					'dns_check'     : True,
					'zone_check'    : False,
					'port_check'    : False,
					'service_check' : False
				})

				"""
				print('[{0}/{1}] {2}'.format(1, 4, tmp_domain), end='\r')
				time.sleep(10)
				print('[{0}/{1}] {2}'.format(2, 4, tmp_domain), end='\r')
				time.sleep(20)
				print('[{0}/{1}] {2}'.format(3, 4, tmp_domain), end='\r')
				time.sleep(30)
				print('[{0}/{1}] {2}'.format(4, 4, tmp_domain))"""

		except dns.resolver.NoNameservers:
			pass
		except dns.resolver.NXDOMAIN:
			pass
		except dns.exception.Timeout:
			pass
		except dns.resolver.NoAnswer:
			pass
		except Exception as e:
			pass
