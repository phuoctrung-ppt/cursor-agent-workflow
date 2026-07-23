#!/usr/bin/env bash
# Inject workflow context at session start
set -euo pipefail

jq -n '{
  "additional_context": "Agentic Planner-Worker-Judge workflow active. Read AGENTS.md for project identity, tech stack, scope, and compliance requirements. Run skill-loader before coding tasks: python3 .cursor/skills/scripts/skill-loader.py --phase <phase> --task \"<task>\" --agent <agent>. Use handoff packets between agents. Write plans to docs/plans/, reviews to docs/reviews/. Protected changes require current plan/review artifacts before completion; low-risk changes need a brief rationale."
}'
