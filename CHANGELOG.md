# Changelog

All notable changes to CoDA-Bench will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-08

### Added
- **Docker-based evaluation** with OpenHands agent
  - Secure isolation preventing access to benchmark answers
  - Network restrictions (only LLM API accessible)
  - Resource limits (memory, CPU, timeout)
- **Full dataset** (1,009 tasks) and **hard subset** (119 tasks)
- **One-command dataset setup** with automatic download and extraction
- Comprehensive documentation:
  - Docker evaluation guide
  - Quick start guide
  - API reference
  - Data format specification
- Evaluation metrics (Execution Accuracy, Discovery Accuracy)
- JSONL prediction format for easy scoring
- Parallel evaluation support (multi-worker)

### Supported
- **Agent**: OpenHands (via Docker)
- **Models**: Any LLM with OpenAI-compatible API
  - GPT-5.5, GPT-4, GPT-3.5
  - Claude models (via compatible endpoints)
  - Custom models (via base URL)

### Known Limitations
- Only Docker mode supported in v1.0
- Direct mode (no Docker) not yet implemented
- Only OpenHands agent officially supported

### Roadmap
- **v1.1** (Coming Soon):
  - Direct evaluation mode (no Docker required)
  - Claude Code agent with Docker support
  - Codex agent with Docker support
  - Mini-SWE-Agent with Docker support
  - Improved logging and progress tracking

## [0.1.0] - 2026-05-15 (Internal Beta)

### Added
- Initial benchmark design
- Data collection from Kaggle
- Baseline agent implementations
- Preliminary evaluation results

---

## Version History

- **1.0.0** (2026-06-08): Public release with Docker evaluation
- **0.1.0** (2026-05-15): Internal beta testing

## Upgrade Guide

### From 0.x to 1.0.0

The public 1.0 release focuses on Docker-based evaluation only:

**Breaking Changes:**
- Removed direct mode from initial release (coming in v1.1)
- Removed multi-agent support (only OpenHands in v1.0)
- Simplified API: single `run_evaluation.py` script

**Migration:**
1. Rebuild Docker images: `cd docker && ./build_all.sh`
2. Update evaluation commands to use simplified API
3. See [QUICKSTART.md](QUICKSTART.md) for new usage

**What's the same:**
- Dataset format unchanged
- Prediction format unchanged
- Evaluation metrics unchanged
- Community data structure unchanged
