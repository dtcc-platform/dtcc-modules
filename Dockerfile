FROM python:3.8-slim-buster

# Install api
COPY **/*module-config.json /
#COPY dtcc-modules-conf.json /dtcc-modules-conf.json
COPY api.py /api.py
RUN ["chmod", "+x", "/api.py"]

# Install client
COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

# Start client
ENTRYPOINT ["/api.py"]
