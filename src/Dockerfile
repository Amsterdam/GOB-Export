FROM amsterdam/docker_python:latest
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
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobexport service module
COPY gobexport gobexport

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

CMD ["python", "-m", "gobexport"]
