import json
import os

import bottle
import extruct


HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 4001))
DEBUG = bool(os.environ.get('DEBUG', True))


def get_type(item):
    type = item.get('type', None)
    token = None

    if type.endswith('FlightReservation'):
        token = item.get('properties', {}).get('reservationNumber', None)

    return type, token


def parse_microformats(message):
    parsed_microdata = extruct.extract(message)
    parsed_microdata = (
        parsed_microdata['microdata'] +
        parsed_microdata['json-ld']
    )
    results = []
    for item in parsed_microdata:
        type, token = get_type(item)
        if not type or not token:
            continue
        results.append({
            'token': token,
            'type': type,
            'metadata': item
        })
    return results


@bottle.post('/parse')
def parse():
    body = bottle.request.json
    return json.dumps(parse_microformats(body['message']))


if __name__ == '__main__':
    bottle.run(host=HOST, port=PORT, debug=DEBUG)
