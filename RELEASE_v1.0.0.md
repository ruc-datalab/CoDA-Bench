# CoDA-Bench v1.0.0 Release

**Release Date**: June 8, 2026  
**Status**: ✅ Stable

## 🎉 First Public Release

We're thrilled to release CoDA-Bench v1.0.0, a benchmark for evaluating AI code agents on data-intensive analytical tasks!

## ✨ What's New

### 🐳 Secure Docker Evaluation
- **Isolated execution**: Agents run in sandboxed Docker containers
- **No answer leakage**: Agents cannot access benchmark ground truth
- **Network restricted**: Only LLM API endpoints accessible
- **Reproducible**: Same results across different environments

### 📦 Simple Installation
```bash
git clone https://github.com/ruc-datalab/CoDA-Bench.git
cd CoDA-Bench
pip install -e .
python scripts/setup_dataset.py --data-dir ./datasets
```

### 🤖 OpenHands Integration
- Pre-configured Docker image with OpenHands SDK
- Battle-tested on 1,009 data analysis tasks
- Works with any OpenAI-compatible API

### 📊 Comprehensive Dataset
- **1,009 tasks** across 31 Kaggle communities
- **119 hard tasks** for challenging evaluation
- **~980 files per task** requiring data discovery
- **~43 GB** of real-world datasets

## 🚀 Quick Start

```bash
# Build Docker image
cd docker && ./build_all.sh && cd ..

# Set API credentials
export LLM_API_KEY="your-key"

# Run evaluation (4 test instances)
python scripts/run_evaluation.py \
    --model gpt-5.5 \
    --instances 0 1 2 3 \
    --output results/test

# Score results
python -m coda_bench.cli evaluate \
    --pred results/test/predictions.jsonl \
    --gold datasets/coda_bench.json \
    --out results/test/scores.json
```

## 📈 Baseline Results

| System | Model | EA (Full) | EA (Hard) |
|--------|-------|-----------|-----------|
| Mini-SWE-Agent | GPT-5.5 | 61.1% | 49.6% |
| OpenHands | GPT-5.5 | 59.7% | 44.5% |
| Claude Code | Sonnet-4.6 | 53.8% | 42.9% |

## 🗺️ What's Next

**v1.1 (Coming Soon)**:
- Direct mode (no Docker) for quick testing
- Additional agents: Claude Code, Codex, Mini-SWE-Agent
- Better logging and progress tracking

## 📚 Documentation

- [README](README.md) - Overview and quick start
- [Docker Guide](docker/README.md) - Detailed Docker instructions
- [Quick Start](QUICKSTART.md) - 5-minute tutorial
- [Data Format](docs/data_format.md) - Dataset schema
- [Evaluation Protocol](docs/evaluation_protocol.md) - Metrics and scoring

## 🙏 Acknowledgments

- Kaggle community for 199 datasets
- OpenHands team for the agent SDK
- ICML 2026 reviewers for feedback

## 📧 Contact

- Issues: https://github.com/ruc-datalab/CoDA-Bench/issues
- Email: zhangshaolei98@ruc.edu.cn

---

**Happy benchmarking!** 🚀
