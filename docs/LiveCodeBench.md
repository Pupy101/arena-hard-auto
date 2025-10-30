# [Fork Link](https://github.com/Pupy101/LiveCodeBench/tree/giga)

---

# Table of context:
1. [Evaluation](#evaluation)

---

### Evaluation

#### Запуск в virtual environment

1) Create and activate venv:

```bash
python3.11 -m venv .venvs
source .venvs/bin/activate
```

2) Install LiveCodeBench with dependencies (datasets is pinned to <3.0 to support HF script datasets used by LCB):

```bash
pip install -e benches/LiveCodeBench
# If you installed datasets>=3 by accident:
pip install "datasets<3"
```

3) Run the runner locally:

```bash
( cd /home/ainosov/work/repositories/onebuttonbenches/benches/LiveCodeBench \
  && set -a \
  && source example.env \
  && set +a \
  && OBM_FUNCTION_FORMAT_VERSION=v3 python -m benches.LiveCodeBench.lcb_runner.runner.main \
       --model GigaChat \
       --scenario codegeneration \
       --evaluate \
       --release_version release_v5 \
       --multiprocess 10 )
```

#### Запуск в Docker

```bash
docker run --env-file example.env -v ./data/live_code_bench:/benches/lcb/output -it <IMAGE> lcb lcb python -m lcb_runner.runner.main <ARGS>
```

Main CLI arguments:

- `--model` - name of model in API;
- `--scenario` possible values: `codegeneration`, `selfrepair`, `testoutputprediction`, `codeexecution`;
- `--evaluate` - flag for evaluating predicts;
- `--release_version` - benchmark release, possible values: `release_v5`;
- `--multiprocess` - count of processes for parallel requesting.

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/live_code_bench:/benches/lcb/output -it <IMAGE> lcb lcb python -m lcb_runner.runner.main --model GigaChat --scenario codegeneration --evaluate --release_version release_v5
```

Подробнее про CLI arguments:

[Readme.md](https://github.com/Pupy101/LiveCodeBench/tree/giga)

Например, 25 сентября 2025 года сюда добавлена поддержка release_v6, для запуска указываете соответственно в `--release_version`
