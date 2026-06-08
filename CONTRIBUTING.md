# Contributing to CoDA-Bench

Thank you for your interest in contributing to CoDA-Bench! We welcome contributions from the community.

## Ways to Contribute

### 🐛 Reporting Bugs
- Check if the issue already exists in [GitHub Issues](https://github.com/ruc-datalab/CoDA-Bench/issues)
- Use the bug report template
- Include reproducible examples and error messages

### 💡 Suggesting Enhancements
- Open an issue with the "enhancement" label
- Clearly describe the proposed feature and its benefits
- Discuss implementation approaches

### 📝 Improving Documentation
- Fix typos, clarify instructions, add examples
- Update outdated information
- Translate documentation to other languages

### 🧪 Adding Baseline Agents
- Implement your agent following the evaluation protocol
- Include clear setup instructions
- Share results and analysis

### 📊 Sharing Results
- Submit evaluation results to the leaderboard
- Share interesting findings or error analysis
- Contribute trajectory logs for research

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CoDA-Bench.git
   cd CoDA-Bench
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

5. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Quality

### Style Guide
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for functions and classes

### Linting and Formatting
```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type checking
mypy coda_bench/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=coda_bench
```

## Pull Request Process

1. **Update documentation** if you change functionality
2. **Add tests** for new features
3. **Ensure tests pass** and code is formatted
4. **Write clear commit messages**:
   ```
   feat: Add support for custom metrics
   fix: Correct numeric matching tolerance
   docs: Update evaluation protocol
   ```

5. **Submit PR** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

6. **Address review feedback** promptly

## Leaderboard Submissions

To submit results to the leaderboard:

1. Run evaluation on both full and hard subsets
2. Create a JSON file with your results:
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
       "contact": "your@email.com",
       "paper": "https://arxiv.org/abs/xxxx.xxxxx",
       "code": "https://github.com/yourorg/youragent"
     }
   }
   ```

3. Submit via:
   - GitHub PR to `leaderboard/submissions/`
   - [Leaderboard form](https://coda-bench.github.io/leaderboard)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and constructive
- Welcome newcomers
- Focus on what is best for the community
- Show empathy towards others

## Questions?

- Open a [GitHub Discussion](https://github.com/ruc-datalab/CoDA-Bench/discussions)
- Email: zhangshaolei98@ruc.edu.cn

Thank you for contributing to CoDA-Bench! 🎉
