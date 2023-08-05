#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .core import DatastoreAPI
from .clients import DFStoreRestClient
from .defaults import *


class RESTStoreDatasource(object):

    def __init__(self, reference, host=DEFAULT_HOST):
        self.reference = reference
        self.rest_client = DFStoreRestClient(host)

    def evaluate(self, context, symbol, start=None, end=None):
        return self.rest_client.retrieve(self.reference, symbol, start=start, end=end)


class LocalStoreDatasource(object):

    def __init__(self, reference, storage):
        self.reference = reference
        self.storage = storage.instance if isinstance(storage, DatastoreAPI) else storage

    def evaluate(self, context, symbol, start=None, end=None):
        return self.storage.retrieve(self.reference, symbol, start=start, end=end)
