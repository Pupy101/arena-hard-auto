# [Fork Link](https://github.com/Pupy101/repoqa/tree/giga)

---

# Table of context:
1. [Evaluation](#evaluation)

---

### Evaluation

```bash
docker run --env-file example.env -v ./data/repoqa:/benches/rqa/results -it <IMAGE> rqa rqa repoqa.search_needle_function <ARGS>
```

Main CLI arguments:

- `--model` - name of model in API;
- `--backend` - backend for API requests, possible values: `giga`, `openai`, `anthropic` and etc;
- `--code_context_size` - length of input context (default `16384`).

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/repoqa:/benches/rqa/results -it <IMAGE> rqa rqa repoqa.search_needle_function --model "GigaChat" --backend giga --code_context_size 20480
```
