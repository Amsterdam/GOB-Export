#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

export GOB_RUN_MODE=TEST
# Coverage 6: coverage run --data-file=/tmp/.coveragerc …
export COVERAGE_FILE=/tmp/.coverage

echo "Running style checks"
flake8

echo "Running tests"
coverage run --source=./gobexport -m pytest tests/

echo "Coverage report"
coverage report --show-missing --fail-under=100
