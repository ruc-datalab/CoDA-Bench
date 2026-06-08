---
license: mit
task_categories:
- question-answering
- code-generation
language:
- en
tags:
- code
- data-analysis
- jupyter
- kaggle
- benchmark
- agent-evaluation
- data-science
size_categories:
- 1K<n<10K
pretty_name: CoDA-Bench
---

# CoDA-Bench: Can Code Agents Handle Data-Intensive Tasks?

[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/XXXX.XXXXX)
[![code](https://img.shields.io/badge/GitHub-CoDA--Bench-black.svg?logo=github)](https://github.com/ruc-datalab/CoDA-Bench)
[![homepage](https://img.shields.io/badge/%F0%9F%8C%90%20Homepage%20-CoDA--Bench-blue.svg)](https://coda-bench.github.io/)
[![leaderboard](https://img.shields.io/badge/%F0%9F%8F%86%20Leaderboard%20-CoDA--Bench-orange.svg)](https://coda-bench.github.io/leaderboard)

> **Authors**: **[Yuxin Zhang](https://github.com/yuxinzhang), [Ju Fan*](http://iir.ruc.edu.cn/~fanj/), [Meihao Fan](https://scholar.google.com/citations?user=9RTm2qoAAAAJ), [Shaolei Zhang](https://zhangshaolei1998.github.io/), [Xiaoyong Du](http://info.ruc.edu.cn/jsky/szdw/ajxjgcx/jsjkxyjsx1/js2/7374b0a3f58045fc9543703ccea2eb9c.htm)**

**CoDA-Bench** (Code and Data-intensive Benchmark) is the first benchmark to jointly evaluate **code intelligence** and **data intelligence** of AI agents in realistic data-intensive environments.

Unlike existing benchmarks that provide oracle data directly, CoDA-Bench requires agents to:
- 🔍 **Discover relevant data** among hundreds of semantically similar files
- 🗂️ **Navigate complex file hierarchies** in a Linux sandbox environment  
- 🔗 **Integrate information** from multiple heterogeneous data sources
- 💻 **Generate correct code** for data-driven analytical tasks

## 📊 Dataset Overview

- **Full Benchmark**: 1,009 tasks across 31 communities (`coda_bench.json`)
- **Hard Subset**: 119 challenging tasks across 15 communities (`coda_bench_hard.json`)
- **Source Data**: 199 Kaggle datasets from 267 notebooks
- **Scale**: Average 980 files per environment (~43 GB total compressed)

## 🏆 Benchmark Results

Current state-of-the-art (as of paper publication):

| System | Model | EA (Full) | EA (Hard) |
|--------|-------|-----------|-----------|
| Mini-SWE-Agent | GPT-5.5 | **61.1%** | **49.6%** |
| Codex CLI | GPT-5.5 | 60.3% | 47.9% |
| OpenHands | GPT-5.5 | 59.7% | 44.5% |
| Claude Code | Sonnet-4.6 | 53.8% | 42.9% |

## 📚 Citation

```bibtex
@inproceedings{zhang2026codabench,
  title={CODA-BENCH: Can Code Agents Handle Data-Intensive Tasks?},
  author={Zhang, Yuxin and Fan, Ju and Fan, Meihao and Zhang, Shaolei and Du, Xiaoyong},
  booktitle={Proceedings of the 43rd International Conference on Machine Learning},
  year={2026},
  organization={PMLR}
}
```

More information refer to [CoDA-Bench's Repo](https://github.com/ruc-datalab/CoDA-Bench)
