FROM python:3.9-slim-buster

# Copy config files from all modules and rename
COPY . /app/
RUN /bin/bash -c 'for file in app/**/*config.json ; do cp $file /${file////-}; done'
RUN rm -rf /app

# Install core
RUN pip install https://gitlab.com/dtcc-platform/dtcc-core/-/raw/develop/dist/dtcc_core-0.1.0-py3-none-any.whl

# Wait for rabbitmq server
RUN apt update -y && apt install curl -y
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/81b1373f17855a4dc21156cfe1694c31d7d1792e/wait-for-it.sh -o /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
