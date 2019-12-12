# GOB-Export

GOB Export contains the logic to export GOB data in various formats.

The primary goal of this component is to preserve the existing DIVA products.
This will allow for a migration to GOB that minimizes the impact for the existing users of DIVA output.

# Infrastructure

A running [GOB infrastructure](https://github.com/Amsterdam/GOB-Infra) and
[GOB API](https://github.com/Amsterdam/GOB-API)
is required to run this component.

## Secure data

In order to access secure data over the GOB API you need to define environment variables:
- KEYCLOAK_URL
- KEYCLOAK_CLIENT_ID
- KEYCLOAK_SECRET

# Docker

## Requirements

* docker-compose >= 1.17
* docker ce >= 18.03

## Run

```bash
docker-compose build
docker-compose up &
```

## Tests

```bash
docker-compose -f src/.jenkins/test/docker-compose.yml build
docker-compose -f src/.jenkins/test/docker-compose.yml run test
```

# Local

## Requirements

* python >= 3.6
* gdal-dev

See the docker file for help on installing gdal

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

Optional: Set environment if GOB-Export should connect to Objectstore:

```bash
export $(cat .env | xargs)  # Copy from .env.example if missing
```

Start the service:

```bash
cd src
python -m gobexport
```

## Tests

Run the tests:

```bash
cd src
sh test.sh
```

# Remarks

## Trigger exports

Exports are triggered by the GOB-Workflow module. See the GOB-Workflow README for more details

## Configuration

The exports are highly data driven. The configurations are stored in gobexport/exporter/config.

## Objectstore exports

The output files are placed on the configured objectstore under {CONTAINER_BASE}/{catalog}/{file}
CONTAINER_BASE default value is `distributie`.

It is recommended to change this value in development to **`development`** in the .env file.
