#!/usr/bin/env bash
# Block destructive shell commands in agent sessions
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.command // empty')

BLOCK_PATTERNS=(
  'rm\s+-rf\s+/'
  'rm\s+-rf\s+\*'
  'git\s+push\s+.*--force'
  'git\s+reset\s+--hard'
  'DROP\s+DATABASE'
  'DROP\s+SCHEMA'
  'truncate\s+table'
)

for pattern in "${BLOCK_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    jq -n --arg cmd "$COMMAND" --arg reason "Blocked by platform safety hook: destructive command pattern matched" \
      '{permission: "deny", userMessage: $reason, agentMessage: ("Command blocked: " + $cmd)}'
    exit 0
  fi
done

jq -n '{permission: "allow"}'
