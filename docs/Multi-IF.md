# [Fork Link](https://github.com/ArtiomNosov/Multi-IF/tree/giga)

---

# Table of context:
1. [Setup](#setup)
2. [Evaluation](#api-based-evaluation)

---

### Evaluation

Run the benchmark using API calls to various LLM providers:

```bash
docker run --env-file example.env -v ./data/Multi-IF:/benches/mif/data -it <IMAGE> mif mif python multi_turn_instruct_following_eval_api.py <ARGS>
```

Main CLI arguments:

- `--max_workers` - number of parallel workers (default: 5)
- `--api_model_name` - model name to evaluate
- `--input_data_csv` - path to the input CSV file
- `--max_new_tokens` - maximum number of tokens to generate
- `--steps` - evaluation steps to run (e.g., 1 2 3)

Example for GigaChat:

```bash
docker run --env-file example.env -v ./data/Multi-IF:/benches/mif/data -it <IMAGE> mif mif python multi_turn_instruct_following_eval_api.py --max_workers 5 --api_model_name gigachat --input_data_csv data/input/multiIF_20241018.csv --max_new_tokens 1024 --steps 1 2 3
```

The results of the benchmark run can be found in the `data/Multi-IF/results` folder.

---

### GigaChat Integration

The Multi-IF benchmark now supports GigaChat models through the lightweight-gigachat module. To use GigaChat models ensure your `example.env` file contains the necessary GigaChat API credentials.
