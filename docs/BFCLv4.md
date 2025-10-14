# BFCL v4

# [Fork Link](https://github.com/Skripkon/gorilla)

1. Copy `.env.example` to `.env` and fill it credetentials to evaluate GigaChat and other models.

```bash
cd onebuttonbenches/benches
cp gorilla/berkeley-function-call-leaderboard/.env.example gorilla/berkeley-function-call-leaderboard/.env
```

2. Build the universal Docker image
```bash
cd onebuttonbenches
docker build --build-arg HOST_UID=$(id -u) --build-arg HOST_GID=$(id -g) -t obb .
```

3. Then run the benchmark from `onebuttonbenches/`
```bash
docker/BFCLv4/./run_benchmark.sh
```

4. Viewing Results

- Generated outputs can be found in `onebuttonbenches/benches/gorilla/berkeley-function-call-leaderboard/result`
- Evaluation metrics are available in `onebuttonbenches/benches/gorilla/berkeley-function-call-leaderboard/score`

5. BONUS: Build HTML tables to compare the performance of two evaluated models (in diff format):

```bash
python3 benches/gorilla/berkeley-function-call-leaderboard/bfcl_eval/scripts/build_diff_table.py \
    --results-dir benches/gorilla/berkeley-function-call-leaderboard/score/data_overall.csv \
    --model-old "GigaChat 2 MAX (PROD)" \
    --model-new "GigaChat 2 MAX (IFT)" \
    --display-old "Giga 28.2" \
    --display-new "Giga 30.1" \
    --output "Giga_28.2_VS_Giga_30.1.html"
```

*Note*: 
- The values for `--model-old` and `--model-new` should be taken from `benches/gorilla/berkeley-function-call-leaderboard/score/data_overall.csv`
- The values for `--display-old` and `--display-new` can be anything you choose.
