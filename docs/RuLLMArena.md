# [Fork Link](https://github.com/Pupy101/ru_llm_arena/tree/giga)

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
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python gen_answer.py <ARGS>
```

Main CLI arguments:

- `--setting-file` - example config - [generate.yaml](../configs/ru-llm-arena/generate.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/ru-llm-arena/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and can change benchmark in settings [config](../configs/ru-llm-arena/generate.yaml)):

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python gen_answer.py --setting-file config/generate.yaml --endpoint-file config/endpoint.yaml
```

---

### Judge

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python gen_judgment.py <ARGS>
```

Main CLI arguments:

- `--setting-file` - example config - [judge.yaml](../configs/ru-llm-arena/judge.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/ru-llm-arena/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and fill creds for openai in [judge.yaml](../configs/ru-llm-arena/judge.yaml)):

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python gen_judgment.py --setting-file config/judge.yaml --endpoint-file config/endpoint.yaml
```

---

### Show result

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python show_result.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `arena-general-v0.1`;
- `--judge-name` - possible values: `gpt-4-1106-preview`;
- `--baseline` - baseline model `gpt-3.5-turbo-0125`.

Example:

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python show_result.py --bench-name arena-general-v0.1 --judge-name gpt-4-1106-preview --baseline gpt-3.5-turbo-0125
```

---

# Запуск через venv (без Docker)

Ниже — альтернатива запуску через локальное виртуальное окружение Python. Для списка аргументов и примеров используйте те же разделы: [Generation](#generation), [Judge](#judge), [Show result](#show-result).

## Настройка окружения

### запустить из корня репозитория

```bash
python3.11 -m venv .venvs/rla
source .venvs/rla/bin/activate
set -a; source example.env; set +a
cd benches/RuLLMArena
pip install --no-cache-dir -U pip setuptools wheel
pip install --no-cache-dir -r requirements.txt -r requirements-optional.txt
ln -sfn ../../configs/ru-llm-arena config
ln -sfn ../../data/ru-llm-arena data
```

Примечания:
- Файл `example.env` заполните своими значениями.

## Запуск

Команды ниже эквивалентны Docker-примерам, но выполняются в активном venv. Пути к конфигам и данным совпадают с теми, что указаны выше.

Команды выполняються из корня репозитория (venv активирован)

### Generation

```bash
python gen_answer.py <ARGS>
```

Основные аргументы CLI: см в разделе [Generation](#generation)

Пример: 

```bash
python gen_answer.py --setting-file config/generate.yaml --endpoint-file config/endpoint.yaml
```

### Judge — см. детали аргументов в разделе «Judge»

```bash
python gen_judgment.py <ARGS>
```

Основные аргументы CLI: см в разделе [Judge](#judge)

Пример:

```bash
python gen_judgment.py --setting-file config/judge.yaml --endpoint-file config/endpoint.yaml
```

### Show result

```bash
python show_result.py <ARGS>
```

Основные аргументы CLI: см в разделе [Show result](#show-result)

Пример:

```bash
python show_result.py --bench-name arena-general-v0.1 --judge-name gpt-4-1106-preview --baseline gpt-3.5-turbo-0125
```
