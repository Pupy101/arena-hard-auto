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

- `--setting-file` - example config - [generate.yaml](../configs/arena-hard-auto/generate.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/arena-hard-auto/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and can change benchmark in settings [config](../configs/arena-hard-auto/generate.yaml) `arena-hard-v0.1` &#8594; `arena-hard-v0.1-ru`):

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_answer.py --setting-file config/generate.yaml --endpoint-file config/endpoint.yaml
```

---

### Judge

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_judgment.py <ARGS>
```

Main CLI arguments:

- `--setting-file` - example config - [judge.yaml](../configs/arena-hard-auto/judge.yaml);
- `--endpoint-file` - example config - [endpoint.yaml](../configs/arena-hard-auto/endpoint.yaml).

Example for GigaChat in Advanced (fill variables in `example.env` and fill creds for openai in [judge.yaml](../configs/arena-hard-auto/judge.yaml)):

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python gen_judgment.py --setting-file config/judge.yaml --endpoint-file config/endpoint.yaml
```

---

### Show result

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python show_result.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `arena-hard-v0.1`/`arena-hard-v0.1-ru`;
- `--judge-model` - possible values: `gpt-4-1106-preview`;
- `--baseline` - baseline model `gpt-4-0314`.

Example:

```bash
docker run --env-file example.env -v ./configs/arena-hard-auto:/benches/ah/config -v ./data/arena-hard-auto/:/benches/ah/data -it <IMAGE> ah ah python show_result.py --bench-name arena-hard-v0.1 --judge-model gpt-4-1106-preview --baseline gpt-4-0314
```
