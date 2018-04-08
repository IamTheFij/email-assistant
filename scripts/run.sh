#!/bin/sh
export HOST=127.0.0.1
export DEBUG=1
export SQLALCHEMY_ECHO=1

PARSER_PACKAGE_TRACKING_PORT=4001
PARSER_MICROFORMATS_PORT=4002
MAIN_INDEXER_PORT=4100
MAIN_VIEWER_PORT=4200
VIEWER_PACKAGE_TRACKING_PORT=4201

# Fill the variable below to put some auth in front of your indexer.
MAIN_INDEXER_API_TOKEN=secret

cd $(dirname "$0")/..
. .env/bin/activate

# Parsers
cd parsers/package-tracking && PORT=${PARSER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &
cd parsers/microformats && PORT=${PARSER_MICROFORMATS_PORT} python -m microformats &

# Indexers
cd indexer && PORT=${MAIN_INDEXER_PORT} API_TOKEN=${MAIN_INDEXER_API_TOKEN} python -m indexer &

# Viewers
cd viewers/main && PORT=${MAIN_VIEWER_PORT} INDEXER_URL=http://127.0.0.1:${MAIN_INDEXER_PORT} INDEXER_TOKEN=${MAIN_INDEXER_API_TOKEN} VIEWER_PACKAGE_TRACKING_URL=http://127.0.0.1:${VIEWER_PACKAGE_TRACKING_PORT} yarn run dev &
cd viewers/package-tracking && PORT=${VIEWER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
wait
