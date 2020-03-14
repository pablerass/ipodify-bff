#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export FLASK_APP=ipodify-bff.app:app
export FLASK_ENV=development
source $DIR/env

pushd $DIR >> /dev/null
flask run
popd