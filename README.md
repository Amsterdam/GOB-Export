# GOB-Export

GOB Export contains the logic to export GOB data in various formats.

The primary goal of this component is to preserve the existing DIVA products.
This will allow for a migration to GOB that minimizes the impact for the existing users of DIVA output.

# Infrastructure

A running [GOB infrastructure](https://github.com/Amsterdam/GOB-Infra) and
[GOB API](https://github.com/Amsterdam/GOB-API)
is required to run this component.

# Docker

## Requirements

* docker-compose >= 1.17
* docker ce >= 18.03

## Run

```bash
docker-compose build
docker-compose up &

# Start a single import
docker exec gobexport python -m gobexport.start catalog collection file
# e.g. meetbouten meetbouten MBT_MEETBOUT.dat
```

## Tests

```bash
docker-compose -f src/.jenkins/test/docker-compose.yml build
docker-compose -f src/.jenkins/test/docker-compose.yml run test
```

# Local

## Requirements

* python >= 3.6

## Initialisation

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt
```

Or activate the previously created virtual environment

```bash
source venv/bin/activate
```

# Run

Start the service:

```bash
export $(cat .env | xargs)  # Copy from .env.example if missing
cd src
python -m gobexport
```

Start a single import in another window:

```bash
cd src
python -m gobexport.start catalog collection file
# e.g. meetbouten meetbouten MBT_MEETBOUT.dat
```

## Tests

Run the tests:

```bash
cd src
sh test.sh
```

# Remarks

The output files are placed on the configured objectstore under {CONTAINER_BASE}/{catalog}/{file}
CONTAINER_BASE default value is `distributie`.
It is recommended to change this value in development to `development/distributie` using the .env file.
