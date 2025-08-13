FROM python:3.10

WORKDIR /benches

# Create virtual environments directory
RUN mkdir -p /benches/venvs

# Arena-Hard-Auto
COPY ./benches/arena-hard-auto /benches/ah
RUN python -m venv /benches/venvs/ah && \
    /benches/venvs/ah/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/ah/bin/pip install --no-cache-dir \
    -r ah/requirements.txt -r ah/requirements-optional.txt

# CRUXEval
COPY ./benches/cruxeval /benches/ce
RUN python -m venv /benches/venvs/ce && \
    /benches/venvs/ce/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/ce/bin/pip install --no-cache-dir -r ce/requirements.txt

# EvalPlus
COPY ./benches/evalplus /benches/ep
RUN python -m venv /benches/venvs/ep && \
    /benches/venvs/ep/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/ep/bin/pip install --no-cache-dir ep/'[perf]' && \
    sh -c 'echo 0 > /proc/sys/kernel/perf_event_paranoid'

# MT-Bench
COPY ./benches/FastChat /benches/fc
RUN python -m venv /benches/venvs/fc && \
    /benches/venvs/fc/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/fc/bin/pip install --no-cache-dir fc/'[model_worker,llm_judge]' \
    --extra-index-url https://download.pytorch.org/whl/cpu

# LiveBench
COPY ./benches/LiveBench /benches/lb
RUN python -m venv /benches/venvs/lb && \
    /benches/venvs/lb/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/lb/bin/pip install --no-cache-dir lb/ \
    --extra-index-url https://download.pytorch.org/whl/cpu

# LiveCodeBench
COPY ./benches/LiveCodeBench /benches/lcb
RUN python -m venv /benches/venvs/lcb && \
    /benches/venvs/lcb/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/lcb/bin/pip install --no-cache-dir lcb/ \
    --extra-index-url https://download.pytorch.org/whl/cpu

# RepoQA
COPY ./benches/repoqa /benches/rqa
RUN python -m venv /benches/venvs/rqa && \
    /benches/venvs/rqa/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/rqa/bin/pip install --no-cache-dir rqa/

# RuLLMArena
COPY ./benches/RuLLMArena /benches/rla
RUN python -m venv /benches/venvs/rla && \
    /benches/venvs/rla/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/rla/bin/pip install --no-cache-dir \
    -r rla/requirements.txt -r rla/requirements-optional.txt

# Aider
# Aider - используем git clone вместо COPY
RUN git clone -b giga https://github.com/ArtiomNosov/aider.git /benches/ad

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    software-properties-common \
    cmake \
    libboost-all-dev \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    ca-certificates-java \
    openjdk-17-jdk \
    libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3.11 -m venv /benches/venvs/ad && \
    /benches/venvs/ad/bin/pip install --no-cache-dir -U pip setuptools wheel && \
    /benches/venvs/ad/bin/pip install --no-cache-dir -r ad/requirements.txt && \
    /benches/venvs/ad/bin/pip install --no-cache-dir -r ad/requirements/requirements-dev.txt

# Install Go with architecture detection
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        GOARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        GOARCH="arm64"; \
    else \
        false; \
    fi && \
    curl -L "https://golang.org/dl/go1.21.5.linux-$GOARCH.tar.gz" -o go.tar.gz && \
    tar -C /usr/local -xzf go.tar.gz && \
    rm go.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Install Rust
ADD https://sh.rustup.rs /tmp/rustup.sh
RUN chmod +x /tmp/rustup.sh && /tmp/rustup.sh -y && rm /tmp/rustup.sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Node.js and dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /npm-install && \
    cd /npm-install && \
    npm init -y && \
    npm install \
    jest \
    @babel/core@7.25.2 \
    @exercism/babel-preset-javascript@0.2.1 \
    @exercism/eslint-config-javascript@0.6.0 \
    @types/jest@29.5.12 \
    @types/node@20.12.12 \
    babel-jest@29.6.4 \
    core-js@3.37.1 \
    eslint@8.49.0

# COPY . /aider
RUN /benches/venvs/ad/bin/pip install --no-cache-dir --upgrade pip uv
RUN /benches/venvs/ad/bin/pip install --no-cache-dir -e /benches/ad[dev]
RUN git config --global --add safe.directory /benches/ad
RUN git clone https://github.com/Aider-AI/polyglot-benchmark .data/aider/polyglot-benchmark


# Add helper script for environment activation
RUN echo '#!/bin/bash\nsource /benches/venvs/$1/bin/activate\ncd /benches/$2\nshift 2\nexec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ah", "ah"]
