# Leaderboard Submission Guide

Submit your CoDA-Bench results to the official leaderboard!

## Submission Requirements

### 1. Run Official Evaluation

Evaluate your agent on both benchmark variants:

```bash
# Full benchmark
coda-bench-evaluate --pred predictions_full.jsonl --gold data/coda_bench.json --out results_full.json

# Hard subset
coda-bench-evaluate --pred predictions_hard.jsonl --gold data/coda_bench_hard.json --out results_hard.json
```

### 2. Prepare Submission File

Create a JSON file with your results:

```json
{
  "submission_id": "unique-identifier",
  "method": "YourAgent-v1.0",
  "model": "GPT-5.5-turbo",
  "organization": "Your Organization",
  "results": {
    "full": {
      "execution_accuracy": 0.611,
      "discovery_accuracy": 0.523,
      "n_tasks": 1009,
      "n_correct": 616
    },
    "hard": {
      "execution_accuracy": 0.496,
      "discovery_accuracy": 0.487,
      "n_tasks": 119,
      "n_correct": 59
    }
  },
  "metadata": {
    "date": "2026-06-08",
    "paper": "https://arxiv.org/abs/xxxx.xxxxx",
    "code": "https://github.com/yourorg/youragent",
    "contact": "your@email.com",
    "notes": "Any additional information about your approach"
  }
}
```

### 3. Submit

**Option A: GitHub PR**
1. Fork the CoDA-Bench repository
2. Add your submission file to `leaderboard/submissions/your_method.json`
3. Create a pull request

**Option B: Web Form**
- Visit [https://coda-bench.github.io/leaderboard](https://coda-bench.github.io/leaderboard)
- Fill out the submission form
- Upload your results file

## Leaderboard Categories

### Main Leaderboard
- Ranked by EA (Full)
- Displays EA and DA for both full and hard subsets

### Specialized Categories
- **Open-source models**: Models with publicly available weights
- **Closed-source APIs**: Commercial API services
- **Domain-specific**: Agents specialized for data analysis

## Ranking Criteria

Primary ranking: **Execution Accuracy (Full)**

Tiebreakers (in order):
1. Execution Accuracy (Hard)
2. Discovery Accuracy (Full)
3. Discovery Accuracy (Hard)
4. Submission date (earlier is better)

## Verification

Submissions may be subject to verification:
- Reproducibility check
- Code review (if available)
- Trajectory log inspection

## Anonymous Submissions

You may submit anonymously during paper review:
- Use a pseudonymous identifier
- Omit paper/code links
- Reveal identity after publication

## Questions?

- Check [FAQ](https://coda-bench.github.io/faq)
- Open an issue on [GitHub](https://github.com/ruc-datalab/CoDA-Bench/issues)
- Email: zhangshaolei98@ruc.edu.cn
