#!/bin/bash
# watchdog.sh — keeps the sprint progressing unattended. Every 5 min: if no sprint driver/resumer is
# running AND the final report isn't done, kick resume_sprint.sh. Self-terminates when 07 report exists.
# Detached + nohup so it survives SSH drops. Logs to logs/_watchdog.log.
set -u
INSTANCE="$(cd "$(dirname "$0")" && pwd)"
RESEARCH="$INSTANCE/hhrouting_bench_research"; LOG="$INSTANCE/logs/_watchdog.log"
ts(){ date -u +%FT%TZ; }
echo "[$(ts)] watchdog START (pid $$)" >> "$LOG"
for i in $(seq 1 80); do   # 80 * 5min = ~6.7h hard cap
  if [ -s "$RESEARCH/07_final_overnight_report.md" ] && [ "$(wc -c <"$RESEARCH/07_final_overnight_report.md")" -gt 1000 ]; then
    echo "[$(ts)] final report present — watchdog exiting" >> "$LOG"; exit 0
  fi
  # is anything actively driving/working?
  active=0
  ps -eo args | grep -E "[r]un_sprint\.sh"    >/dev/null && active=1
  ps -eo args | grep -E "[r]esume_sprint\.sh" >/dev/null && active=1
  for L in A B C D E F G R; do ps -eo args | grep -E "[r]un_agent\.sh $L " >/dev/null && active=1; done
  if [ "$active" -eq 0 ]; then
    echo "[$(ts)] no active sprint/agent — kicking resume_sprint.sh" >> "$LOG"
    nohup "$INSTANCE/resume_sprint.sh" >> "$INSTANCE/logs/_resume.log" 2>&1 &
    sleep 60   # give the resumer time to claim work before re-checking
  fi
  sleep 300
done
echo "[$(ts)] watchdog hit time cap — exiting" >> "$LOG"
