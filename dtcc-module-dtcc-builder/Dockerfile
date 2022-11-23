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

RUN git clone -b develop https://gitlab.com/dtcc-platform/dtcc-builder.git
RUN cd dtcc-builder && git submodule update --init --recursive
RUN cd dtcc-builder && mkdir build && cd build && cmake .. && make -j && make install

#RUN curl --output build.zip --location https://gitlab.com/dtcc-platform/dtcc-builder/-/jobs/artifacts/develop/download?job=build
#ADD build.zip /build.zip
#RUN unzip /build.zip

# Add /usr/local/lib into LD
RUN ldconfig /usr/local/lib

# Add user and change to user
RUN useradd -m $USER -G sudo && \
    echo "$USER:$USER" | chpasswd && \
    echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
ARG _uid
ARG gid
RUN usermod -u ${_uid} dtcc
RUN groupmod -g ${gid} dtcc

#RUN touch banner
#RUN ./createbanner.sh
#USER $USER

# Generate welcome message printed at login
#RUN touch banner
#RUN ./createbanner.sh
#COPY banner /
#COPY banner $HOME/.welcome
#COPY *docker/Welcome $HOME/.welcome
#RUN echo "cat $HOME/.welcome" >> $HOME/.bashrc

RUN mkdir /shared_data
RUN chown $USER:$USER /shared_data
RUN chown $USER:$USER /home/$USER

# Image setup
#FROM base as dev
#USER $USER
#ENTRYPOINT ["/bin/bash", "-l", "-c"]
#CMD ["/bin/bash", "-i"]


# Install wrapper
COPY dtcc-module-dtcc-builder/wrapper.py /wrapper.py
RUN ["chmod", "+x", "wrapper.py"]

# Install client
#COPY pubsub_client /pubsub_client
ADD pubsub_client /pubsub_client
RUN pip install -r /pubsub_client/requirements.txt
RUN chown $USER:$USER /pubsub_client
RUN chown $USER:$USER /wrapper.py

FROM base as dev
USER $USER

Start client
ENTRYPOINT ["/wrapper.py"]
# ENTRYPOINT ["/bin/bash", "-l", "-c"]
# CMD ["/bin/bash", "-i"]
