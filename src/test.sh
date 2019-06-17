#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

echo "Running style checks"
flake8

echo "Running unit tests"
pytest tests/

echo "Running coverage tests"
export COVERAGE_FILE=/tmp/.coverage
pytest --cov=gobexport --cov-report html --cov-fail-under=96 tests/
