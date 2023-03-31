# syntax=docker/dockerfile:1
FROM amsterdam/gob_wheelhouse:3.9-bullseye as wheelhouse
MAINTAINER datapunt@amsterdam.nl


# Application stage.
FROM amsterdam/gob_baseimage:3.9-bullseye as application
MAINTAINER datapunt@amsterdam.nl

# Fill the wheelhouse.
COPY --from=wheelhouse /opt/wheelhouse /opt/wheelhouse

# Install export service in /app folder.
WORKDIR /app

# Install required Python packages.
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install --no-cache-dir \
	--find-links /opt/wheelhouse --requirement requirements.txt
RUN rm requirements.txt
# Wheelhouse cleanup.
RUN rm -rf /opt/wheelhouse

# Copy gobexport service module.
COPY gobexport gobexport

# Copy sftp.
COPY sftp sftp

# Copy public keys.
COPY keys/*.pub /keys/

USER datapunt
CMD ["uwsgi"]


# Development.
FROM application as development
USER root

RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Core.git
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install -e /app/GOB-Core
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Config.git
RUN pip install -e /app/GOB-Config
USER datapunt


# Test.
FROM application as test
USER root

RUN rm -rf /app/src/gobcore/tests
RUN rm -rf /app/src/gobconfig/tests

# Copy test module and tests.
COPY test.sh .flake8 .coveragerc pytest.ini ./
COPY tests tests

# Copy Jenkins files.
COPY .jenkins /.jenkins
RUN mkdir -m 2755 -p /app/shared/message_broker && chown -R datapunt.datapunt /app/shared

USER datapunt
