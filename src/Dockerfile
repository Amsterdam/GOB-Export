FROM amsterdam/python:3.9-buster as application
MAINTAINER datapunt@amsterdam.nl

# Install GDAL
RUN apt-get update
RUN apt-get install -y libgdal-dev

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install api service in /app folder
WORKDIR /app

# Install required Python packages
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobexport service module
COPY gobexport gobexport

# Copy sftp test
COPY sftp sftp

# Copy public keys
COPY keys/*.pub /keys/

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

CMD ["uwsgi"]

FROM application as development

RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Core.git
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install -e /app/GOB-Core
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Config.git
RUN pip install -e /app/GOB-Config


FROM application as test
RUN rm -rf /app/src/gobcore/tests
RUN rm -rf /app/src/gobconfig/tests

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

# Copy jenkins files
COPY .jenkins /.jenkins

#RUN mkdir -p /app/shared/message_broker && chown datapunt /app/shared
