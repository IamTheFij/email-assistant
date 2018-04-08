"""
Indexer related methods, methods to communicate with the indexer.
"""
import os

import requests

INDEXER_URL = os.environ['INDEXER_URL']
INDEXER_TOKEN = os.environ.get('INDEXER_TOKEN')


def index_token(data):
    """
    Index a new token.

    :param data: The data to index.
    :return: The payload returned by the indexer API.
    """
    headers = {}
    if INDEXER_TOKEN:
        headers['Authorization'] = 'Bearer %s' % INDEXER_TOKEN
    response = requests.post(
        INDEXER_URL + '/token',
        data=data,
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def is_already_indexed(token):
    """
    Check whether a token has already been indexed or not.

    :param token: The token id to check.
    """
    headers = {}
    if INDEXER_TOKEN:
        headers['Authorization'] = 'Bearer %s' % INDEXER_TOKEN

    response = requests.get(
        INDEXER_URL + '/token/' + token,
        headers=headers
    )
    return response.status_code == requests.codes.ok
