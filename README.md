# GOB-Export

GOB Export contains the logic to export GOB data in DIVA format

The primary goal of this component is to preserve the existing DIVA products.
This will allow for a migration to GOB that minimizes the impact for the existing users of DIVA output.

# Requirements

    * docker-compose >= 1.17
    * docker ce >= 18.03
    * python >= 3.6

# Installation

## Local

Create a virtual environment:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt

Or activate the previously created virtual environment

    source venv/bin/activate

### Dependencies

GOB Export depends on the GOB-API and GOB database

- To start a database instance follow the instructions in the GOB-Upload project.

If the GOB-Upload project has already been initialised then execute:

```bash
    cd ../GOB-Upload
    docker-compose up database &
```

- To start an API instance follow the instructions in the GOB-API project.

If the GOB-API project has already been initialised then execute:

```bash
    cd ../GOB-API/src
    python -m api
```

### Export

The export reads its data from the GOB API.
The address of the API can be specified in the API_HOST environment variable.
If no API_HOST variable is set, the default value for this variable is used:

    export API_HOST=http://127.0.0.1:5000

When running against a dockered API use:

    export API_HOST=http://127.0.0.1:8141/

To be able to connect to the objectstore some environment variables are needed.
Add the configuration for the objectstore connection to a .env file in the root of this repository,
based on the .env.example.

```bash
cp .env.example .env
```

Set the required shell variables:

```bash
export $(cat .env | xargs)
```

An export is run by the following commands:

```bash
cd src
python -m export catalog collection file    # e.g. python -m export meetbouten meetbouten MBT_MEETBOUT.dat
```

The file is placed on the configured objectstore under {CONTAINER_BASE}/{catalog}/{file}
CONTAINER_BASE default value is `distributie`. It is recommended to change this value in development to `development/distributie` using the .env file.

The catalogs and collections that have been implemented are:
- meetbouten
  - meetbouten
  - metingen
  - referentiepunten
  - rollagen

### Tests

Linting
```bash
    cd src
    flake8
```

Unit tests
```bash
    cd src
    pytest
```

Test coverage (100%)
```bash
    cd src
    export COVERAGE_FILE=/tmp/.coverage
    pytest --cov=api --cov-fail-under=100 tests/
```

## Docker

```bash
    docker-compose build
```

### Tests

```bash
    docker-compose -f src/.jenkins/test/docker-compose.yml build
    docker-compose -f src/.jenkins/test/docker-compose.yml run --rm test
```
