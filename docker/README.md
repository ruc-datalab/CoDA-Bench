# Docker-based Evaluation

Docker-based evaluation provides **secure isolation** to prevent agents from accessing benchmark answers or other unauthorized data.

## Why Docker?

### Security Benefits
- **Data Isolation**: Agent can only access `/data` (community data), not the full filesystem
- **Network Control**: Prevents downloading external packages that might leak information
- **Resource Limits**: CPU and memory constraints prevent resource abuse
- **Clean Environment**: Each task runs in a fresh, isolated container

### Two Evaluation Modes

| Mode | Description | Use Case | Security |
|------|-------------|----------|----------|
| **Direct** | Agent runs on host with data mounted | Quick testing, debugging | ⚠️ Low |
| **Docker** | Agent runs in isolated container | Official evaluation, benchmarking | ✅ High |

**Recommendation**: Use Docker mode for reproducible, secure evaluation.

## Quick Start

### 1. Build Docker Images

```bash
# Build all agent images
cd docker
./build_all.sh

# Or build specific agent
cd docker/openhands
docker build -t codabench-openhands:latest .
```

### 2. Run Docker Evaluation

```bash
# Using evaluation script (recommended)
python scripts/run_evaluation.py \
    --agent openhands \
    --model gpt-5.5 \
    --mode docker \
    --output results/openhands_docker \
    --workers 4

# Or use docker-specific script
python scripts/run_evaluation_docker.py \
    --agent openhands \
    --model gpt-5.5 \
    --output results/test
```

## Available Docker Images

### OpenHands
```bash
cd docker/openhands
docker build -t codabench-openhands:latest .
```

**Features**:
- Network isolation with `network-lock.sh`
- Read-only data mount (`/data:ro`)
- Resource limits (8GB RAM, 2 CPUs)
- Pre-installed: pandas, numpy, scikit-learn, matplotlib

**Security**:
- Disables `wget`, `apt-get`, `apt`
- Offline pip configuration
- Only `/workspace` is writable
- LLM API access via proxy only

### Claude Code
```bash
cd docker/claude-code
docker build -t codabench-claude-code:latest .
```

**Features**:
- Claude Code CLI pre-installed
- Isolated workspace
- Data-only access

### Codex
```bash
cd docker/codex
docker build -t codabench-codex:latest .
```

**Features**:
- Codex CLI environment
- Python 3.10+ with data science libraries
- Network-restricted

### Mini-SWE-Agent
```bash
cd docker/miniswe
docker build -t codabench-miniswe:latest .
```

## Docker Architecture

```
Host Machine
├── datasets/communities/community_1/  (read-only)
└── results/instance_0/
    ├── workspace/                     (read-write)
    └── output/                        (read-write)

Docker Container
├── /data          -> mounted from datasets/communities/
├── /workspace     -> mounted from results/instance_0/workspace/
└── /trajectories  -> mounted from results/instance_0/output/
```

### Mount Strategy
- `/data` - **Read-only**: Community data, agent cannot modify
- `/workspace` - **Read-write**: Agent's working directory
- `/trajectories` - **Read-write**: Output logs and results

## Configuration

### Resource Limits

Default limits (can be adjusted in run scripts):
- **Memory**: 8GB
- **CPUs**: 2 cores
- **Timeout**: 600 seconds per task

Edit `docker/<agent>/run_task.sh`:
```bash
docker run \
    --memory=16g \      # Increase memory
    --cpus=4 \          # More CPU cores
    ...
```

### Network Isolation

Network access is **disabled by default** to prevent:
- Downloading solutions from the internet
- Accessing external APIs (except LLM API)
- Installing unauthorized packages

**LLM API Access**: Configured via environment variables in container, bypassing general network restrictions.

### Environment Variables

Required for all agents:
```bash
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-5.5"
```

Claude Code specific:
```bash
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

## Comparison: Direct vs Docker

### Direct Mode (Quick Testing)

**Pros**:
- Faster execution (no container overhead)
- Easier debugging (direct file access)
- Simpler setup

**Cons**:
- ⚠️ Agent can access entire filesystem
- ⚠️ Can potentially read benchmark answers
- ⚠️ Can download external packages
- ⚠️ Not reproducible across environments

**Use when**:
- Developing new agents
- Quick debugging
- Local testing

```bash
python scripts/run_evaluation.py \
    --agent openhands \
    --model gpt-5.5 \
    --mode direct \
    --output results/quick_test
```

### Docker Mode (Official Evaluation)

**Pros**:
- ✅ Secure data isolation
- ✅ Reproducible environment
- ✅ Resource constraints
- ✅ Network control

**Cons**:
- Slower (container startup overhead)
- Requires Docker installed
- More complex debugging

**Use when**:
- Running official benchmarks
- Submitting to leaderboard
- Comparing different agents fairly

```bash
python scripts/run_evaluation.py \
    --agent openhands \
    --model gpt-5.5 \
    --mode docker \
    --output results/official_eval
```

## Best Practices

### 1. Always Use Docker for Official Results
```bash
# ✅ Good - secure, reproducible
python scripts/run_evaluation.py --mode docker --agent openhands ...

# ⚠️ Not recommended for leaderboard submission
python scripts/run_evaluation.py --mode direct --agent openhands ...
```

### 2. Test First with Subset
```bash
# Test with 4 instances first
python scripts/run_evaluation.py \
    --mode docker \
    --agent openhands \
    --instances 0 1 2 3 \
    --output results/docker_test
```

### 3. Monitor Resource Usage
```bash
# Check container stats
docker stats codabench-oh-*
```

### 4. Clean Up After Evaluation
```bash
# Remove stopped containers
docker container prune

# Remove old images
docker image prune
```

## Troubleshooting

### Container Fails to Start
```bash
# Check Docker is running
docker ps

# Verify image exists
docker images | grep codabench

# Rebuild if needed
cd docker/<agent>
docker build -t codabench-<agent>:latest .
```

### Network Issues
```bash
# LLM API not accessible
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="your-key"

# For proxies
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
```

### Memory/Timeout Issues
```bash
# Increase limits in docker/<agent>/run_task.sh
--memory=16g \
--cpus=4

# Or increase timeout
--timeout 1200
```

### Permission Errors
```bash
# Fix workspace permissions
chmod -R 777 results/

# Run with current user
docker run --user $(id -u):$(id -g) ...
```

## Advanced: Custom Docker Images

Create your own agent Docker image:

1. Create `docker/my-agent/Dockerfile`:
```dockerfile
FROM python:3.10-slim
RUN pip install my-agent-package
COPY network-lock.sh /opt/
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

2. Create `docker/my-agent/run_task.sh`:
```bash
#!/bin/bash
docker run --rm \
    -v "$TASK_DIR:/workspace:rw" \
    -v "$DATA_DIR:/data:ro" \
    -v "$OUTPUT_DIR:/output:rw" \
    -e "LLM_API_KEY=$LLM_API_KEY" \
    --memory=8g --cpus=2 \
    codabench-my-agent:latest
```

3. Register in `scripts/run_evaluation.py`

## Security Checklist

Before official evaluation:
- ✅ Using Docker mode
- ✅ Data mounted read-only (`/data:ro`)
- ✅ Network isolation enabled
- ✅ Resource limits set
- ✅ Agent cannot access answers directory
- ✅ Built from official Dockerfile

## Citation

```bibtex
@inproceedings{zhang2026codabench,
  title={CODA-BENCH: Can Code Agents Handle Data-Intensive Tasks?},
  author={Zhang, Yuxin and Fan, Ju and Fan, Meihao and Zhang, Shaolei and Du, Xiaoyong},
  booktitle={Proceedings of the 43rd International Conference on Machine Learning},
  year={2026}
}
```
