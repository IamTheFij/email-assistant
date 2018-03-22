import os

import bottle


HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 4001))
DEBUG = bool(os.environ.get('DEBUG', True))


@bottle.get('/')
def index():
    return 'OK'


if __name__ == '__main__':
    bottle.run(host=HOST, port=PORT, debug=DEBUG)
