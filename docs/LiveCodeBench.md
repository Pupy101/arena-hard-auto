# Table of context:
1. [Evaluation](#evaluation)

---

### Evaluation

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
docker run --env-file example.env -v ./data/live_code_bench:/benches/lcb/output -it <IMAGE> lcb lcb python -m lcb_runner.runner.main <ARGS>
```
