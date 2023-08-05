#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pandas
import requests

from .defaults import *


class DFBigtempoRestClient(object):

    def __init__(self, host=DEFAULT_HOST):
        self.host = host
        self.json_client = JSONBigtempoRestClient(host)

    def process(self, reference, symbol, start=None, end=None, json_format=DEFAULT_JSON_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        json = self.json_client.process(reference, symbol, start=start, end=end, json_format=json_format, date_format=date_format)
        return None is json is None else pandas.read_json(json, orient=json_format)


class JSONBigtempoRestClient(object):

    def __init__(self, host=DEFAULT_HOST):
        self.host = host

    def process(self, reference, symbol, start=None, end=None, json_format=DEFAULT_JSON_FORMAT, date_format=DEFAULT_DATE_FORMAT):
        url_base = '{host}{api_prefix}/process/{reference}/{symbol}?json_format={json_format}&date_format={date_format}'
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
