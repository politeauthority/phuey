FROM python:3.7-slim-buster

VOLUME /app/
WORKDIR /app/
ADD ./ /app
ENV PHUEY_CONFIG=docker
ENV PHUEY_DB_HOST=redis
ENV PHUEY_DB_PORT=3306

# Install apk requirements
RUN apt-get update && \
    apt-get install -y \
        gcc \
        python-pip \
        python3-distutils \
        bash

# Install and build Phuey and dependencies
RUN pip3 install -r /app/requirements.txt
    # python3 /app/setup.py build && \
    # python3 /app/setup.py install

CMD cd /app/web && python3 app.py 5000
