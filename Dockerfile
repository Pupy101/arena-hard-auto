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
    /benches/venvs/ce/bin/pip install --no-cache-dir ce/requirements.txt

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

# Add helper script for environment activation
RUN echo '#!/bin/bash\nsource /benches/venvs/$1/bin/activate\ncd /benches/$2\nshift 2\nexec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ah", "ah"]
