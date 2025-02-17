# [Fork Link](https://github.com/Pupy101/cruxeval/tree/giga)

---

# Table of context:
1. [Generation](#generation)
2. [Evaluation](#evaluation)
3. [Show](#show)

---

### Generation

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python run_api.py <ARGS>
```

Main CLI arguments:

- `--model` - name of model in API;
- `--parallel` - count threads for parallel requests to model;
- `--temperature` - posible values: `0.2`, `0.8` (`0.2` - for `pass@1` metrics and `0.8` for `pass@5`);
- `--mode` - mode of validation, `input` - model generate input for function by output and vice versa for `output`;
- `--cot` - bool flag for enable CoT in evaluation.

__Generations automaticaly saved in `/benches/ce/results/dump`.__


Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python run_api.py --model GigaChat --parallel 100 --temperature 0.2
```

---

### Evaluation

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python evaluate.py <ARGS>
```

Main CLI arguments:

- `--generations-path` - path to generations;
- `--scored-path` - optional parameter (path to save scored result).

__Scored generations automaticaly saved in `/benches/ce/results/eval`.__

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python evaluate.py --generations-path /benches/ce/results/dump/GigaChat_temp0.2_input/generations.json
```

### Show

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python read_results.py <ARGS>
```

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/cruxeval:/benches/ce/results -it <IMAGE> ce ce python read_results.py --eval-dir /benches/ce/results/eval
```
