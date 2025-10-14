#!/bin/bash

# All supported models are listed in https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/SUPPORTED_MODELS.md

IMAGE=obb
ENV_FILE=benches/gorilla/berkeley-function-call-leaderboard/.env
BFCL_PROJECT_ROOT=benches/gorilla/berkeley-function-call-leaderboard
NUM_THREADS=5

export BFCL_PROJECT_ROOT=$BFCL_PROJECT_ROOT

# GigaChat-2-MAX--IFT-FC,GigaChat-2-MAX--PROD-FC, claude-3-7-sonnet-20250219-FC, gpt-4o-mini-2024-07-18-FC
MODELS="gpt-4o-mini-2024-07-18-FC"

TEST_CATEGORIES="\
simple_python,simple_java,simple_javascript,multiple,\
live_simple,live_multiple,\
live_relevance,\
irrelevance,live_irrelevance,\
memory_kv,memory_vector,memory_rec_sum,\
multi_turn_base,multi_turn_miss_func,multi_turn_miss_param,multi_turn_long_context"

docker run \
    --add-host=host.docker.internal:host-gateway \
    --env-file $ENV_FILE \
    -v ./benches/gorilla/berkeley-function-call-leaderboard:/benches/gorilla/berkeley-function-call-leaderboard \
    $IMAGE gorilla/berkeley-function-call-leaderboard gorilla/berkeley-function-call-leaderboard \
    bash -c "bfcl generate --model '$MODELS' --test-category '$TEST_CATEGORIES' --num-threads $NUM_THREADS && bfcl evaluate --test-category '$TEST_CATEGORIES' --partial-eval"  # set --partial-eval if needed
