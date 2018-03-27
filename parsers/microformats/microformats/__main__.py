import json
import os

import bottle
import extruct


def microformats_to_jsonld(mf):
    if isinstance(mf, dict) and 'type' in mf and 'properties' in mf:
        if isinstance(mf['type'], list):
            # Fix a bug in JSON-LD format of some emails
            mf['type'] = ''.join(mf['type'])
        context, type = mf['type'].rsplit('/', 1)
        converted = {
            '@type': type,
            '@context': context
        }
        for key, property in mf['properties'].items():
            converted[key] = microformats_to_jsonld(property)
        return converted
    else:
        return mf


HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 4001))
DEBUG = bool(os.environ.get('DEBUG', True))

TYPES_TO_TOKEN = {
    "BusReservation": (
        lambda x: x.get('reservationNumber', None)
    ),
    "FlightReservation": (
        lambda x: x.get('reservationNumber', None)
    ),
    "TrainReservation": (
        lambda x: x.get('reservationNumber', None)
    ),
}


def get_type(item):
    type = item.get('@type', None)
    token = None

    if type in TYPES_TO_TOKEN:
        token = TYPES_TO_TOKEN[type](item)

    return type, token


def parse_microformats(message):
    parsed_microdata = extruct.extract(message)
    parsed_microdata = (
        [
            microformats_to_jsonld(x)
            for x in parsed_microdata['microdata']
        ] +
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
    return json.dumps(parse_microformats(
        body['message']['html'] or body['message']['plain']
    ))


if __name__ == '__main__':
    bottle.run(host=HOST, port=PORT, debug=DEBUG)
