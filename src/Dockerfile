FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

# Install api service in /app folder
WORKDIR /app

# Install required Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobuploadservice module
COPY api api

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

CMD python3 -m api
