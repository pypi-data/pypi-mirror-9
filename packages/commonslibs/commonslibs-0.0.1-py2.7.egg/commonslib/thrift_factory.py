#!/usr/bin/env python
# -*- coding: utf-8 -*-
from thrift.transport import TTransport
from thrift.transport.TSocket import TSocket

__author__ = 'freeway'


class ThriftClientFactory(object):

    _protocols = {}
    _transports = {}

    @classmethod
    def get_transport(cls, host, port):
        key = "{0}:{1}".format(host, port)
        transport = cls._transports.get(key, None)
        if transport is None:
            socket = TSocket(host, port)
            transport = TTransport.TBufferedTransport(socket)
            transport.open()
            cls._transports[key] = transport
        return transport


    @classmethod
    def clean_all(cls):
        for transport in cls._transports.values():
            transport.close()
        cls._transports.clear()
