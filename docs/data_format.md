# Data Format

This document describes the data format for CoDA-Bench tasks and predictions.

## Task Format

Each task in `coda_bench.json` or `coda_bench_hard.json` is a JSON object with the following fields:

```json
{
  "instance_id": 0,
  "question": "What is the percentage of missing values in the RBC feature?",
  "answer": "38%",
  "answer_guidelines": "Answer must be a percentage integer formatted as 'XX%'.",
  "reference_code": "import pandas as pd\n...",
  "dataset": "ckdisease",
  "notebook": "eda-processing-tutorial",
  "release_community": "community_26"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | int | Unique task identifier (0 to N-1) |
| `question` | str | Natural language task description |
| `answer` | str | Gold answer for evaluation |
| `answer_guidelines` | str | Format requirements for the answer |
| `reference_code` | str | Reference Python solution |
| `dataset` | str | Original Kaggle dataset name |
| `notebook` | str | Source Kaggle notebook name |
| `release_community` | str | Community identifier (e.g., "community_26") |

### Field Usage

**For agent execution**:
- ✅ Provide: `question`, `answer_guidelines`
- ❌ Hide: `answer`, `reference_code`

**For evaluation**:
- Compare agent prediction against `answer`
- Use `reference_code` for debugging/analysis only

**For data loading**:
- Use `release_community` to determine which archive to extract
- Archive path: `archives/{release_community}.tar.zst`
- Data path: `data/{release_community}/full_community/`

## Prediction Format

Predictions must be submitted as a JSONL (JSON Lines) file where each line is a valid JSON object:

```jsonl
{"instance_id": 0, "prediction": "38%"}
{"instance_id": 1, "prediction": "150"}
{"instance_id": 2, "prediction": "0.75"}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | int | Task identifier (must match a task in the gold file) |
| `prediction` | str | Final answer from the agent |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `method` | str | Agent/method name (e.g., "GPT-5.5-CodeAgent") |
| `metadata` | dict | Additional information (see below) |

### Metadata Fields (Optional)

You can include any additional information in the `metadata` field:

```json
{
  "instance_id": 0,
  "prediction": "38%",
  "method": "MyAgent-v1",
  "metadata": {
    "files_accessed": ["data/community_26/full_community/ckdisease/CleanedKidneyDisease.csv"],
    "execution_time_seconds": 12.5,
    "code_generated": "import pandas as pd\n...",
    "num_retries": 2,
    "confidence": 0.95
  }
}
```

Common metadata fields:
- `files_accessed`: List of file paths used (required for DA calculation)
- `execution_time_seconds`: Time taken to solve the task
- `code_generated`: Final code executed
- `num_retries`: Number of attempts before success
- `confidence`: Agent's confidence in the answer

## Validation

Use the validation script to check your submission:

```bash
coda-bench-validate --pred predictions.jsonl --gold data/coda_bench.json
```

The validator checks:
- ✅ File is valid JSONL format
- ✅ Each line is valid JSON
- ✅ Required fields are present
- ✅ `instance_id` values match the gold file
- ✅ No duplicate `instance_id` values
- ✅ No extra `instance_id` values not in gold

## Answer Format Guidelines

The `answer_guidelines` field specifies the expected format. Common patterns:

### Percentages
```
Answer must be a percentage integer formatted as 'XX%'.
Example: "42%"
```

### Numbers
```
Answer must be an integer.
Example: "150"
```

### Floating-point
```
Answer must be a decimal number with 2 decimal places.
Example: "3.14"
```

### Categorical
```
Answer must be one of: 'Yes', 'No', 'Unknown'.
Example: "Yes"
```

### Lists
```
Answer must be a comma-separated list of values.
Example: "value1, value2, value3"
```

**Important**: Always format your answer according to the `answer_guidelines` to maximize your exact match score.

## Data Community Structure

After extracting an archive, the directory structure is:

```
data/
└── community_26/
    └── full_community/
        ├── dataset1/
        │   ├── file1.csv
        │   ├── file2.json
        │   └── ...
        ├── dataset2/
        │   └── ...
        └── ...
```

Each community contains:
- Multiple Kaggle datasets (subdirectories)
- Various file types: CSV, JSON, TXT, Excel, images, etc.
- Semantic similarity: datasets within a community are related by topic

## File Access Tracking

For Discovery Accuracy (DA) calculation, track all files your agent accesses:

```python
import os
from pathlib import Path

accessed_files = []

def track_file_access(filepath):
    """Track when the agent accesses a file."""
    accessed_files.append(str(Path(filepath).resolve()))

# Example: wrapping pandas read_csv
original_read_csv = pd.read_csv
def tracked_read_csv(*args, **kwargs):
    if args:
        track_file_access(args[0])
    return original_read_csv(*args, **kwargs)
pd.read_csv = tracked_read_csv
```

Include tracked files in your prediction metadata:

```json
{
  "instance_id": 0,
  "prediction": "38%",
  "metadata": {
    "files_accessed": [
      "/path/to/data/community_26/full_community/ckdisease/CleanedKidneyDisease.csv"
    ]
  }
}
```

## Example Complete Prediction

```json
{
  "instance_id": 0,
  "prediction": "38%",
  "method": "GPT-5.5-CodeAgent",
  "metadata": {
    "files_accessed": [
      "data/community_26/full_community/ckdisease/CleanedKidneyDisease.csv"
    ],
    "execution_time_seconds": 15.3,
    "code_generated": "import pandas as pd\nimport numpy as np\n\nfile_path = 'data/community_26/full_community/ckdisease/CleanedKidneyDisease.csv'\ndata = pd.read_csv(file_path)\n\nif 'Unnamed: 0' in data.columns:\n    data.drop('Unnamed: 0', axis=1, inplace=True)\n\nmissing = data.isna().sum()\ntotal_rows = data.shape[0]\nrbc_missing_percentage = (missing['Red Blood Cells'] / total_rows) * 100\n\nprint(f\"{int(rbc_missing_percentage)}%\")",
    "model": "gpt-5.5-turbo",
    "temperature": 0.2,
    "max_tokens": 8000
  }
}
```

## Questions?

For questions about the data format:
- Check the [evaluation protocol](evaluation_protocol.md)
- Open an issue on [GitHub](https://github.com/ruc-datalab/CoDA-Bench/issues)
- Email: zhangshaolei98@ruc.edu.cn
