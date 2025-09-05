# [Fork Link](https://github.com/Pupy101/arena-hard-auto/tree/giga)

---

# Table of context:
1. [Generation](#generation)
2. [Judge](#judge)
3. [Show result](#show-result)
4. [Запуск через venv (без Docker)](#запуск-через-venv-без-docker)
   - [Настройка окружения](#настройка-окружения)
   - [Запуск](#запуск)

---

### Generation

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_answer.py <ARGS>
```

Main CLI arguments:

- `--config-file` - example config - [generate.yaml](../configs/arena-hard-auto/arena-hard-v0.1.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/arena-hard-auto/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and `endpoint.yaml` and also use one of benchmark settings [config](../configs/arena-hard-auto/arena-hard-v*.yaml) `arena-hard-v0.1` &#8594; `arena-hard-v0.1-ru` &#8594; `arena-hard-v2.0`):

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_answer.py --config-file config/arena-hard-v*.yaml --endpoint-file config/endpoint.yaml
```

---

### Judge

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_judgment.py <ARGS>
```

Main CLI arguments:

- `--setting-file` - example config - [judge.yaml](../configs/arena-hard-auto/arena-hard-v*.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/arena-hard-auto/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and fill creds for openai in [endpoint.yaml](../configs/arena-hard-auto/endpoint.yaml)):

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_judgment.py --setting-file config/arena-hard-v*.yaml --endpoint-file config/endpoint.yaml
```

---

### Show result

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python show_result.py <ARGS>
```

Main CLI arguments:

- `--benchmark` - possible values: `arena-hard-v0.1`/`arena-hard-v0.1-ru`/`arena-hard-v2.0`;
- `--judge-names` - you can use list of values, example value: `gpt-4-1106-preview`;
- `--category` – For v2.0, the options are `hard_prompt creative_writing`, while for v0.1 and v0.1-ru, the corresponding names are `arena-hard-v0.1` and `arena-hard-v0.1-ru` respectively.

Example:

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python show_result.py --benchmark arena-hard-v0.1 --judge-names gpt-4-1106-preview --category arena-hard-v0.1
```

# Запуск через venv (без Docker)

Запускать нужно в корне проекта

## Настройка окружения

### 1) Создать и активировать venv

```bash
python3.11 -m venv .venvs/ah
source .venvs/ah/bin/activate
pip install -U pip setuptools wheel
```

### 2) Установить зависимости

```bash
pip install -r benches/arena-hard-auto/requirements.txt 
            -r benches/arena-hard-auto/requirements-optional.txt
```

### 3) Задать переменные окружения

```bash
set -a
source example.env
set +a
```

### 4) Привязать config и data к проектным путям

```bash
cd benches/arena-hard-auto
ln -s ../../configs/arena-hard-auto config || true
ln -s ../../data/arena-hard-auto data || true
```

## Запуск

Запускать нужно в этой директории:

```bash
cd benches/arena-hard-auto
```

### Generation

```bash
python gen_answer.py <ARGS>
```

Main CLI arguments: см выше в [Generation](#generation)

Example:

```bash
python gen_answer.py --setting-file config/generate.yaml --endpoint-file config/endpoint.yaml
```

### Judge

```bash
python gen_judgment.py <ARGS>
```

Main CLI arguments: см выше в [Judge](#judge)

Example:

```bash
python gen_judgment.py --setting-file config/judge.yaml --endpoint-file config/endpoint.yaml
```

### Show result

```bash
python show_result.py <ARGS>
```

Main CLI arguments: см выше в [Show result](#show-result)

Example:

```bash
python show_result.py --bench-name arena-hard-v0.1 --judge-name gpt-4-1106-preview --baseline gpt-4-0314
```
