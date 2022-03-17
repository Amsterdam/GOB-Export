#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

export COVERAGE_FILE=/tmp/.coverage

echo "Running style checks"
flake8

echo "Running unit tests"
pytest tests/

echo "Running coverage tests"
pytest --cov=gobexport --cov-report html --cov-report term-missing  --cov-fail-under=100 tests/
