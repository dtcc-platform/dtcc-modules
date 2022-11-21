FROM python:3.8-slim-buster

COPY ../pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

COPY wrapper.py /wrapper.py

# install our custom tool
COPY dtcc_hello_world.py /dtcc_hello_world.py

# start pubsub client

