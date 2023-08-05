#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .defaults import *


class StoreRestClient(object):

    def __init__(self, host=DEFAULT_HOST):
        self.host = host

    def save(self, data, reference, symbol, jsonformat=DEFAULT_JSON_FORMAT):
        json = data.to_json(orient=jsonformat, date_format='iso')
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = '{host}{api_prefix}/{reference}/{symbol}?jsonformat={jsonformat}'.format(host=self.host,
                                                                                       api_prefix=API_URL_PREFIX,
                                                                                       reference=reference,
                                                                                       symbol=symbol,
                                                                                       jsonformat=jsonformat)
        response = requests.post(url, data=json, headers=headers)
        return response.status_code in [200, 201]

    def retrieve(self, reference, symbol, start=None, end=None, jsonformat=DEFAULT_JSON_FORMAT):
        url = '{host}{api_prefix}/{reference}/{symbol}?jsonformat={jsonformat}'.format(host=self.host,
                                                                                       api_prefix=API_URL_PREFIX,
                                                                                       reference=reference,
                                                                                       symbol=symbol,
                                                                                       jsonformat=jsonformat)
        if start:
            url += '&start=%s' % start.isoformat()
        if end:
            url += '&end=%s' % end.isoformat()

        response = requests.get(url)
        if response.status_code not in [200, 201]:
            return None

        json = response.text
        return pandas.read_json(json, orient=jsonformat)

    def delete(self, reference, symbol):
        url = '{host}{api_prefix}/{reference}/{symbol}'.format(host=self.host,
                                                               api_prefix=API_URL_PREFIX,
                                                               reference=reference,
                                                               symbol=symbol)
        response = requests.delete(url)
        return response.status_code in [200, 204]


class StoreRestDatasource(object):

    def __init__(self, reference, host=DEFAULT_HOST):
        self.reference = reference
        self.rest_client = StoreRestClient(host)

    def evaluate(self, context, symbol, start=None, end=None):
        return self.rest_client.retrieve(self.reference, symbol, start=start, end=end)
