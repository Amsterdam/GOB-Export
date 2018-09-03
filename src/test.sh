#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

echo "Running style checks"
flake8

echo "Running unit tests"
pytest

echo "Running coverage tests"
export COVERAGE_FILE=/tmp/.coverage
pytest --cov=export --cov-fail-under=100 tests/
