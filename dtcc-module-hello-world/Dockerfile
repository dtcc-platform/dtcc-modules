FROM python:3.8-slim-buster


COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

COPY dtcc-module-hello-world/wrapper.py /wrapper.py

# install our custom tool
COPY dtcc-module-hello-world/dtcc_hello_world.py /dtcc_hello_world.py

# start pubsub client
RUN ["chmod", "+x", "/wrapper.py"]
ENTRYPOINT ["/wrapper.py"]
