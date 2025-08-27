# [Fork Link](https://github.com/Pupy101/arena-hard-auto/tree/giga)

---

# Table of context:
1. [Generation](#generation)
2. [Judge](#judge)
3. [Show result](#show-result)

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
