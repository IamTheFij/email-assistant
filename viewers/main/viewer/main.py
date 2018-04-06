import os
import sys

import flask
import requests


app = flask.Flask(__name__)
app.config['DEBUG'] = True

indexer_url = os.environ.get('INDEXER_URL', 'http://indexer')


@app.route('/')
def check():
    return flask.render_template('home.html')


@app.route('/shipping')
def get_tokens():
    resp = requests.get(
        indexer_url+'/token',
        params={
            'filter_type': 'SHIPPING',
            'desc': True,
        },
    )
    resp.raise_for_status()
    tokens = resp.json().get('tokens')
    for token in tokens:
        try:
            resp = requests.get(
                'http://viewer_package_tracking:3000/info/'+token['token']
            )
            resp.raise_for_status()
            print('Response: ', resp.text, file=sys.stderr)
            info = resp.json()
            token['metadata'].update(info)
        except Exception as e:
            print('Error', e, file=sys.stderr)
            pass
    return flask.render_template('shipping.html', trackers=tokens)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
