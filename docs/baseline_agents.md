# Baseline Agents

This document describes baseline agent implementations for CoDA-Bench.

## Overview

We provide reference implementations for several baseline agents to help you get started:

1. **Random Agent**: Submits random answers (baseline floor)
2. **Oracle Agent**: Has access to target files (oracle ceiling for DA)
3. **Simple LLM Agent**: Basic code-generation agent
4. **Advanced Agents**: State-of-the-art implementations

## Quick Start

```bash
# Install baseline dependencies
pip install -e ".[baselines]"

# Run a baseline agent
python baselines/run_simple_agent.py --model gpt-4 --split full --output predictions.jsonl
```

## Baseline Results

| Agent | Model | EA (Full) | EA (Hard) | DA (Full) | DA (Hard) |
|-------|-------|-----------|-----------|-----------|-----------|
| Mini-SWE-Agent | GPT-5.5 | **61.1%** | **49.6%** | 52.3% | 48.7% |
| Codex CLI | GPT-5.5 | 60.3% | 47.9% | 51.7% | 47.2% |
| OpenHands | GPT-5.5 | 59.7% | 44.5% | 48.9% | 43.1% |
| Claude Code | Sonnet-4.6 | 53.8% | 42.9% | 47.2% | 41.8% |

## Implementation Guide

### 1. Agent Interface

All agents should implement this interface:

```python
from pathlib import Path
from typing import Protocol

class Agent(Protocol):
    def solve_task(self, question: str, data_dir: Path) -> str:
        """Solve a task and return the answer.
        
        Args:
            question: Natural language task description
            data_dir: Path to the data community directory
            
        Returns:
            Final answer as a string
        """
        ...
```

### 2. Sandbox Setup

Create isolated environments for each task:

```python
import tempfile
import shutil
from pathlib import Path

def setup_sandbox(community_id: str, data_root: Path) -> Path:
    """Create a sandbox for task execution."""
    sandbox = Path(tempfile.mkdtemp(prefix=f"coda_bench_{community_id}_"))
    data_path = data_root / community_id / "full_community"
    
    # Symlink data into sandbox
    (sandbox / "data").symlink_to(data_path)
    
    return sandbox

def cleanup_sandbox(sandbox: Path):
    """Remove sandbox after execution."""
    shutil.rmtree(sandbox)
```

### 3. Example: Simple LLM Agent

```python
import openai
from pathlib import Path

class SimpleLLMAgent:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.client = openai.OpenAI()
    
    def solve_task(self, question: str, data_dir: Path) -> str:
        # List available files
        files = list(data_dir.rglob("*"))
        file_list = "\n".join(f"- {f.relative_to(data_dir)}" for f in files[:100])
        
        # Create prompt
        prompt = f"""You are a data analysis assistant. 

Question: {question}

Available files in data directory:
{file_list}

Write Python code to solve this task and print the final answer.
"""
        
        # Generate code
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        code = response.choices[0].message.content
        
        # Execute code (simplified - use proper sandboxing in production)
        exec_globals = {"data_dir": str(data_dir)}
        exec(code, exec_globals)
        
        # Extract answer from output
        return exec_globals.get("answer", "")
```

### 4. File Discovery Strategies

**Strategy 1: Keyword Matching**
```python
def find_files_by_keywords(data_dir: Path, question: str) -> list[Path]:
    keywords = extract_keywords(question)
    candidates = []
    for file in data_dir.rglob("*.csv"):
        if any(kw.lower() in file.name.lower() for kw in keywords):
            candidates.append(file)
    return candidates
```

**Strategy 2: Content Inspection**
```python
import pandas as pd

def find_relevant_files(data_dir: Path, question: str) -> list[Path]:
    candidates = []
    for csv_file in data_dir.rglob("*.csv"):
        try:
            df = pd.read_csv(csv_file, nrows=5)
            if matches_schema(df.columns, question):
                candidates.append(csv_file)
        except Exception:
            pass
    return candidates
```

**Strategy 3: LLM-based Discovery**
```python
def llm_discover_files(data_dir: Path, question: str, llm) -> list[Path]:
    file_list = "\n".join(str(f.relative_to(data_dir)) for f in data_dir.rglob("*"))
    
    prompt = f"""Which files are most relevant to answer this question?

Question: {question}

Available files:
{file_list}

Return a JSON list of the most relevant file paths."""
    
    response = llm.generate(prompt)
    return parse_file_paths(response, data_dir)
```

## Contributing Your Agent

We welcome contributions of new baseline implementations!

1. Create a new file in `baselines/your_agent.py`
2. Implement the agent interface
3. Add documentation and usage instructions
4. Submit a PR with evaluation results

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Resources

- [OpenHands](https://github.com/All-Hands-AI/OpenHands): Open-source code agent
- [SWE-agent](https://github.com/princeton-nlp/SWE-agent): Software engineering agent
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT): Autonomous GPT-4 agent

## Questions?

- Open an issue on [GitHub](https://github.com/ruc-datalab/CoDA-Bench/issues)
- Email: zhangshaolei98@ruc.edu.cn
