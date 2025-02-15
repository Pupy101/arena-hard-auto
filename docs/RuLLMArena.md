# [Fork Link](https://github.com/Pupy101/ru_llm_arena/tree/giga)

---

# Table of context:
1. [Generation](#generation)
2. [Judge](#judge)
3. [Show result](#show-result)

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
- `--judge-model` - possible values: `gpt-4-1106-preview`;
- `--baseline` - baseline model `gpt-3.5-turbo-0125`.

Example:

```bash
docker run --env-file example.env -v ./configs/ru-llm-arena:/benches/rla/config -v ./data/ru-llm-arena/:/benches/rla/data -it <IMAGE> rla rla python show_result.py --bench-name arena-general-v0.1 --judge-model gpt-4-1106-preview --baseline gpt-3.5-turbo-0125
```
