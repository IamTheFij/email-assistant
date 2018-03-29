#!/bin/sh

ROOT_DIR=$(realpath $(dirname "$0")/..)
cd ${ROOT_DIR}

virtualenv -p python3 .env && source .env/bin/activate
find . -name requirements.txt -exec pip install -r {} \;

for i in $(find . -name "*.rb" -print | grep -v "vendor/bundle"); do
    echo "Installing ruby dependencies for $i"
    cd "$(dirname "$i")"
    bundle install --path vendor/bundle
    cd ${ROOT_DIR}
done
