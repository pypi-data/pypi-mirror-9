#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from .blueprint import new_blueprint
from .datastores import RemoteDatasourceFactory, LocalDatasourceFactory


class BigtempoAPI(object):

    def __init__(self, app=None, bigtempo_engine=None):
        self.app = app
        self.bigtempo_engine = bigtempo_engine

        if app is not None and bigtempo_engine is not None:
            self.init_app(app, bigtempo_engine)

    def init_app(self, app, bigtempo_engine):
        app.register_blueprint(new_blueprint(bigtempo_engine))

    @property
    def instance(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'bigtempo_engine_instance'):
                ctx.bigtempo_engine_instance = self.bigtempo_engine
            return ctx.bigtempo_engine_instance
        else:
            return self.bigtempo_engine

    @property
    def engine(self):
        return self.instance

    def create_datasource_factory(self, datastore):
        if isinstance(datastore, basestring):
            return RemoteDatasourceFactory(engine, datastore)
        else:
            return LocalDatasourceFactory(engine, datastore)
