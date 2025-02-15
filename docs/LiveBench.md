# [Fork Link](https://github.com/Pupy101/LiveBench/tree/giga)

---

# Table of context:
1. [Generation](#generation)
2. [Judge](#judge)
3. [Show result](#show-result)

---

### Generation

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python gen_api_answer.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `live_bench`;
- `--model` - name of model in API;
- `--parallel` - count of threads for parallel requesting;
- `--resume` - do not generate answers for questions that have already been generated;
- `--retry-failures` - retry generating answers for questions that have failed in the past.

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python gen_api_answer.py --bench-name live_bench --model GigaChat --parallel 20
```

---

### Judge

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python gen_ground_truth_judgment.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `live_bench`;
- `--model` - name of model for judgement;
- `--parallel` - count of threads for parallel requesting.

Example:

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python gen_ground_truth_judgment.py --bench-name live_bench --model GigaChat --parallel 100
```

---

### Show result

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python show_livebench_result.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `live_bench`;
- `--model-list` - names of models.

Example:

```bash
docker run --env-file example.env -v ./data/live_bench:/benches/lb/livebench/data -it <IMAGE> lb lb/livebench python show_livebench_result.py --bench-name live_bench --model-list GigaChat
```
