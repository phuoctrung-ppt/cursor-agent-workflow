#!/usr/bin/env python3
"""Cursor workflow hook helper for protected-change review gates and worker scopes.

Modes:
  record-edit   Read hook JSON from stdin and record edited file paths.
  pre-tool-use  Read hook JSON from stdin and block edits outside worker scope.
  stop          Read hook JSON from stdin and require review artifacts for protected changes.
  skip-review   Log a manual review override with an audit trail.

The implementation is deliberately defensive: it fail-opens for non-protected or
unparseable payloads, and fail-closes only after the shared protected classifier
is triggered.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ROOT is resolved by walking up 2 levels from this script's location (.cursor/hooks/).
# This assumes the script always lives at <project-root>/.cursor/hooks/workflow-guard.py.
# If you move the file, update the parents[2] index accordingly.
ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = ROOT / "AGENTS.md"  # Project domain config hub (fill in for each project)
CONFIG = ROOT / ".cursor" / "config" / "protected-paths.json"
SCOPES = ROOT / ".cursor" / "config" / "worker-scopes.json"
STATE_DIR = ROOT / ".cursor" / "state"
STATE = STATE_DIR / "workflow-state.json"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load_stdin() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw}


def rel(path: str) -> str | None:
    if not path:
        return None
    p = Path(path)
    try:
        if p.is_absolute():
            return p.resolve().relative_to(ROOT).as_posix()
    except Exception:
        return p.name
    return p.as_posix().lstrip("./")


def extract_paths(obj: Any) -> list[str]:
    paths: list[str] = []
    path_keys = {"file_path", "filePath", "path", "filename", "file", "target_file", "targetFile"}

    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, k)
        elif isinstance(value, list):
            for v in value:
                walk(v, key)
        elif isinstance(value, str):
            if key in path_keys or "/" in value or value.endswith((".ts", ".tsx", ".js", ".json", ".md", ".yml", ".yaml", ".sh", ".py")):
                rp = rel(value)
                if rp and not rp.startswith(".."):
                    paths.append(rp)

    walk(obj)
    seen = set()
    result = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) or fnmatch.fnmatch("/" + path, pat) for pat in patterns)


def current_git_changed() -> list[str]:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    paths = []
    for line in out.splitlines():
        if not line.strip():
            continue
        item = line[3:].strip()
        if " -> " in item:
            item = item.split(" -> ", 1)[1]
        if item:
            paths.append(item)
    return paths


def state() -> dict[str, Any]:
    return load_json(STATE, {"editedFiles": [], "stopBlockCount": 0, "overrides": [], "events": []})


def save_state(s: dict[str, Any]) -> None:
    write_json(STATE, s)


def protected_reasons(paths: list[str]) -> list[str]:
    cfg = load_json(CONFIG, {})
    # Merge generic + project globs. The flat 'protectedGlobs' key is kept for
    # backward-compat but is no longer required — merging at runtime avoids duplication.
    if "protectedGlobs" in cfg:
        protected_globs = cfg["protectedGlobs"]
    else:
        protected_globs = cfg.get("genericProtectedGlobs", []) + cfg.get("projectProtectedGlobs", [])
    keywords = cfg.get("protectedKeywords", [])
    threshold = int(cfg.get("multiFileThreshold", 3))
    reasons: list[str] = []
    protected_paths = [p for p in paths if matches(p, protected_globs)]
    if protected_paths:
        reasons.append("protected path(s): " + ", ".join(protected_paths[:8]))
    if len(set(paths)) >= threshold:
        reasons.append(f"multi-file threshold: {len(set(paths))} files >= {threshold}")
    keyword_hits: list[str] = []
    for p in paths:
        fp = ROOT / p
        if not fp.is_file() or fp.stat().st_size > 1_000_000:
            continue
        try:
            text = fp.read_text(errors="ignore")
        except Exception:
            continue
        for kw in keywords:
            if kw in text:
                keyword_hits.append(f"{p}:{kw}")
                break
    if keyword_hits:
        reasons.append("protected keyword(s): " + ", ".join(keyword_hits[:8]))
    return reasons


def output_allow(extra: dict[str, Any] | None = None) -> int:
    data = {"permission": "allow"}
    if extra:
        data.update(extra)
    print(json.dumps(data))
    return 0


def output_block(reason: str, *, stop: bool = False, followup: str | None = None) -> int:
    if stop:
        data = {"decision": "block", "reason": reason}
        if followup:
            data["followup_message"] = followup
        print(json.dumps(data))
        return 0
    print(json.dumps({"permission": "deny", "userMessage": reason, "agentMessage": reason}))
    return 0


def command_record_edit(_: argparse.Namespace) -> int:
    payload = load_stdin()
    paths = extract_paths(payload)
    s = state()
    edited = set(s.get("editedFiles", []))
    edited.update(paths)
    s["editedFiles"] = sorted(edited)
    s.setdefault("events", []).append({"time": now(), "type": "record-edit", "paths": paths})
    save_state(s)
    return output_allow()


def agent_name(payload: Any) -> str:
    for key in ("agent", "agentName", "agent_name", "name"):
        if isinstance(payload, dict) and isinstance(payload.get(key), str):
            return payload[key]
    return os.environ.get("CURSOR_AGENT_NAME") or os.environ.get("AGENT_NAME") or "default"


def command_pre_tool_use(_: argparse.Namespace) -> int:
    payload = load_stdin()
    paths = extract_paths(payload)
    if not paths:
        return output_allow()
    scopes = load_json(SCOPES, {"default": ["**/*"]})
    agent = agent_name(payload)
    agent_scopes = scopes.get("agents", {}) if isinstance(scopes.get("agents", {}), dict) else {}
    allowed = agent_scopes.get(agent, scopes.get(agent, scopes.get("default", ["**/*"])))
    denied = [p for p in paths if not matches(p, allowed)]
    if denied:
        reason = (
            f"Worker scope violation for agent '{agent}'. Blocked path(s): {', '.join(denied)}. "
            "Request a scope expansion from the orchestrator instead of editing outside the handoff packet."
        )
        return output_block(reason)
    return output_allow()


def has_artifact(paths: list[str], globs: list[str]) -> bool:
    # Only current edited/diff paths count. Pre-existing artifacts do not satisfy
    # the gate because they do not prove this change was reviewed/planned.
    return any(matches(p, globs) for p in paths)


def has_review_artifact(paths: list[str]) -> bool:
    cfg = load_json(CONFIG, {})
    return has_artifact(paths, cfg.get("reviewArtifactGlobs", ["docs/reviews/**"]))


def has_plan_artifact(paths: list[str]) -> bool:
    cfg = load_json(CONFIG, {})
    return has_artifact(paths, cfg.get("planArtifactGlobs", ["docs/plans/**", "docs/adr/**"]))


def active_override(s: dict[str, Any]) -> dict[str, Any] | None:
    overrides = s.get("overrides", [])
    if overrides:
        return overrides[-1]
    override_file = STATE_DIR / "review-override.json"
    if override_file.exists():
        return load_json(override_file, None)
    return None


def command_stop(_: argparse.Namespace) -> int:
    _payload = load_stdin()
    s = state()
    paths = sorted(set(s.get("editedFiles", []) + current_git_changed()))
    reasons = protected_reasons(paths)
    if not reasons:
        s["stopBlockCount"] = 0
        save_state(s)
        return output_allow({"reason": "no protected changes detected"})

    missing = []
    cfg = load_json(CONFIG, {})
    if cfg.get("planRequiredForProtected", True) and not has_plan_artifact(paths):
        missing.append("docs/plans/* or docs/adr/* plan artifact")
    if not has_review_artifact(paths):
        missing.append("docs/reviews/* review artifact")
    if not missing:
        s["stopBlockCount"] = 0
        save_state(s)
        return output_allow({"reason": "protected change has required plan and review artifacts"})

    override = active_override(s)
    if override and override.get("reason"):
        s["stopBlockCount"] = 0
        save_state(s)
        return output_allow({"reason": "manual review override logged"})

    cfg = load_json(CONFIG, {})
    cap = int(cfg.get("stopRetryCap", 2))
    count = int(s.get("stopBlockCount", 0)) + 1
    s["stopBlockCount"] = count
    s.setdefault("events", []).append({"time": now(), "type": "stop-block", "count": count, "reasons": reasons})
    save_state(s)

    if count <= cap:
        reason = (
            "Protected change detected without required artifact(s): " + ", ".join(missing) + ". "
            f"Reason(s): {'; '.join(reasons)}. "
            "Create/update the plan and run /workflow-eval to persist the review, or use `.cursor/hooks/review-override.sh --skip-review \"reason\"` for a logged manual override."
        )
        followup = "Continue: create the required workflow/judge review artifact or log an explicit skip-review override with a reason."
        return output_block(reason, stop=True, followup=followup)

    escalation = ROOT / "docs" / "reviews" / f"{dt.date.today().isoformat()}-hook-review-escalation.md"
    escalation.parent.mkdir(parents=True, exist_ok=True)
    escalation.write_text(
        "# Protected Review Gate Escalation\n\n"
        f"Date: {dt.date.today().isoformat()}\n\n"
        "The stop hook reached its retry cap while a protected change lacked required plan/review artifacts.\n\n"
        "## Protected Reasons\n\n" + "\n".join(f"- {r}" for r in reasons) + "\n\n"
        "## Changed Files\n\n" + "\n".join(f"- `{p}`" for p in paths) + "\n\n"
        "## Missing Artifacts\n\n" + "\n".join(f"- {m}" for m in missing) + "\n\n"
        "## Required Human Action\n\nCreate real plan/review artifacts for this change or approve a logged skip-review override.\n"
    )
    s["stopBlockCount"] = 0
    s.setdefault("events", []).append({"time": now(), "type": "stop-escalation", "path": escalation.relative_to(ROOT).as_posix()})
    save_state(s)
    return output_allow({"reason": f"retry cap reached; escalation written to {escalation.relative_to(ROOT).as_posix()}"})


def command_skip_review(args: argparse.Namespace) -> int:
    reason = args.reason.strip()
    if not reason:
        print("usage: review-override.sh --skip-review \"reason\"", file=sys.stderr)
        return 2
    cfg = load_json(CONFIG, {})
    log_path = ROOT / cfg.get("overrideLog", "docs/reviews/review-overrides.log")
    s = state()
    paths = sorted(set(s.get("editedFiles", []) + current_git_changed()))
    entry = {"time": now(), "reason": reason, "changedFiles": paths}
    s.setdefault("overrides", []).append(entry)
    s.setdefault("events", []).append({"time": now(), "type": "skip-review", "reason": reason})
    save_state(s)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"Logged review override: {log_path.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("record-edit")
    sub.add_parser("pre-tool-use")
    sub.add_parser("stop")
    skip = sub.add_parser("skip-review")
    skip.add_argument("--skip-review", dest="reason", required=True)
    args = parser.parse_args()
    return {
        "record-edit": command_record_edit,
        "pre-tool-use": command_pre_tool_use,
        "stop": command_stop,
        "skip-review": command_skip_review,
    }[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
