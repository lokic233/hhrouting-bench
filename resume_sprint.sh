#!/bin/bash
# resume_sprint.sh — IDEMPOTENT, crash-resilient sprint runner. Checks which deliverables already exist
# and only (re)runs the agents whose outputs are missing/empty, respecting wave dependencies. Safe to call
# repeatedly (by the monitor or by hand). A no-op once everything is produced.
set -u
INSTANCE="$(cd "$(dirname "$0")" && pwd)"
source /tmp/agentenv.sh 2>/dev/null
RESEARCH="$INSTANCE/hhrouting_bench_research"; LOGS="$INSTANCE/logs"; TASKS="$INSTANCE/tasks"
RA="$INSTANCE/run_agent.sh"; mkdir -p "$RESEARCH" "$LOGS"
ts(){ date -u +%H:%M:%SZ; }
# a deliverable "exists" iff present AND non-trivial (>200 bytes) — guards against empty/stub files
have(){ [ -s "$RESEARCH/$1" ] && [ "$(wc -c <"$RESEARCH/$1")" -gt 200 ]; }
running(){ pgrep -f "run_agent.sh $1 " >/dev/null; }

commit(){ ( cd "$INSTANCE" && git add -A && \
  git -c user.name="Loki Chen" -c user.email="dengcchi@meta.com" commit -q -m "resume: $1" 2>/dev/null && \
  timeout 40 git push origin main 2>&1 | tail -1 ) || true; }

# run agent $1(letter) on $2(backend) with task $3, ONLY if not already running; wait for it.
run_if_needed(){ local A="$1" BK="$2" TF="$3"
  if running "$A"; then echo "[$(ts)] $A already running — waiting"; while running "$A"; do sleep 30; done; return; fi
  echo "[$(ts)] (re)launching $A on $BK"
  nohup "$RA" "$A" "$BK" "$TASKS/$TF" "$LOGS/agent_${A}.log" >/dev/null 2>&1 &
  local p=$!; while kill -0 "$p" 2>/dev/null; do sleep 30; done
}

echo "[$(ts)] resume_sprint: checking deliverables..."

# WAVE 1: A(01_*.csv) C(03_payload_schema_inventory.md) G(01b_production_traces.md)
w1=()
have 01_benchmark_validation_table.csv || w1+=("A claude-opus-4-8 task_A.md")
have 03_payload_schema_inventory.md   || w1+=("C codex task_C.md")
have 01b_production_traces.md          || w1+=("G gemini task_G.md")
if [ ${#w1[@]} -gt 0 ]; then echo "[$(ts)] WAVE1 missing: ${#w1[@]}"; pids=()
  for s in "${w1[@]}"; do set -- $s; run_if_needed "$1" "$2" "$3" & pids+=($!); sleep 4; done
  for p in "${pids[@]}"; do wait "$p"; done; commit "wave1"
else echo "[$(ts)] WAVE1 complete"; fi

# WAVE 2: B(02_workload_decomposition.csv) D(04_trace_feasibility_matrix.csv)
w2=()
have 02_workload_decomposition.csv || w2+=("B claude-opus-4-7 task_B.md")
have 04_trace_feasibility_matrix.csv || w2+=("D claude-opus-4-8 task_D.md")
if [ ${#w2[@]} -gt 0 ]; then echo "[$(ts)] WAVE2 missing: ${#w2[@]}"; pids=()
  for s in "${w2[@]}"; do set -- $s; run_if_needed "$1" "$2" "$3" & pids+=($!); sleep 4; done
  for p in "${pids[@]}"; do wait "$p"; done; commit "wave2"
else echo "[$(ts)] WAVE2 complete"; fi

# WAVE 3: E(05_canonical_workload_taxonomy.md)
have 05_canonical_workload_taxonomy.md || { echo "[$(ts)] WAVE3 E"; run_if_needed E claude-opus-4-8 task_E.md; commit "wave3"; }
# WAVE 4: F(06_red_team_review.md)
have 06_red_team_review.md || { echo "[$(ts)] WAVE4 F"; run_if_needed F codex task_F.md; commit "wave4"; }
# WAVE 5: R(07_final_overnight_report.md)
have 07_final_overnight_report.md || { echo "[$(ts)] WAVE5 R"; run_if_needed R claude-opus-4-8 task_R.md; commit "wave5"; }

echo "[$(ts)] resume_sprint DONE. Deliverables:"; ls -1 "$RESEARCH" | grep -E "^0[0-9]" | sort
