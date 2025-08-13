#!/bin/bash

docker run \
       --env-file example_my.env \
       -it --rm \
       --memory=12g \
       --memory-swap=12g \
       --add-host=host.docker.internal:host-gateway \
       -v ./benches/aider:/aider \
       -v ./configs/aider:/benches/ad/config \
       -v ./data/aider/:/benchmarks \
       -e HISTFILE=/benchmarks/.bash_history \
       -e PROMPT_COMMAND='history -a' \
       -e HISTCONTROL=ignoredups \
       -e HISTSIZE=10000 \
       -e HISTFILESIZE=20000 \
       -e AIDER_DOCKER=1 \
       -e AIDER_BENCHMARK_DIR=/benchmarks \
       aider \
       bash
