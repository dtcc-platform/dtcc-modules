FROM python:3.8-alpine


COPY ../pubsub_client /
RUN pip install -r /pubsub_client/requirements.txt

COPY wrapper.py /wrapper.py

# install our custom tool
COPY dtcc_hello_world.py /dtcc_hello_world.py

# start pubsub client
RUN ["chmod", "+x", "/wrapper.py"]
ENTRYPOINT ["/wrapper.py"]

