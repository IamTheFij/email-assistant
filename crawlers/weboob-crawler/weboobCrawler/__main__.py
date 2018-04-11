#!/usr/bin/env python2
"""
Weboob based crawler

Crawls your accounts on websites using Weboob and indexes the fetched data.

You should pass it an ``INDEXER_URL`` environment variable to specify where the
indexer resides. For instance,
``INDEXER_URL=http://localhost:4100 python -m weboobCrawler``.

It expects a path to a INI configuration file as first argument on the command
line. An example INI configuration file resides in ``config.ini.example``.
"""
from __future__ import absolute_import
from __future__ import print_function

import collections
import configparser
import json
import logging
import subprocess
import sys

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


def eventually_call_command(value):
    """
    Eventually call a command to get the value, if the value starts and ends
    with quotes "`".

    :param value: The value to process.
    :returns: The processed value.
    """
    if value.startswith(u'`') and value.endswith(u'`'):
        cmd = value[1:-1]
        try:
            processed_value = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(u'The call to the external tool failed: %s' % e)
        processed_value = processed_value.decode('utf-8')
        processed_value = processed_value.split('\n')[0].strip('\r\n\t')
        return processed_value
    return value


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
        backends = {}
        for k in [x for x in config.keys() if x != 'DEFAULT']:
            backends[k] = config[k]['backend']

        # Create base WebNip object
        self.webnip = WebNip(
            modules_path=config['DEFAULT']['modules_path']
        )

        # Create backends
        self.backends = []
        for name, module in backends.items():
            try:
                self.backends.append(
                    self.webnip.load_backend(
                        module,
                        module,
                        params={
                            # Get params, calling the subcommands if necessary
                            k: eventually_call_command(v)
                            for k, v in config[name].items()
                        }
                    )
                )
            except Exception as exc:
                LOGGER.error(
                    'An error occured whild building backend %s: %s',
                    name,
                    str(exc)
                )


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
                try:
                    data[backend.NAME][cap] = SUPPORTED_CAPS[cap](
                        self, backend
                    )
                except Exception as exc:
                    LOGGER.error(
                        ('An error occured whild fetching %s with capability '
                         '%s: %s'),
                        backend.NAME,
                        cap,
                        str(exc)
                    )
        return data


def main(config_file):
    # Load the config
    config = configparser.ConfigParser(allow_no_value=True)
    if not config.read(config_file):
        LOGGER.error('Unreadable config file %s.', config_file)
        sys.exit(1)

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
                    index_token(json_item)
    LOGGER.info('All done!')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s CONFIG_FILE' % sys.argv[0])

    main(sys.argv[1])
