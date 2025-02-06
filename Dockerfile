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

# Add helper script for environment activation
RUN echo '#!/bin/bash\nsource /benches/venvs/$1/bin/activate\ncd /benches/$2\nshift 2\nexec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ah", "ah"]
