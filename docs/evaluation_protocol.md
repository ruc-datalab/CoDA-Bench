# Evaluation Protocol

This document describes the official evaluation protocol for CoDA-Bench.

## Overview

CoDA-Bench evaluates AI agents on their ability to solve data-intensive analytical tasks by jointly assessing:
- **Data Intelligence**: Discovering relevant files among hundreds of candidates
- **Code Intelligence**: Writing correct code to solve the task

## Metrics

### 1. Execution Accuracy (EA)

**Definition**: Percentage of tasks where the agent's final answer matches the gold answer.

**Matching Rules**:
- **Exact Match**: Normalized string comparison (case-insensitive, whitespace-normalized)
- **Numeric Match**: For answers containing numbers, compare extracted numeric values with tolerance of 1e-6

**Formula**:
```
EA = (# correct answers) / (# total tasks)
```

### 2. Discovery Accuracy (DA)

**Definition**: Percentage of tasks where the agent discovered all required data files.

**Calculation**:
- Compare files accessed by the agent against gold target files
- A task is correct only if the agent found **all** required files
- Accessing extra files does not penalize the score

**Formula**:
```
DA = (# tasks with all files found) / (# total tasks)
```

## Evaluation Setup

### 1. Sandbox Environment

Each task must be evaluated in an isolated Linux sandbox:

```bash
# Create sandbox directory
mkdir -p sandbox/instance_{instance_id}

# Extract community data
tar --use-compress-program='zstd -d' -xf archives/{release_community}.tar.zst -C sandbox/instance_{instance_id}/

# The data will be at: sandbox/instance_{instance_id}/data/{release_community}/full_community/
```

### 2. Agent Execution

Provide the agent with:
- ✅ The task `question` from the dataset
- ✅ The `answer_guidelines` specifying the format
- ✅ Access to the sandbox environment

**Do NOT provide**:
- ❌ The `answer` (gold label)
- ❌ The `reference_code`
- ❌ The `data_path` or file names
- ❌ The target files to use

### 3. Answer Submission

The agent should submit a single string answer:

```json
{
  "instance_id": 0,
  "prediction": "38%"
}
```

Optional fields for analysis:
- `method`: Agent name/version
- `metadata`: Additional info (files used, execution time, etc.)

### 4. Scoring

Use the official evaluation script:

```python
from coda_bench import evaluate, load_tasks, load_predictions

tasks = load_tasks('coda_bench.json')
predictions = load_predictions('predictions.jsonl')
result = evaluate(tasks, predictions)

print(f"Execution Accuracy: {result.exact_accuracy:.2%}")
```

## Benchmark Variants

### Full Benchmark (1,009 tasks)

- Tests general data analysis capabilities
- Average environment: 980 files, ~1.4 GB
- Report as **EA (Full)** and **DA (Full)**

### Hard Subset (119 tasks)

- Filtered for complexity:
  - Data complexity: ≥2 target files required
  - Code complexity: >30 effective lines in reference solution
- Average environment: 1,422 files, ~2.1 GB
- Report as **EA (Hard)** and **DA (Hard)**

## Leaderboard Submission

To submit results to the leaderboard:

1. **Run evaluation** on both full and hard subsets
2. **Format results** as JSON:
```json
{
  "method": "YourAgent-v1",
  "model": "GPT-5.5",
  "ea_full": 0.611,
  "ea_hard": 0.496,
  "da_full": 0.523,
  "da_hard": 0.487,
  "metadata": {
    "date": "2026-06-08",
    "contact": "your@email.com"
  }
}
```

3. **Submit** via GitHub PR or [leaderboard form](https://coda-bench.github.io/leaderboard)

## Best Practices

### ✅ Do

- Use isolated sandboxes for each task
- Allow agents to explore the file system freely
- Record all files accessed for DA calculation
- Use the official evaluation script
- Report both EA and DA metrics

### ❌ Don't

- Provide hints about file locations
- Allow agents to access gold answers
- Reuse sandboxes across tasks (potential data leakage)
- Modify the evaluation script
- Cherry-pick results or filter tasks

## Reproducibility

To ensure reproducibility:

1. **Document your setup**:
   - Agent implementation details
   - Model name and version
   - Hyperparameters (temperature, max tokens, etc.)
   - Sandbox configuration

2. **Share trajectory logs** (optional):
   - Commands executed
   - Files accessed
   - Code generated
   - Final answers

3. **Use version-controlled data**:
   - Specify dataset version
   - Use official archives from HuggingFace

## Questions?

For clarifications about the evaluation protocol:
- Open an issue on [GitHub](https://github.com/ruc-datalab/CoDA-Bench/issues)
- Email: zhangshaolei98@ruc.edu.cn
