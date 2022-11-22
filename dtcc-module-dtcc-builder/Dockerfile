FROM phusion/baseimage:master as base

# Install dependencies
COPY dtcc-module-dtcc-builder/install_scripts/ /
RUN apt-get update && apt-get install -y locales  sudo
RUN ./install_dependencies.sh

# Install tool
RUN git clone -b develop https://gitlab.com/dtcc-platform/dtcc-builder.git
RUN cd dtcc-builder && git submodule update --init --recursive
RUN cd dtcc-builder && mkdir build && cd build && cmake .. && make -j && make install

# Install wrapper
COPY dtcc-module-dtcc-builder/wrapper.py /wrapper.py
RUN ["chmod", "+x", "/wrapper.py"]

# Install client
COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

# Start client
ENTRYPOINT ["/wrapper.py"]
