import flask
import pandas

import flask_bigtempo.utils as butils
from .defaults import *


# TODO: Implement select route


def new_blueprint(bigtempo_engine,
                  default_json_format=DEFAULT_JSON_FORMAT,
                  default_date_format=DEFAULT_DATE_FORMAT):
    blueprint = flask.Blueprint('bigtempo', __name__, url_prefix=API_URL_PREFIX)


    @blueprint.route('/process/<reference>/<symbol>', methods=['GET'])
    def process(reference, symbol):
        json_format = flask.request.args.get('json_format', default_json_format)
        date_format = flask.request.args.get('date_format', default_date_format)
        start = butils.parse_datetime_str(flask.request.args.get('start', None))
        end = butils.parse_datetime_str(flask.request.args.get('end', None))

        try:
            datasource = bigtempo_engine.get(reference)
        except KeyError:
            flask.abort(404)

        data = datasource.process(symbol, start, end)
        if data is None:
            flask.abort(404)

        json = data.to_json(orient=json_format, date_format=date_format)
        return flask.Response(json, content_type='application/json')


    @blueprint.route('/select/all', methods=['GET'])
    def select_all():
        data = bigtempo_engine.select().all()
        return flask.jsonify(data)


    return blueprint
