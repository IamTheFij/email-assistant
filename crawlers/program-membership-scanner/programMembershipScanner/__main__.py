import argparse
import base64
import io
import os

import barcode
import magic
import requests
from barcode.writer import SVGWriter


if __name__ == '__main__':
    INDEXER_URL = os.environ['INDEXER_URL']
    INDEXER_TOKEN = os.environ.get('INDEXER_TOKEN')

    parser = argparse.ArgumentParser(
        description='Add some membership programs.'
    )
    parser.add_argument('organization',
                        help='Organization the membership is made with.')
    parser.add_argument('memberName',
                        help='Name of the member of the program.')
    parser.add_argument('membershipNumber', help='Number of the membership.')
    parser.add_argument('--programName', help='Name of the program.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--barcode', help='Barcode of the form TYPE:DATA with TYPE a valid type from https://github.com/WhyNotHugo/python-barcode/blob/master/barcode/__init__.py#L29-L50.')
    group.add_argument('--image', help='Any image for the card')

    args = parser.parse_args()

    metadata = {
        '@type': 'ProgramMembership',
        '@context': 'http://schema.org',
        'hostingOrganization': {
            '@type': 'Organization',
            'name': args.organization,
        },
        'member': {
            '@type': 'Person',
            'name': args.memberName,
        },
        'membershipNumber': args.membershipNumber,
    }
    if args.programName:
        metadata['programName'] = args.programName

    # Handle barcode generation
    image = None
    if args.barcode:
        barcode_type, barcode_data = args.barcode.split(':', 1)

        fp = io.BytesIO()
        barcode.generate(barcode_type, barcode_data,
                         writer=SVGWriter(), output=fp)
        image = (
            'data:image/svg+xml;base64,%s' % (
                base64.b64encode(fp.getvalue()).decode('utf-8')
            )
        )
        fp.close()
    elif args.image:
        mime = magic.Magic(mime=True).from_file(args.image)
        with open(args.image, 'rb') as fp:
            image = 'data:%s;base64,%s' % (
                mime,
                base64.b64encode(fp.read()).decode('utf-8')
            )

    if image:
        metadata['image'] = image

    # Index token
    headers = {}
    if INDEXER_TOKEN:
        headers['Authorization'] = 'Bearer %s' % INDEXER_TOKEN
    response = requests.post(
        INDEXER_URL + '/token',
        json={
            'token': metadata['membershipNumber'],
            'type': metadata['@type'],
            'metadata': metadata
        },
        headers=headers,
    )
    response.raise_for_status()
    print(response.json())
