# CoDA-Bench Package

Core evaluation utilities for CoDA-Bench.

## Installation

```bash
pip install -e .
```

## CLI Tools

After installation, two command-line tools are available:

### Evaluate Predictions

```bash
coda-bench-evaluate --pred predictions.jsonl --gold coda_bench.json --out results.json
```

### Validate Submission Format

```bash
coda-bench-validate --pred predictions.jsonl --gold coda_bench.json
```

## Python API

```python
from coda_bench import evaluate, load_tasks, load_predictions

# Load data
tasks = load_tasks('coda_bench.json')
predictions = load_predictions('predictions.jsonl')

# Evaluate
result = evaluate(tasks, predictions)

print(f"Exact Accuracy: {result.exact_accuracy:.2%}")
print(f"Numeric Accuracy: {result.numeric_accuracy:.2%}")

# Access detailed results
for instance in result.per_instance:
    print(f"Instance {instance['instance_id']}: {instance['exact_match']}")
```

## Modules

- `coda_bench.schema`: Data models (Task, Prediction)
- `coda_bench.evaluation`: Evaluation functions (evaluate, exact_match, numeric_match)
- `coda_bench.io`: I/O utilities (load_tasks, load_predictions, write_json)
- `coda_bench.cli`: Command-line interfaces
