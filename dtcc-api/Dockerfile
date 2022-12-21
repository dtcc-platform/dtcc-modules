FROM python:3.9-slim-buster

# Copy config files from all modules and rename
COPY . /app/
RUN /bin/bash -c 'for file in app/**/*config.json ; do cp $file /${file////-}; done'
RUN rm -rf /app

# Install core
RUN pip install https://gitlab.com/dtcc-platform/dtcc-core/-/raw/develop/dist/dtcc_core-0.1.0-py3-none-any.whl

# Start client
ENTRYPOINT python3 -m core.api
