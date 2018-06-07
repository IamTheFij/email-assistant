import base64
import mimetypes
import os

import arrow


def _guess_doc_mimetype(filename):
    """
    Guess the MIME type of a document.
    """
    # Python mimetypes library expects a filename, so we have to build a
    # filename from the extension taken from Weboob data.
    guessed_mime = mimetypes.guess_type(filename)
    return guessed_mime[0] if guessed_mime[0] else 'application/octet-stream'


def health_to_schema(data, repo_dir):
    totalPaymentDue = sum(
        x['amount'] if not x['isRefund'] else -x['amount'] for x in data
    )

    orders = []
    for item in data:
        orders.append({
            "@type": "Order",
            "description": item['subtype'],
            "orderDate": (
                item['originalDate'] if item['originalDate'] else item['date']
            ),
            'totalPaymentDue': {
                '@type': 'MonetaryAmount',
                'value': item['amount']
            }
        })

    filename = os.path.join(repo_dir, 'data', data[0]['filename'])
    mimetype = _guess_doc_mimetype(filename)
    with open(filename, 'rb') as fh:
        url = 'data:%s;base64,%s' % (
            mimetype,
            base64.b64encode(fh.read()).decode('utf-8')
        )

    return {
        '@type': 'Invoice',
        '@context': 'http://schema.org/',
        'identifier': '%s' % os.path.splitext(data[0]['filename'])[0],
        'totalPaymentDue': {
            '@type': 'MonetaryAmount',
            'value': totalPaymentDue
        },
        'date': data[0]['date'],
        'name': '%s - %s' % (data[0]['vendor'],
                             arrow.get(data[0]['date']).format('DD/MM/YYYY')),
        'customer': {
            '@type': 'Person',
            'name': data[0]['beneficiary'],
        },
        'referencesOrder': orders,
        'url': url
    }
