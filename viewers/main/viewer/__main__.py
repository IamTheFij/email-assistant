import os
import sys

import addict
import arrow
import flask
import requests


def format_datetime(value):
    value = arrow.get(value).to('local')
    return value.format('HH:MM DD/MM/YYYY')


app = flask.Flask(__name__)
app.config['DEBUG'] = bool(os.environ.get('DEBUG', True))
app.config['HOST'] = os.environ.get('HOST', '0.0.0.0')
app.config['PORT'] = int(os.environ.get('PORT', 5000))
app.jinja_env.filters['datetime'] = format_datetime

indexer_url = os.environ.get('INDEXER_URL', 'http://indexer')
viewer_package_tracking_url = os.environ.get(
    'VIEWER_PACKAGE_TRACKING_URL', 'http://viewer_package_tracking:3000'
)
viewer_microformats_url = os.environ.get(
    'VIEWER_MICROFORMATS_URL', 'http://viewer_package_tracking:3000'
)


@app.route('/')
def check():
    return flask.render_template('home.html')


@app.route('/ParcelDelivery')
def get_shipping():
    resp = requests.get(
        indexer_url+'/token',
        params={'filter_type': 'ParcelDelivery'},
    )
    resp.raise_for_status()
    tokens = resp.json().get('tokens')
    for token in tokens:
        try:
            resp = requests.get(
                viewer_package_tracking_url+'/info/'+token['token']
            )
            resp.raise_for_status()
            print('Response: ', resp.text, file=sys.stderr)
            info = resp.json()
            token['metadata'].update(info)
        except Exception as e:
            print('Error', e, file=sys.stderr)
            pass
    tokens = [
        addict.Dict(x)
        for x in tokens
    ]
    return flask.render_template('ParcelDelivery.html', trackers=tokens)


@app.route('/<data_type>')
def get_type(data_type):
    resp = requests.get(
        indexer_url+'/token',
        params={'filter_type': data_type},
    )
    resp.raise_for_status()
    tokens = [
        addict.Dict(x)
        for x in resp.json().get('tokens')
    ]
    return flask.render_template(data_type + '.html', tokens=tokens)


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
