# [Fork Link](https://github.com/Pupy101/evalplus/tree/giga)

---

# Table of context:
1. [Evaluation](#evaluation)

---

### Evaluation

```bash
docker run --env-file example.env -v ./data/evalplus:/benches/ep/evalplus_results -it <IMAGE> ep ep evalplus.evaluate <ARGS>
```

Main CLI arguments:

- `--model` - name of model in API;
- `--dataset` possible values: `humaneval`, `mbpp`;
- `--backend` - backend for API requests, possible values: `giga`, `openai`, `anthropic` and etc;
- `--greedy` - bool flag for greedy benchmark;
- `--i_just_wanna_run` - bool flag for rerun tests from cached responses;
- `--parallel` - count processes for testing generations.

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/evalplus:/benches/ep/evalplus_results -it <IMAGE> ep ep evalplus.evaluate --model GigaChat --dataset humaneval --backend giga --greedy
```
