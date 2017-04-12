#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, aiodns, urllib.request
import time, socket, sys
import utils.colors as colors
from tabulate import tabulate

try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

try:
	import dns.resolver, dns.query, dns.zone
except:
    exit('ImportError: No module named python-dnspython\npip install dnspython')

class Scanner:

    def __init__(self, roots, max_tasks=1000, cluster_count=1000, wordlist=None):
        self.loop = asyncio.get_event_loop()
        self.roots = roots
        self.subtasks = []
        self.wordlist = wordlist
        self.max_tasks = max_tasks
        self.cluster_count = cluster_count
        self.q = Queue(loop=self.loop)
        self.current_domain = None
        self.done = []
        #self.session = aiodns.DNSResolver(loop=self.loop)
        self.session = dns.resolver.Resolver()
        self.root_domains = set()

        self.t0 = time.time()
        self.t1 = None
        self.session.timeout = 2.0
        self.session.lifetime = 2.0

    """def close(self):
        self.session.close()"""

    @asyncio.coroutine
    def start(self):
        yield from asyncio.gather(*self.get_subtasks())

    @asyncio.coroutine
    def stop(self):
        pass
        #Stop tasks
        #for t in reversed(self.subtasks):
        #    t.close()

        #Yarım kalan süreçlerin tamamlanması için
        #return asyncio.wait_for(*[t.wait_closed() for t in self.subtasks], return_exceptions=True)

    @asyncio.coroutine
    def work(self, domain):
        try:
            yield from self.fetch(domain)
        except asyncio.CancelledError:
            pass
        except asyncio.InvalidStateError:
            pass
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print("Error : " + e)

    @asyncio.coroutine
    def get_subtasks(self):

        if len(self.subtasks) > 0:
            return list(self.subtasks)

        wlists = self.load_wordlist()
        wlists = self.cluster_sorting(wlists)

        for root_domain in self.roots:
            self.subtasks.append(asyncio.async(self.work(root_domain), loop=self.loop))

            for word in wlists[0][0:500]:
                self.subtasks.append(asyncio.async(self.work('{}.{}'.format(word.strip(), root_domain)), loop=self.loop))
                pass

        return list(self.subtasks)

    @asyncio.coroutine
    def fetch(self, domain):

        try:
                #yield from print(domain)

                #yield from asyncio.sleep(5)

                """
                #Zone Check
                zone = dns.query.xfr(ns_ip, "demo.mealmeal.co.uk")
                if zone:
                    for name, node in zone.nodes.items():
                        if name != '@' and name != '*':
                            print(name + '.' + root_domain)

                """
                #Http Check
                http_request = Http("http://" + domain, loop=self.loop)
                http_request.send()
                #print("")

                pass

        except dns.exception.FormError as dns_error:
            print("Error : " + str(dns_error))

            """
            response = yield from self.session.query(domain, 'NS')

            nslists = set()
            for name_server in response:
                name_server = str(name_server.host).rstrip('.')
                #nslists.add(socket.gethostbyname(name_server))
                nslists.add(name_server)

            for ns_ip in nslists:
                zone = False
                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain))
                soc = socket.gethostbyname_ex(domain)

                print(soc)

                if zone:
                    for name, node in zone.nodes.items():
                        print(name)

        except dns.exception.FormErro as dns_error:
            print("Error : " + str(dns_error))"""

    def get_nameservers(self, domain):
        response = self.session.query(domain, 'NS')

        nslists = []
        for name_server in response:
            name_server = socket.gethostbyname_ex(str(name_server).rstrip('.'))
            nslists.append(name_server)

        return nslists

    def load_wordlist(self):
        filename = open(self.wordlist,'r')
        with filename as infile:
            wlist = filename.read().split('\n')
        filename.close
        return list(filter(None, wlist))

    """def add_domain(self, ns, domain):
        self.q.put_nowait(ns, domain)"""

    def table_output(self, columns, rows):
        print(tabulate(rows, columns, tablefmt="grid"))
        print()

    def cluster_sorting(self, words, max_iter_length=1000):
        #[list(t) for t in zip(*[iter(words)] * max_iter_length)]
        #Word listesini kümelendir.
        return [words[x:x+max_iter_length] for x in range(0, len(words), max_iter_length)]


class Http:

    def __init__(self, url, path='/', method='HEAD', loop=None):
        self.user_agent_lists = set()
        self.url = url
        self.method = method
        self.path = path
        self.loop = loop
        self.timeout = 0.5 #Default

    def load_user_agents(self, file_path):
        ua_lists = []
        with open(file_path, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    ua_lists.append(ua.strip()[1:-1-1])
        random.shuffle(ua_lists)
        return ua_lists

    def get_random_user_agent(self):
        if len(self.user_agent_lists) == 0:
            _ROOT = os.path.abspath(os.path.dirname(__file__))
            self.user_agent_lists = self.load_user_agents(os.path.join(_ROOT, 'utils', 'user_agents.txt'))

        return random.choice(self.user_agent_lists)

    def send(self):
        try:
            response = urllib.request.urlopen(url=self.url, timeout=self.timeout)
            assert response.status == 200 or response.status == 301
            print(self.url)
        except urllib.error.URLError:
            print("Error : " + self.url)
            pass
