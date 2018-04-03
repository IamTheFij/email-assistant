#!/usr/bin/env python2
"""
Weboob based crawler

Crawls your accounts on websites using Weboob and indexes the fetched data.

You should pass it an ``INDEXER_URL`` environment variable to specify where the
indexer resides. For instance,
``INDEXER_URL=http://localhost:4100 python -m weboobCrawler``.

It expects a path to a YAML configuration file as first argument on the command
line. An example YAML configuration file resides in ``config.yaml.example``.

The configuration options are:
    - ``backends``: mandatory, a list of Weboob backends to use.
    - ``modules_path``: mandatory, the path to the local clone of the Weboob
    modules to use. You can set it to ``!!null`` and it will use the modules
    from the ``weboob-modules`` Python package.

For each backend listed in the ``backends`` key, you should provide a config
option with the backend name and the config options to use to build the backend
(see Weboob doc). The ``config.yaml.example`` shows an example of this using
the ``fremobile`` backend.
"""
from __future__ import absolute_import
from __future__ import print_function

import collections
import json
import logging
import sys

import yaml

from weboobCrawler.capabilities import SUPPORTED_CAPS
from weboobCrawler.indexer import index_token

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

try:
    from weboob.core import WebNip
    from weboob.tools.json import WeboobEncoder
except ImportError:
    LOGGER.error("Weboob is not available on your system. Make sure you "
                 "installed it.")
    raise


class WeboobProxy(object):
    """
    Wrapper around Weboob ``WebNip`` class, to fetch housing posts without
    having to spawn a subprocess.
    """
    @staticmethod
    def version():
        """
        Get Weboob version.

        :return: The installed Weboob version.
        """
        return WebNip.VERSION

    def __init__(self, config):
        """
        Create a Weboob handle and try to load the modules.

        :param config: A config dict.
        """
        backends = config["backends"]

        # Create base WebNip object
        self.webnip = WebNip(modules_path=config["modules_path"])

        # Create backends
        self.backends = [
            self.webnip.load_backend(
                module,
                module,
                params=config[module]
            )
            for module in backends
        ]

    @staticmethod
    def _ensure_fully_qualified_id(item_id, backend):
        """
        Ensure a retrieved resource has a fully qualified ID, of the form
        id@backend_name.

        :param item_id: The id of a fetched resource.
        :param backend: The Weboob backend used to fetch the resource.
        :return: The fully qualified id (including the backend).
        """
        if item_id and '@' not in item_id:
            return '%s@%s' % (item_id, backend.NAME)
        return item_id

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.webnip.deinit()

    def fetch(self):
        """
        Main method, fetch everything from the loaded backends.
        """
        data = collections.defaultdict(dict)
        for backend in self.backends:
            caps = (x.__name__ for x in backend.iter_caps())
            for cap in caps:
                if cap not in SUPPORTED_CAPS:
                    continue
                # For each supported backend and capability, run the matching
                # fetch function
                data[backend.NAME][cap] = SUPPORTED_CAPS[cap](self, backend)
        return data


def main(config_file):
    # Load the YAML config
    with open(config_file, 'r') as fh:
        config = yaml.load(fh.read())

    with WeboobProxy(config) as weboob_proxy:
        # Fetch data from Weboob
        weboob_data = weboob_proxy.fetch()
        for backend in weboob_data.keys():
            for cap in weboob_data[backend].keys():
                for item in weboob_data[backend][cap]:
                    # Build an indexed token for all fetched items and index it
                    json_item = json.dumps(
                        {
                            'token': item['identifier'],
                            'type': item['@type'],
                            'metadata': item,
                        },
                        cls=WeboobEncoder
                    )
                    LOGGER.info('Indexing fetched data: %s.', json_item)
                    response = index_token(json_item)
    LOGGER.info('All done!')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s CONFIG_FILE' % sys.argv[0])

    main(sys.argv[1])
