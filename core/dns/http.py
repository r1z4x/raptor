#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

class Http:

    def __init__(self, url, path='/', method='HEAD', loop=None):
        self.user_agent_lists = set()
        self.url = url
        self.method = method
        self.path = path
        self.loop = loop

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
        async with aiohttp.ClientSession(loop=self.loop) as client:
            async with client.request(method=self.method, url=self.url) as resp:
                if resp.status == 200 || resp.status == 301:
                    print(self.url)
