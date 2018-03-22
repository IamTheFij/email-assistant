#!/bin/sh
export HOST=127.0.0.1
export DEBUG=1
export SQLALCHEMY_ECHO=1

PARSER_PACKAGE_TRACKING_PORT=4001
PARSER_MICROFORMATS_PORT=4002
MAIN_INDEXER_PORT=4100
MAIN_VIEWER_PORT=4200
VIEWER_PACKAGE_TRACKING_PORT=4201
VIEWER_MICROFORMATS_PORT=4202

cd $(dirname "$0")
source .env/bin/activate

# Parsers
cd parsers/package-tracking && PORT=${PARSER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &
cd parsers && PORT=${PARSER_MICROFORMATS_PORT} python -m microformats &

# Indexers
cd indexer && PORT=${MAIN_INDEXER_PORT} python -m indexer &

# Viewers
cd viewers/main && PORT=${MAIN_VIEWER_PORT} INDEXER_URL=http://127.0.0.1:${MAIN_INDEXER_PORT} VIEWER_PACKAGE_TRACKING_URL=http://127.0.0.1:${VIEWER_PACKAGE_TRACKING_PORT} VIEWER_MICROFORMATS_URL=http://127.0.0.1:${VIEWER_MICROFORMATS_PORT} python -m viewer &
cd viewers/package-tracking && PORT=${VIEWER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &
cd viewers && PORT=${VIEWER_MICROFORMATS_PORT} python -m microformats &

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
wait
