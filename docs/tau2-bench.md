### Tau2-Bench

---

### Prerequisites

- Copy the file `example.env` and fill in all required variables (API keys, etc.) before running. These values are injected into the container with `--env-file`.
- In addition to the variables in `example.env`, you may set the following environment variables for GigaChat support (if needed):
  - `GIGA_USER`
  - `GIGA_PASSWORD`
  - `GIGA_MODEL`


---

### Run evaluation

Use the container's tau2 virtual environment via the entrypoint:

```bash
docker run \
  --add-host=host.docker.internal:host-gateway \
  -e TAU2_DATA_DIR=/tau2-data \
  -v <ABSOLUTE_PATH_TO>/onebuttonbenches/benches/tau2-bench/data:/tau2-data \
  --env-file <PATH_TO_ENV_FILE> \
  -it <IMAGE> tau2 tau2 \
  tau2 run --domain <DOMAIN> \
  --agent-llm <AGENT_LLM> \
  --user-llm <USER_LLM> \
  --num-trials 1 \
  --max-concurrency 1 \
```

Notes:

- If you build Docker image by following OBB guide, then its name is `obb`.
- Supported domains: `retail`, `airline`, `telecom`.
- `--agent-llm`: A model to evaluate (any OpenAI model or any model containing a word "giga" in any register)
- `--user-llm`: This model should be fixed among all experiments. Usually, a strong model from OpenAI is used. 
- You can add `--num-tasks 1` to test evaluation on 1 sample
- In `OPENAI_API_BASE` use `host.docker.internal` instead of `localhost`

Sample test run (replace <ABSOLUTE_PATH_TO> with your actual path):

```bash
docker run \
  --add-host=host.docker.internal:host-gateway \
  -e TAU2_DATA_DIR=/tau2-data \
  -v <ABSOLUTE_PATH_TO>/onebuttonbenches/benches/tau2-bench/data:/tau2-data \
  --env-file .env -it obb \
  tau2 tau2 \
  tau2 run --domain airline \
  --agent-llm GigaChat \
  --user-llm gpt-4.1 \
  --num-trials 1 \
  --num-tasks 1
```

### Viewing results (tau2-bench includes a powerful interactive console viewer)

```bash
docker run \
  --add-host=host.docker.internal:host-gateway \
  -e TAU2_DATA_DIR=/tau2-data \
  -v <ABSOLUTE_PATH_TO>/onebuttonbenches/benches/tau2-bench/data:/tau2-data \
  -it obb tau2 tau2 \
  tau2 view
```
