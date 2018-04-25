"""
Implementation of fetching through the Weboob ``CapDocument`` capability. This
fetches for bills and documents on your accounts.

Serializes everything to schema.org schemas.
"""
import base64
import collections
import json
import logging
import mimetypes

from weboobCrawler.indexer import is_already_indexed

LOGGER = logging.getLogger(__name__)


def fetch_subscriptions(weboob_proxy, backend):
    """
    Fetch subscriptions from a given backend.

    :param weboob_proxy: An instance of ``WeboobProxy`` class.
    :param backend: A valid built backend to use.
    :return The list of fetched subscriptions (Weboob objects).
    """
    subscriptions = []
    for subscription in backend.iter_subscription():
        # Ensure ids are fully qualified, of the form id@backend_name.
        subscription.id = weboob_proxy._ensure_fully_qualified_id(
            subscription.id,
            backend
        )
        subscriptions.append(subscription)
    return subscriptions


def fetch_for_subscriptions(weboob_proxy, method, subscriptions, backend):
    """
    Fetch related items for a given list of subscriptions.

    :param weboob_proxy: An instance of ``WeboobProxy`` class.
    :param method: The method to call on the bakend to fetch items.
    :param subscriptions: A list of Weboob ``Subscription`` objects to fetch
        items from.
    :param backend: A valid built backend to use.
    :return The list of fetched items (Weboob objects).
    """
    items = collections.defaultdict(list)
    for subscription in subscriptions:
        for item in getattr(backend, method)(subscription.id.rsplit('@', 1)[0]):
            # Fetch all items for this subscriptions and ensure they have a
            # fully qualified id
            item.id = weboob_proxy._ensure_fully_qualified_id(
                item.id, backend
            )
            items[subscription.id].append(item)
    return items


def _guess_doc_mimetype(doc):
    """
    Guess the MIME type for a Weboob document.

    :param doc: A Weboob ``Document`` object.
    :return: The guessed MIME type or ``application/octet-stream``.
    """
    # Python mimetypes library expects a filename, so we have to build a
    # filename from the extension taken from Weboob data.
    guessed_mime = mimetypes.guess_type("foobar.%s" % doc.format)
    return guessed_mime[0] if guessed_mime[0] else 'application/octet-stream'


def serialize_document(doc, subscription):
    """
    Serialization of Weboob ``Document`` object to schema.org representation.

    :param doc: The Weboob ``Document`` object to serialize.
    :param subscription: The Weboob ``Subscription`` object from which the
        document was fetched.
    """
    if doc.type != 'bill':
        # If this is not a bill, serialize it as a DigitalDocument
        serialized_doc = {
            '@type': 'DigitalDocument',
            '@context': 'http://schema.org/',
            'identifier': doc.id,
            'dateCreated': doc.date,
            'name': doc.label,
            'additionalType': doc.type,
            'url': doc.url,
        }
        serialized_doc['fileFormat'] = _guess_doc_mimetype(doc)
        return serialized_doc

    # Otherwise, serialize it as an Invoice
    serialized_doc = {
        '@type': 'Invoice',
        '@context': 'http://schema.org/',
        'identifier': doc.id,
        'totalPaymentDue': {
            '@type': 'MonetaryAmount',
            'value': doc.price if not doc.income else -doc.price,
            'currency': doc.currency,
        },
        'name': doc.label,
        'date': doc.date,
        'url': doc.url,
        'accountId': subscription.id,
    }
    if doc.startdate and doc.finishdate:
        serialized_doc['billingPeriod'] = {
            doc.startdate
        }
        serialized_doc['totalPaymentDue'] = {
            'validFrom': doc.startdate,
            'validThrough': doc.finishdate,
        }
    if doc.vat:
        # Note this is not a standard schema.org key
        serialized_doc['totalPaymentDue']['vat'] = doc.vat
    if subscription.subscriber:
        serialized_doc['customer'] = {
            '@type': 'Person',
            'name': subscription.subscriber,
        }
    return serialized_doc


def fetch(weboob_proxy, backend):
    """
    Fetch and serialized data from a ``CapDocument`` enabled backend.

    :param weboob_proxy: An instance of ``WeboobProxy`` class.
    :param backend: A valid built backend to use.
    :returns: A list of schema.org serialized items to index.
    """
    LOGGER.info('Fetching data...')

    # First, fetch subscriptions and documents from Weboob
    subscriptions = fetch_subscriptions(weboob_proxy, backend)
    LOGGER.info('Found subscriptions %s.', [x.id for x in subscriptions])
    documents = fetch_for_subscriptions(
        weboob_proxy, 'iter_documents', subscriptions, backend
    )
    LOGGER.info('Found documents %s.',
                {k: [x.id for x in v] for k, v in documents.items()})

    serialized = []
    for subscription in subscriptions:
        for document in documents.get(subscription.id, []):
            # Serialize the fetched documents using schema.org schemas
            serialized_doc = serialize_document(document, subscription)
            if not is_already_indexed(serialized_doc['identifier']):
                # If the document was not already indexed, download the content
                # and put it in ``url`` field as a data URL.
                LOGGER.info('Downloading content for item %s.',
                            serialized_doc['identifier'])
                mimetype = _guess_doc_mimetype(document)
                serialized_doc['url'] = 'data:%s;base64,%s' % (
                    mimetype,
                    base64.b64encode(
                        backend.download_document(document)
                    ).decode('utf-8')
                )
            else:
                # Otherwise, the document was already indexed, simply discard
                # the URL or it will overwrite the fetched content as a data
                # URL in the indexer.
                del serialized_doc['url']
            serialized.append(serialized_doc)
    return serialized
