# [Fork Link](https://github.com/Pupy101/FastChat/tree/giga/fastchat/llm_judge)

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
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_api_answer.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--model` - name of model in API;
- `--parallel` - count of threads for parallel requesting.

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_api_answer.py --bench-name mt_bench --model GigaChat --parallel 10
```

---

### Judge

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_judgment.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--judge-model` - possible values: `gpt-4`;
- `--model-list` - names of models for judgement;
- `--parallel` - count of threads for parallel requesting.

Example for GigaChat in Advanced (fill variables for openai in `example.env`):

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_judgment.py --bench-name mt_bench --judge-model gpt-4 --model-list GigaChat --parallel 10
```

---

### Show result

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python show_result.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--judge-model` - possible values: `gpt-4`;
- `--model-list` - names of models.

Example:

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python show_result.py --bench-name mt_bench --judge-model gpt-4 --model-list GigaChat GigaChat-Pro
```

---

# Запуск через venv (без Docker)

## Настройка окружения


### 1) Создать и активировать виртуальное окружение

```bash
python3.11 -m venv .venvs/fc
source .venvs/fc/bin/activate
```

### 2) Обновить базовые инструменты

```bash
pip install -U pip setuptools wheel
```

### 3) Установить FastChat с нужными extras (model_worker, llm_judge)

Флаг --extra-index-url нужен для установки wheels PyTorch (CPU)

```bash
pip install benches/FastChat[model_worker,llm_judge] --extra-index-url https://download.pytorch.org/whl/cpu
```

### 4) Экспортируйте переменные окружения

```bash
set -a
source example.env
set +a
```

### 5) Перейти в директорию llm_judge и сделать симлинк на data

```bash
cd benches/FastChat/fastchat/llm_judge
ln -s ../../../../data/fastchat data || true
```

## Запуск

### Generation:

```bash
python gen_api_answer.py <ARGS>
```

Основные аргументы CLI: см в разделе [Generation](#generation)

Пример для GigaChat (предварительно экспортируйте нужные переменные окружения в разделе [Settings venv](#settings-venv)):

```bash
python gen_api_answer.py --bench-name mt_bench --model GigaChat --parallel 10
```

### Judge:

```bash
python gen_judgment.py <ARGS>
```

Основные аргументы CLI: см в разделе [Judge](#judge)

Пример (для `gpt-4` в роли судьи нужно экспортировать переменные окружения в разделе [Settings venv](#settings-venv) в exemple.env должен быть переменные для OpenAI):

```bash
python gen_judgment.py --bench-name mt_bench --judge-model gpt-4 --model-list GigaChat --parallel 10
```

### Show result:

```bash
python show_result.py <ARGS>
```

Основные аргументы CLI: см в разделе [Show result](#show-result)

Пример:

```bash
python show_result.py --bench-name mt_bench --judge-model gpt-4 --model-list GigaChat GigaChat-Pro
```
