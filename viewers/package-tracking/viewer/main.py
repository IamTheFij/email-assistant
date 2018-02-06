import os
import sys

from flask_bootstrap import Bootstrap
import flask
import requests


app = flask.Flask(__name__)
app.config['DEBUG'] = True
Bootstrap(app)

indexer_url = os.environ.get('INDEXER_URL', 'http://indexer')


@app.route('/')
def check():
    return 'OK'


@app.route('/shipping')
def get_tokens():
    resp = requests.get(
        indexer_url+'/token',
        params={'filter_type': 'SHIPPING'},
    )
    resp.raise_for_status()
    print(resp.text, file=sys.stderr)
    tokens = resp.json().get('tokens')
    return flask.render_template('shipping.html', trackers=tokens)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
