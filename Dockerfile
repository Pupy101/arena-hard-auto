FROM python:3.10

WORKDIR /app

# create dirs and environments for each project
RUN mkdir /app/venvs && \
    mkdir -p /app/livecodebench && \ 
    python -m venv /app/venvs/livecodebench

# cp each project
COPY ./benches/LiveCodeBench /app/livecodebench/

# install projects in their respective venvs
RUN /app/venvs/livecodebench/bin/pip install --upgrade pip && \
    /app/venvs/livecodebench/bin/pip install pydantic-settings && \
    /app/venvs/livecodebench/bin/pip install -e livecodebench

CMD [ "bash" ]
