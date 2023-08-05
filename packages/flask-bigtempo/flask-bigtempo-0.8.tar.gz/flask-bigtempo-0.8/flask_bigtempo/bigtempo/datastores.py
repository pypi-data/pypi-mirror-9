#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .clients import DFBigtempoRestClient
from .defaults import *
from ..store.datasources import RESTStoreDatasource, LocalStoreDatasource


class RESTBigtempoDatasource(object):

    def __init__(self, reference, host=DEFAULT_HOST):
        self.reference = reference
        self.rest_client = DFBigtempoRestClient(host)

    def evaluate(self, context, symbol, start=None, end=None):
        return self.rest_client.process(self.reference, symbol, start=start, end=end)


class RemoteDatasourceFactory(object):

    def __init__(self, engine, host):
        self.engine = engine
        self.host = host

    def register(self, reference, bigtempo=False, **kwargs):
        ds_cls = RESTBigtempoDatasource if bigtempo else RESTStoreDatasource
        datasource = ds_cls(reference, self.host)
        self.engine(reference, **kwargs)(datasource)
        return self


class LocalDatasourceFactory(object):

    def __init__(self, engine, datastore):
        self.engine = engine
        self.datastore = datastore

    def register(self, reference, **kwargs):
        datasource = LocalStoreDatasource(reference, self.datastore)
        self.engine(reference, **kwargs)(datasource)
        return self
