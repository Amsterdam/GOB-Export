#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

export GOB_RUN_MODE=TEST
export COVERAGE_FILE=/tmp/.coverage

echo "Running tests"
coverage run --source=./gobexport -m pytest tests/

echo "Running coverage report"
coverage report --show-missing --fail-under=99

echo "Running style checks"
flake8
