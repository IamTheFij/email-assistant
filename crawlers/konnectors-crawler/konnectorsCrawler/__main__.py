import collections
import configparser
import json
import logging
import os
import shutil
import subprocess32 as subprocess
import sys

import git
import requests

from konnectorsCrawler.doctypes.health import health_to_schema


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


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


def clean_sensitive_files(repo_dir):
    IMPORTED_DATA_PATH = os.path.join(repo_dir, 'importedData.json')
    if os.path.isfile(IMPORTED_DATA_PATH):
        os.remove(IMPORTED_DATA_PATH)

    DOWNLOADED_DATA_PATH = os.path.join(repo_dir, 'data')
    if os.path.isdir(DOWNLOADED_DATA_PATH):
        shutil.rmtree(DOWNLOADED_DATA_PATH)

    KONNECTOR_DEV_CONFIG_PATH = os.path.join(repo_dir,
                                             'konnector-dev-config.json')
    if os.path.isfile(KONNECTOR_DEV_CONFIG_PATH):
        os.remove(KONNECTOR_DEV_CONFIG_PATH)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: %s config_file' % sys.argv[0])

    # Load the config
    config = configparser.ConfigParser(allow_no_value=True)
    if not config.read(sys.argv[1]):
        LOGGER.error('Unreadable config file %s.', config_file)
        sys.exit(1)

    # Get the konnectors to use
    konnectors = list(set(
        (v['backend'], v.get('branch', 'master')) for k, v in config.items() if k != 'DEFAULT'
    ))

    # Clone/update the konnectors
    konnectors_dir = config['DEFAULT']['konnectors_dir']
    if not os.path.isdir(konnectors_dir):
        LOGGER.info('Creating directory %s.', konnectors_dir)
        os.makedirs(konnectors_dir)

    for repo_url, branch in konnectors:
        # Clone the git repo
        LOGGER.info('Cloning connector from %s in %s...',
                    repo_url, konnectors_dir)
        repo_name = os.path.splitext(repo_url.split('/')[-1])[0]
        repo_dir = os.path.join(konnectors_dir, repo_name)
        if not os.path.isdir(repo_dir):
            repo = git.Repo.clone_from(repo_url, repo_dir)
        else:
            repo = git.Repo(repo_dir)

        # Checkout the HEAD of the expected branch
        LOGGER.info('Checking out branch %s in %s...', branch, repo_dir)
        repo.remotes.origin.fetch()
        try:
            head = next(
                x for x in repo.remotes.origin.refs
                if x.name.endswith('/%s' % branch)
            )
            head.checkout()
        except StopIteration:
            LOGGER.error('Unknown branch %s for connector %s.', branch,
                         repo_url)
            continue

        # Install JS deps
        # TODO: Check konnectors/libs version
        LOGGER.info('Installing JS dependencies in %s...', repo_dir)
        subprocess.check_call(['yarn', 'install'], stdout=subprocess.DEVNULL,
                              cwd=repo_dir)

    # Fetch data
    for k, v in config.items():
        if k == 'DEFAULT':
            continue

        repo_name = os.path.splitext(v['backend'].split('/')[-1])[0]
        repo_dir = os.path.join(konnectors_dir, repo_name)

        clean_sensitive_files(repo_dir)

        konnector_dev_config = {
            "COZY_URL": "http://cozy.tools:8080",
            "fields": {}
        }
        konnector_dev_config['fields'].update({
            k2: v2 for k2, v2 in v.items()
            if k2 != 'backend' and k2 not in config['DEFAULT'].keys()
        })
        with open(
            os.path.join(repo_dir, 'konnector-dev-config.json'), 'w'
        ) as fh:
            json.dump(konnector_dev_config, fh)

        try:
            # Run konnector
            LOGGER.info('Running connector %s...', k)
            subprocess.check_call(['yarn', 'standalone'],
                                  stdout=subprocess.DEVNULL, cwd=repo_dir)
            # Post-processing
            with open(os.path.join(repo_dir, 'importedData.json'), 'r') as fh:
                imported_data = json.load(fh)

            # Combine all fetched documents by types and group by filename
            sorted_imported_data = collections.defaultdict(
                lambda: collections.defaultdict(list)
            )
            for data in imported_data:
                sorted_imported_data[data['type']][data['filename']].append(data)

            # Then loop on the data and convert it to schema.org formatting
            # before indexing
            for data_type, data_list in sorted_imported_data.items():
                if data_type == 'health':
                    for filename, data in data_list.items():
                        LOGGER.info('Post-processing health data %s.',
                                    filename)
                        converted_item = health_to_schema(data, repo_dir)
                        index_token(json.dumps({
                            'token': converted_item['identifier'],
                            'type': converted_item['@type'],
                            'metadata': converted_item
                        }))
                else:
                    LOGGER.warn('Unknown data type %s.', data_type)
        finally:
            LOGGER.info('Cleaning sensitive files left in %s.', repo_dir)
            clean_sensitive_files(repo_dir)
