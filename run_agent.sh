#!/bin/bash
# run_agent.sh — dispatch ONE HHRouting-Bench agent to its configured backend, headless, with internet.
# Adapted from research-os/engine/run_committee.sh for Linux devvm (internet-mode flags differ from macOS).
#
# Usage: run_agent.sh <AGENT_LETTER> <backend> <task_file> <log_file>
#   backend ∈ {claude-opus-4-8, claude-sonnet-4-7, codex, gemini}
set -u
AGENT="$1"; BACKEND="$2"; TASKFILE="$3"; LOG="$4"
INSTANCE="$(cd "$(dirname "$0")" && pwd)"
COMMON="$INSTANCE/prompts/agents/_common.md"
ROLE="$INSTANCE/prompts/agents/agent_${AGENT}.md"
RESEARCH="$INSTANCE/hhrouting_bench_research"
mkdir -p "$RESEARCH"

# Build the full prompt: common rules + role prompt + the concrete task.
PROMPT="$(cat "$COMMON" "$ROLE" "$TASKFILE" 2>/dev/null)
=== YOUR WORKING DIRECTORY ===
Write ALL deliverables to: $RESEARCH
(cd there or use absolute paths. Exact filenames matter.)
=== BEGIN WORK NOW. Be thorough, cite every URL, finish your deliverables. ==="

cd "$RESEARCH" || exit 9
echo "[$(date -u +%H:%M:%SZ)] START agent=$AGENT backend=$BACKEND" >> "$LOG"

# Per-agent safety timeout (generous — thorough research is the goal; this only kills a truly hung proc).
TO="${AGENT_TIMEOUT:-4500}"   # 75 min default

case "$BACKEND" in
  claude-*|opus*|sonnet*)
    timeout "$TO" claude --dangerously-enable-internet-mode --allow-dangerously-skip-permissions \
      --model "$BACKEND" -p "$PROMPT" </dev/null >>"$LOG" 2>&1 ;;
  codex*)
    # codex default model (the explicit 5.5 string 421s on this gateway); full access for file writes.
    timeout "$TO" codex --dangerously-bypass-approvals-and-sandbox exec --skip-git-repo-check \
      "$PROMPT" </dev/null >>"$LOG" 2>&1 ;;
  gemini*)
    OTEL_SDK_DISABLED=true timeout "$TO" gemini --dangerously-enable-internet-mode --yolo \
      -p "$PROMPT" </dev/null >>"$LOG" 2>&1 ;;
  *)
    echo "ERROR: unknown backend '$BACKEND'" >> "$LOG"; exit 4 ;;
esac
RC=$?
echo "[$(date -u +%H:%M:%SZ)] END agent=$AGENT backend=$BACKEND rc=$RC" >> "$LOG"
exit $RC
