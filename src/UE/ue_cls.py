#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


current_milli_time = lambda: int(round(time.time() * 1000))

# class UE(object):
class SRV:
    def start(self, *args, **kwargs):
        raise NotImplementedError

    def stop(self, *args, **kwargs):
        raise NotImplementedError

    def task(self, *args, **kwargs):
        raise NotImplementedError



