#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
import queue as queue
import threading

class Worker(threading.Thread):
    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.kill_received = False
        self.tasks = tasks
        self.setDaemon(True)
        self.start()

    def stop(self):
        self.kill_received = True

    def run(self):
        while not self.kill_received:
            try:
                func, args, kargs = self.tasks.get(True, None)

                if not func:
                    break

                func(*args, **kargs)
            except:
                pass
            finally:
                self.tasks.task_done()

class ThreadPool():
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.tasks = queue.Queue()
        self.threads = [Worker(self.tasks) for _ in range(self.num_threads)]

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
