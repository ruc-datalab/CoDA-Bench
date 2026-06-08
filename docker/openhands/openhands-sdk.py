#!/usr/bin/env python3
"""
OpenHands SDK script for CoDA-Bench evaluation.
Runs an OpenHands agent on a single task instance using the SDK.

Environment variables:
    LLM_MODEL       - Model name (default: gpt-5.5)
    LLM_API_KEY     - API key
    LLM_BASE_URL    - API base URL (default: https://api.openai.com/v1)
    WORKSPACE       - Workspace directory (default: /workspace)
    TRAJECTORY_PATH - Where to save the interaction trajectory (JSONL)
    STATS_PATH      - Where to save run statistics (JSON)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

os.environ.setdefault("OPENHANDS_SUPPRESS_BANNER", "1")

# === Network Isolation ===
# Keep proxy in os.environ so LLM calls work normally.
# Monkey-patch OpenHands sanitized_env() to strip proxy from terminal subprocesses.
_PROXY_VARS = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
               "all_proxy", "ALL_PROXY", "no_proxy", "NO_PROXY")

def _patch_sanitized_env():
    """Patch sanitized_env to strip proxy vars from subprocess environments."""
    try:
        from openhands.sdk.utils import command as cmd_module
        _original = cmd_module.sanitized_env

        def _sanitized_env_no_proxy(env=None):
            result = _original(env)
            for var in _PROXY_VARS:
                result.pop(var, None)
            result["PIP_NO_INDEX"] = "1"
            result["PIP_INDEX_URL"] = "file:///dev/null"
            return result

        cmd_module.sanitized_env = _sanitized_env_no_proxy

        # Also patch in all modules that imported sanitized_env by name
        from openhands.tools.terminal.terminal import subprocess_terminal
        subprocess_terminal.sanitized_env = _sanitized_env_no_proxy
        from openhands.tools.terminal.terminal import factory as terminal_factory
        terminal_factory.sanitized_env = _sanitized_env_no_proxy
        try:
            from openhands.tools.terminal.terminal import tmux_terminal
            tmux_terminal.sanitized_env = _sanitized_env_no_proxy
        except ImportError:
            pass

        print("[sdk] Patched sanitized_env: terminal subprocesses will have no proxy", flush=True)
    except Exception as e:
        print(f"[sdk] Warning: Failed to patch sanitized_env: {e}", flush=True)

_patch_sanitized_env()


def main():
    from openhands.sdk import LLM, Agent, Conversation, Tool
    from openhands.tools.terminal import TerminalTool
    from openhands.tools.file_editor import FileEditorTool

    workspace = Path(os.environ.get("WORKSPACE", "/workspace"))
    task_file = workspace / "task_description.txt"
    result_file = workspace / "result.txt"
    trajectory_path = Path(os.environ.get("TRAJECTORY_PATH", "/output/trajectory.jsonl"))
    stats_path = Path(os.environ.get("STATS_PATH", "/output/stats.json"))

    trajectory_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    if not task_file.exists():
        print(f"ERROR: {task_file} not found", file=sys.stderr)
        return 1

    task = task_file.read_text(encoding="utf-8").strip()
    print(f"Task loaded ({len(task)} chars)", flush=True)

    # Build LLM config
    llm_model = os.environ.get("LLM_MODEL", "gpt-5.5")
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")

    if not llm_api_key:
        print("ERROR: LLM_API_KEY not set", file=sys.stderr)
        return 1

    llm = LLM(
        model=llm_model,
        api_key=llm_api_key,
        base_url=llm_base_url,
    )
    print(f"LLM configured: {llm_model} @ {llm_base_url}", flush=True)

    agent = Agent(
        llm=llm,
        tools=[
            Tool(name=TerminalTool.name),
            Tool(name=FileEditorTool.name),
        ],
    )

    # Callback to capture trajectory events
    events = []

    def on_event(event):
        events.append(event)
        with open(trajectory_path, "a", encoding="utf-8") as f:
            if hasattr(event, "model_dump"):
                data = event.model_dump(mode="json", exclude_none=True)
            else:
                data = event
            f.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")

    conversation = Conversation(
        agent=agent,
        workspace=str(workspace),
        callbacks=[on_event],
    )
    print("Sending task to agent...", flush=True)

    start_time = time.time()
    conversation.send_message(task)
    conversation.run()
    duration = time.time() - start_time

    print(f"Completed in {duration:.1f}s with {len(events)} events", flush=True)

    # Get token usage from LLM metrics if available
    token_info = {}
    if hasattr(llm, "metrics"):
        metrics = llm.metrics
        if hasattr(metrics, "model_dump"):
            token_info = metrics.model_dump()

    stats = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "interaction_rounds": len(events),
        "model": llm_model,
        "api_base": llm_base_url,
        "tokens": token_info,
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    if result_file.exists() and result_file.read_text(encoding="utf-8").strip():
        result = result_file.read_text(encoding="utf-8").strip()
        print(f"SUCCESS: result.txt = {result[:200]}")
        return 0
    else:
        print("WARNING: result.txt is empty or missing", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
