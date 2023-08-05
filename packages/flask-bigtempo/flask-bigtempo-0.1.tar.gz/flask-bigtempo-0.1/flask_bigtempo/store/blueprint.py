import flask
import pandas

from .defaults import *


def new_blueprint(storage, default_json_format=DEFAULT_JSON_FORMAT):
    blueprint = flask.Blueprint('datastore', __name__, url_prefix=API_URL_PREFIX)


    @blueprint.route('/<reference>/<symbol>', methods=['POST', 'PUT'])
    def save(reference, symbol):
        jsonformat = flask.request.args.get('jsonformat', default_json_format)

        json = flask.request.get_data()
        data = pandas.read_json(json, orient=jsonformat)
        storage.save(data, reference, symbol)

        return flask.jsonify({'status': True})


    @blueprint.route('/<reference>/<symbol>', methods=['GET'])
    def retrieve(reference, symbol):
        jsonformat = flask.request.args.get('jsonformat', default_json_format)
        start = flask.request.args.get('start', None)
        end = flask.request.args.get('end', None)

        data = storage.retrieve(reference, symbol, start=start, end=end)
        if data is None:
            flask.abort(404)

        json = data.to_json(orient=jsonformat, date_format='iso')
        return flask.Response(json, content_type='application/json')

    @blueprint.route('/<reference>/<symbol>', methods=['DELETE'])
    def delete(reference, symbol):
        status = storage.delete(reference, symbol)

        return flask.jsonify({'status': status})


    return blueprint
