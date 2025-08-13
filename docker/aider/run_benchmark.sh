#!/bin/bash

# Скрипт для запуска benchmark с параметрами модели и упражнений
# Использование: ./run_benchmark.sh [имя_запуска] [модель] [формат_редактирования] [количество_потоков] [директория_упражнений]

# Проверяем количество аргументов
if [ $# -lt 5 ]; then
    echo "Ошибка: Необходимо передать все параметры"
    echo "Использование: $0 <имя_запуска> <модель> <формат_редактирования> <количество_потоков> <директория_упражнений>"
    echo "Пример: $0 run-giga-max gigachat/GigaChat-Max whole 10 polyglot-benchmark"
    exit 1
fi

RUN_NAME="$1"
MODEL="$2"
EDIT_FORMAT="$3"
THREADS="$4"
EXERCISES_DIR="$5"

docker run \
       --env-file example_my.env \
       -it --rm \
       --memory=12g \
       --memory-swap=12g \
       --add-host=host.docker.internal:host-gateway \
       -v ./benches/aider:/aider \
       -v ./configs/aider:/benches/ad/config \
       -v ./data/aider:/benchmarks \
       -e HISTFILE=/benchmarks/.bash_history \
       -e PROMPT_COMMAND='history -a' \
       -e HISTCONTROL=ignoredups \
       -e HISTSIZE=10000 \
       -e HISTFILESIZE=20000 \
       -e AIDER_DOCKER=1 \
       -e AIDER_BENCHMARK_DIR=/benchmarks \
       -it aider ad ad python ./benchmark/benchmark.py $RUN_NAME --model $MODEL --edit-format $EDIT_FORMAT --threads $THREADS --exercises-dir $EXERCISES_DIR --read-model-settings /benches/ad/config/configs/aider/.aider.conf.yml
