#!/bin/bash
# run_sprint.sh — HHRouting-Bench overnight multi-agent sprint driver.
# Runs the 7-agent committee (A,C,G || B,D || E || F || final report) across 4 backends with a
# dependency-aware wave schedule. Each agent is headless, internet-enabled, writes durable deliverables.
set -u
INSTANCE="$(cd "$(dirname "$0")" && pwd)"
source /tmp/agentenv.sh 2>/dev/null   # user cert env (unset agent-role; point thrift TLS at user x509)
LOGS="$INSTANCE/logs"; TASKS="$INSTANCE/tasks"; RESEARCH="$INSTANCE/hhrouting_bench_research"
mkdir -p "$LOGS" "$TASKS" "$RESEARCH"
RA="$INSTANCE/run_agent.sh"
ts(){ date -u +%H:%M:%SZ; }
banner(){ echo "==================== [$(ts)] $* ===================="; }

# Backend assignment (all 4 backends in play):
#   A Validator      -> claude-opus-4-8   (strongest factual web research)
#   C Sampler        -> codex             (good at schema/structured extraction)
#   G Trace-hunter   -> gemini            (contained, single-file deep search)
#   B Decomposer     -> claude-opus-4-7 (4.7)
#   D TraceFeasib    -> claude-opus-4-8
#   E Taxonomy       -> claude-opus-4-8
#   F RedTeam        -> codex             (independent family from producers)
#   Report (07)      -> claude-opus-4-8

run_wave(){ # label "AGENT BACKEND TASKFILE" ...
  local label="$1"; shift
  banner "WAVE: $label START"
  local pids=()
  for spec in "$@"; do
    set -- $spec; local A="$1" BK="$2" TF="$3"
    local LOG="$LOGS/agent_${A}.log"
    echo "[$(ts)] launch agent $A on $BK (task $TF)"
    nohup "$RA" "$A" "$BK" "$TASKS/$TF" "$LOG" >/dev/null 2>&1 &
    pids+=($!)
    sleep 4   # stagger so concurrent CLIs don't hammer the gateway at once
  done
  echo "[$(ts)] wave '$label' pids: ${pids[*]} — waiting..."
  for p in "${pids[@]}"; do wait "$p"; done
  banner "WAVE: $label DONE"
  # research-os principle: commit+push after every wave so no deliverable is ever lost.
  ( cd "$INSTANCE" && git add -A && \
    git -c user.name="Loki Chen" -c user.email="dengcchi@meta.com" \
      commit -q -m "sprint: wave [$label] deliverables" 2>/dev/null && \
    timeout 40 git push origin main 2>&1 | tail -1 ) || echo "[$(ts)] (nothing to commit for $label)"
}

banner "HHROUTING-BENCH SPRINT START"
run_wave "1: discover (A||C||G)"   "A claude-opus-4-8 task_A.md" "C codex task_C.md" "G gemini task_G.md"
run_wave "2: decompose (B||D)"     "B claude-opus-4-7 task_B.md" "D claude-opus-4-8 task_D.md"
run_wave "3: taxonomy (E)"         "E claude-opus-4-8 task_E.md"
run_wave "4: red-team (F)"         "F codex task_F.md"
run_wave "5: final report (R)"     "R claude-opus-4-8 task_R.md"
banner "HHROUTING-BENCH SPRINT COMPLETE — deliverables in $RESEARCH"
ls -la "$RESEARCH" >> "$LOGS/_sprint.log" 2>&1
