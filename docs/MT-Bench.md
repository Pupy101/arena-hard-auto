# Table of context:
1. [Generation](#generation)
2. [Judge](#judge)
3. [Show result](#show-result)

---

### Generation

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_api_answer.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--model` - name of model in API;
- `--parallel` - count of threads for parallel requesting.

Example for GigaChat in Advanced (fill variables in `example.env`):

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_api_answer.py --bench-name mt_bench --model GigaChat --parallel 10
```

---

### Judge

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_judgment.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--judge-model` - possible values: `gpt-4`;
- `--model-list` - names of models for judgement;
- `--parallel` - count of threads for parallel requesting.

Example for GigaChat in Advanced (fill variables for openai in `example.env`):

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python gen_judgment.py --bench-name mt_bench --judge-model gpt-4 --model-list GigaChat --parallel 10
```

---

### Show result

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it <IMAGE> fc fc/fastchat/llm_judge python show_result.py <ARGS>
```

Main CLI arguments:

- `--bench-name` - possible values: `mt_bench`/`mt_bench-ru`;
- `--judge-model` - possible values: `gpt-4`;
- `--model-list` - names of models.

Example:

```bash
docker run --env-file example.env -v ./data/fastchat:/benches/fc/fastchat/llm_judge/data -it 7d8bd6e07934 fc fc/fastchat/llm_judge python show_result.py --bench-name mt_bench-ru --judge-model gpt-4 --model-list GigaChat GigaChat-Pro
```
