FROM python:3.8-slim-buster

# Install tool
COPY dtcc-module-hello-world/dtcc_hello_world.py /dtcc_hello_world.py

# Install wrapper
COPY dtcc-module-hello-world/tools.py /tools.py
COPY dtcc-module-hello-world/run.py /run.py
RUN ["chmod", "+x", "/run.py"]

# Install client
COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

# Start client
ENTRYPOINT ["/run.py"]
