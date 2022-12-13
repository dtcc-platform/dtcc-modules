# This is the base Dockerfile for DTCC Platform. This file is part
# of the dtcc-model repository (which resides as a submodule in all
# other repositories). Docker images for all other repositories are
# built on top of this base image by adding specific dependencies
# via the install_dependencies.sh script.

# Use Phusion base image (minimal Docker-friendly Ubuntu)
FROM phusion/baseimage:master as base

# Set some variables
ENV USER dtcc
ENV HOME /home/$USER


# Install libraries used by other repos
COPY dtcc-module-dtcc-builder/install_scripts/ /
#COPY docker/createbanner.sh /

RUN apt-get update && apt-get install -y locales  sudo 

RUN ./install_dependencies.sh

WORKDIR /
RUN git clone -b develop https://gitlab.com/dtcc-platform/dtcc-builder.git 
WORKDIR /dtcc-builder

RUN git submodule update --init --recursive
RUN mkdir build 
RUN cd build && cmake .. && make -j && make install


#RUN curl --output build.zip --location https://gitlab.com/dtcc-platform/dtcc-builder/-/jobs/artifacts/develop/download?job=build
#ADD build.zip /build.zip
#RUN unzip /build.zip

# Add /usr/local/lib into LD
RUN ldconfig /usr/local/lib

# Add user and change to user
RUN useradd -m $USER -G sudo && \
    echo "$USER:$USER" | chpasswd && \
    echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers


RUN mkdir /shared_data && cd /shared_data
RUN wget http://data.dtcc.chalmers.se:5001/demo-data-public -v -O dtcc-demo-data-public.tar.gz
RUN tar zxfv dtcc-demo-data-public.tar.gz
RUN chown -R $USER:$USER /shared_data
RUN chown $USER:$USER /home/$USER

# Install wrapper
COPY dtcc-module-dtcc-builder/tools.py /tools.py
COPY dtcc-module-dtcc-builder/run.py /run.py
RUN ["chmod", "+x", "/run.py"]

# Install pubsub client
COPY pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt

# Start client
ENTRYPOINT ["/run.py"]


