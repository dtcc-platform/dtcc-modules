FROM python:3.9-slim-buster

# Install tool
# ------------


# Install wrappers
COPY wrappers /wrappers

# Install core
RUN python3 -m pip install https://gitlab.com/dtcc-platform/dtcc-core/-/raw/develop/dist/dtcc_core-0.1.0-py3-none-any.whl


# Install Entrypoint
RUN apt update -y && apt install curl -y
RUN curl https://gitlab.com/dtcc-platform/dtcc-core/-/raw/develop/scripts/run-dtcc-modules.sh -o run-dtcc-modules.sh
RUN chmod +x /run-dtcc-modules.sh

# Wait for rabbitmq server
RUN curl https://github.com/vishnubob/wait-for-it/blob/81b1373f17855a4dc21156cfe1694c31d7d1792e/wait-for-it.sh -o /wait-for-it.sh
RUN chmod +x /wait-for-it.sh