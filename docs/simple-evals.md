## simple-evals

### Generation

```bash
docker run \
  --env-file example.env \
  -it --rm \
  -v ./benches/simple-evals:/benches/se \
  -v ./data/simple-evals:/tmp \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  <IMAGE> se se python -m simple-evals.simple_evals <ARGS>
```

Основные аргументы:

- `--model` — идентификатор модели API (например, `gpt-4.1`)
- `--eval` — название теста (например, `mmlu`, `math`, `mgsm`, `humaneval`, `simpleqa`, `drop`, `gpqa`, `healthbench`)
- `--examples` — ограничение на число примеров (опционально)

Примеры:

```bash
docker run --env-file example.env -it --rm \
  -v ./benches/simple-evals:/benches/se \
  -v ./data/simple-evals:/tmp \
  <IMAGE> se se python -m simple-evals.simple_evals --eval mmlu --model gpt-4.1
```

```bash
docker run --env-file example.env -it --rm \
  -v ./benches/simple-evals:/benches/se \
  -v ./data/simple-evals:/tmp \
  <IMAGE> se se python -m simple-evals.simple_evals --eval humaneval --model gpt-4.1
```

### Запуск через виртуальное окружение (venv)

Для запуска без Docker нужно настроить виртуальное окружение. **Важно: выполняйте все команды из корня репозитория.**

```bash
# Команды выполняются из корня репозитория

# Создание venv с Python 3.11
python3.11 -m venv .hidden/venv_se

# Активация venv
source .hidden/venv_se/bin/activate

# Обновление pip
pip install --upgrade pip setuptools wheel

# Установка зависимостей
pip install openai anthropic pandas numpy blobfile jinja2 requests scipy tqdm tabulate gigachat

# Клонирование human-eval (для humaneval)
git clone https://github.com/openai/human-eval benches/human-eval

# Делаем импортируемым пакет simple_evals (создаем симлинк без дефиса)
ln -sf benches/simple-evals simple_evals

# Настройка путей для импорта (как в Docker)
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
echo "$(pwd)" > "$SITE_PACKAGES/onebutton_se_paths.pth"
echo "$(pwd)/benches/human-eval" >> "$SITE_PACKAGES/onebutton_se_paths.pth"

# Установка переменных окружения для API через файл
# Заполните example.env и выполните:
set -a
source example.env
set +a
```

Пример запуска после настройки:

```bash
python -m simple_evals.simple_evals --n-threads 1 --eval mmlu --model GigaChat
```

**Важно:** Результаты сохраняются в `/tmp` (как в Docker). Для удобства можно создать символическую ссылку: `ln -s ./data/simple-evals /tmp` или использовать переменную окружения, если она поддерживается кодом.

### Куда пишутся результаты

Скрипты `simple-evals` сохраняют отчёты и результаты в контейнерный путь `/tmp`. Благодаря бинд-монту `-v ./data/simple-evals:/tmp` файлы окажутся на хосте в `./data/simple-evals`.

Типичные файлы:

- HTML-отчёт: `*_*.html`
- Метрики: `*_*.json`
- Полные результаты: `*_*_allresults.json`

### Требования

В образе уже настроено окружение `se` с зависимостями, включая `openai`, `anthropic`, `pandas`, `numpy`, `blobfile` и `human-eval` (для `humaneval`). Для работы с API задайте переменные окружения `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.

