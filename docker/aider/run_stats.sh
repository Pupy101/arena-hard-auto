#!/bin/bash

# Скрипт для запуска benchmark с --stats параметром
# Использование: ./run_stats.sh [путь_к_директории]

# Проверяем, передан ли аргумент
if [ $# -eq 0 ]; then
    echo "Ошибка: Необходимо указать путь к директории с результатами benchmark"
    echo "Использование: $0 <путь_к_директории>"
    echo "Пример: $0 tmp.benchmarks/2025-08-10-20-34-29--run-giga-max/"
    exit 1
fi

BENCHMARK_DIR="$1"

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
       -it aider ad ad python ./benchmark/benchmark.py --stats /benchmarks/$BENCHMARK_DIR