# Install:
#   * Create a virtualenv and `pip install -r requirements.txt` for all such files in the repo.
#   * For each Ruby submodule, use `bundle install --path vendor/bundle`.

export HOST=127.0.0.1
export DEBUG=1
export SQLALCHEMY_ECHO=1

PARSER_PACKAGE_TRACKING_PORT=4001
MAIN_INDEXER_PORT=4100
MAIN_VIEWER_PORT=4200
VIEWER_PACKAGE_TRACKING_PORT=4201

# Parsers
cd parsers/package-tracking && PORT=${PARSER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &

# Indexers
cd indexer && PORT=${MAIN_INDEXER_PORT} python -m indexer &

# Viewers
cd viewers/main && PORT=${MAIN_VIEWER_PORT} INDEXER_URL=http://127.0.0.1:${MAIN_INDEXER_PORT} VIEWER_PACKAGE_TRACKING_URL=http://127.0.0.1:${VIEWER_PACKAGE_TRACKING_PORT} python -m viewer &
cd viewers/package-tracking && PORT=${VIEWER_PACKAGE_TRACKING_PORT} bundle exec ruby main.rb &

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
wait
