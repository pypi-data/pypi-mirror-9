#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .defaults import *


class DFStoreRestClient(object):

    def __init__(self, host=DEFAULT_HOST):
        self.host = host
        self.json_client = JSONStoreRestClient(host)

    def save(self, data, reference, symbol, json_format=DEFAULT_JSON_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        json = data.to_json(orient=json_format, date_format=date_format)
        return self.json_client.save(json, reference, symbol, json_format=json_format)

    def retrieve(self, reference, symbol, start=None, end=None, json_format=DEFAULT_JSON_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        json = self.json_client.retrieve(reference, symbol, start=start, end=end, json_format=json_format, date_format=date_format)
        return None if json is None else pandas.read_json(json, orient=json_format)

    def delete(self, reference, symbol):
        return self.json_client.delete(reference, symbol)


class JSONStoreRestClient(object):

    def __init__(self, host=DEFAULT_HOST):
        self.host = host

    def save(self, json, reference, symbol, json_format=DEFAULT_JSON_FORMAT):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = '{host}{api_prefix}/{reference}/{symbol}?json_format={json_format}'.format(host=self.host,
                                                                                         api_prefix=API_URL_PREFIX,
                                                                                         reference=reference,
                                                                                         symbol=symbol,
                                                                                         json_format=json_format)
        response = requests.post(url, data=json, headers=headers)
        return response.status_code in [200, 201]

    def retrieve(self, reference, symbol, start=None, end=None, json_format=DEFAULT_JSON_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        url_base = '{host}{api_prefix}/{reference}/{symbol}?json_format={json_format}&date_format={date_format}'
        url = url_base.format(host=self.host,
                              api_prefix=API_URL_PREFIX,
                              reference=reference,
                              symbol=symbol,
                              json_format=json_format,
                              date_format=date_format)
        if start:
            url += '&start=%s' % start.isoformat()
        if end:
            url += '&end=%s' % end.isoformat()

        response = requests.get(url)
        if response.status_code not in [200, 201]:
            return None

        json = response.text
        return json

    def delete(self, reference, symbol):
        url = '{host}{api_prefix}/{reference}/{symbol}'.format(host=self.host,
                                                               api_prefix=API_URL_PREFIX,
                                                               reference=reference,
                                                               symbol=symbol)
        response = requests.delete(url)
        return response.status_code in [200, 204]
