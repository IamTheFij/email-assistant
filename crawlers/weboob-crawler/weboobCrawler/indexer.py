"""
Indexer related methods, methods to communicate with the indexer.
"""
import os

import requests

INDEXER_URL = os.environ['INDEXER_URL']


def index_token(data):
    """
    Index a new token.

    :param data: The data to index.
    :return: The payload returned by the indexer API.
    """
    response = requests.post(
        INDEXER_URL + '/token',
        data=data,
    )
    response.raise_for_status()
    return response.json()


def is_already_indexed(token):
    """
    Check whether a token has already been indexed or not.

    :param token: The token id to check.
    """
    response = requests.get(
        INDEXER_URL + '/token/' + token,
    )
    return response.status_code == requests.codes.ok
