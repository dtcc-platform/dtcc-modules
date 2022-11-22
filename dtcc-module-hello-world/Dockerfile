FROM python:3.8-slim-buster

# Install tool
COPY dtcc-module-hello-world/dtcc_hello_world.py /dtcc_hello_world.py

# Install wrapper
COPY dtcc-module-hello-world/wrapper.py /wrapper.py
RUN ["chmod", "+x", "/wrapper.py"]

# Install client
COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

# Start client
ENTRYPOINT ["/wrapper.py"]
