# Aider Benchmark

[Fork Link](https://github.com/Aider-AI/aider)

---

## Table of Contents:
1. [Overview](#overview)
2. [Supported Benchmarks](#supported-benchmarks)
3. [Setup](#setup)
4. [Running Benchmarks](#running-benchmarks)
5. [Configuration](#configuration)
6. [Results](#results)
7. [GigaChat Integration](#gigachat-integration)
8. [Examples](#examples)

---

## Overview

The Aider benchmark evaluates how effectively AI coding assistants can translate natural language coding requests into executable code that passes unit tests. It provides an end-to-end evaluation of not just the LLM's coding ability, but also its capacity to edit existing code and format those edits so that Aider can save them to local source files.

The benchmark is based on the [Exercism](https://github.com/exercism/python) coding exercises and evaluates the complete workflow from natural language request to working code.

## Supported Benchmarks

### 1. Polyglot Benchmark
- **Description**: Evaluates coding assistance across multiple programming languages
- **Based on**: Exercism coding exercises
- **Metrics**: Pass rate, syntax errors, indentation errors, test timeouts
- **Languages**: Python, JavaScript, Java, C++, and more

### 2. SWE Bench
- **Description**: Software engineering benchmark for real-world coding tasks
- **Status**: Integration planned
- **Metrics**: Code quality, functionality, test coverage

### 3. SWE Bench Lite
- **Description**: Lightweight version of SWE Bench
- **Status**: Integration planned
- **Metrics**: Simplified evaluation metrics

## Setup

### Prerequisites
- Docker environment with one-button-benches
- API keys for supported models (OpenAI, Anthropic, GigaChat)
- Polyglot benchmark data

### Environment Variables
Set the following environment variables in your `example.env` file:

```bash
# OpenAI API (for GPT models)
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1  # Optional, for custom endpoints

# Anthropic API (for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key

# GigaChat API (automatically configured)
# No additional setup required - uses lightweight-gigachat module
```

## Running Benchmarks

### Basic Command Structure

```bash
docker/aider/run_benchmark.sh <run-name> <model-name> <run-type> <threads>
```

### Main CLI Arguments

- "run-name" - name of current run for example run-giga-max
- "model-name" - model for current run for example gigachat/GigaChat-Max 
- "run-type" - type of current run for example whole
- "threads" - specifies how many exercises to benchmark in parallel. Start with a single thread if you are working out the kinks on your benchmarking setup or working with a new model, etc. Once you are getting reliable results, you can speed up the process by running with more threads. 10 works well against the OpenAI APIs.
- "exercises-dir" - exercises for current run -  for example polyglot-benchmark

### Running Polyglot Benchmark

#### Example for gigachat/GigaChat-Max:
```bash
docker/aider/run_benchmark.sh run-giga-max gigachat/GigaChat-Max whole 10 polyglot-benchmark
```

### Running with Custom Settings

You can modify the benchmark behavior by editing the configuration files at ./configs/aider


## Results

### Viewing Results

```bash
docker/aider/run_stats.sh <run-directory>
```

- "run-directory" - directory of run for view stats - it's will present at directory data/aider

### Result Format

Results are stored in YAML format with the following structure:

```yaml
- dirname: 2025-08-11-07-23-01--run-giga-max
  test_cases: 225
  model: gigachat/GigaChat-Max
  edit_format: whole
  commit_hash: 414e13e
  pass_rate_1: 2.2
  pass_rate_2: 2.2
  pass_num_1: 5
  pass_num_2: 5
  percent_cases_well_formed: 100.0
  error_outputs: 295
  num_malformed_responses: 0
  num_with_malformed_responses: 0
  user_asks: 0
  lazy_comments: 0
  syntax_errors: 0
  indentation_errors: 0
  exhausted_context_windows: 0
  prompt_tokens: 0
  completion_tokens: 0
  test_timeouts: 0
  total_tests: 225
  command: aider --model gigachat/GigaChat-Max
  date: 2025-08-11
  versions: 0.86.1.dev
  seconds_per_case: 0.0
  total_cost: 0.0000

costs: $0.0000/test-case, $0.00 total, $0.00 projected
```

## Examples

### Quick Start - Polyglot Benchmark

1. **Setup environment**:
   Copy example.env and fill in your API keys

2. **Run benchmark**:
   ```bash
   docker/aider/run_benchmark.sh run-giga-max gigachat/GigaChat-Max whole 10 polyglot-benchmark
   ```

3. **View results**:
   ```bash
   docker/aider/run_stats.sh <run-directory>
   ```
   
   "run-directory" - fill with your run directory name it will present at directory data/aider
  