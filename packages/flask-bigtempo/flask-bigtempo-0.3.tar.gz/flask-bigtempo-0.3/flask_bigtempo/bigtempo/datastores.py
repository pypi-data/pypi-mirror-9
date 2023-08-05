#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .clients import DFBigtempoRestClient
from .defaults import *


class RESTStoreDatasource(object):

    def __init__(self, reference, host=DEFAULT_HOST):
        self.reference = reference
        self.rest_client = DFBigtempoRestClient(host)

    def evaluate(self, context, symbol, start=None, end=None):
        return self.rest_client.process(self.reference, symbol, start=start, end=end)
