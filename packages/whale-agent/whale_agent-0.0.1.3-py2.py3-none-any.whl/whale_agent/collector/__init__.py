# -*- coding: utf8 -*-


class Collector(object):

    def __init__(self, conf):
        self.conf = conf

    def run(self):
        pass

    def result(self):
        return CollectResult()


class CollectResult(object):

    def __str__(self):
        return 'Collector result'
