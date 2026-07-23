#!/usr/bin/env python3
"""Universal phase-based skill loader for the agent framework.

Every agent calls this script at the start of a task. It reads
`.cursor/skills/skills-manifest.json`, filters skills by execution phase
(and optionally agent), scores them against task keywords, and returns:

  - matched skill ENTRY PATHS (SKILL.md) — agent reads only what it needs
  - matched reference FILE PATHS (links only, never content)
  - skill scripts the agent may run

The script never prints file contents. Context stays minimal by design.

Usage:
  python3 .cursor/skills/scripts/skill-loader.py \
      --phase implement-frontend \
      --task "Build dashboard with server components" \
      --keywords "react,rsc,streaming,dashboard" \
      [--agent frontend-worker] [--limit 4] [--ref-limit 8] \
      [--root /path/to/project] [--manifest-path /path/to/skills-manifest.json]

Phases: brainstorm | plan | design | implement-frontend | implement-backend
        | database | devops | skill-authoring | test | fix | review | dev-module

Root resolution order (first wins):
  1. --root argument
  2. GIT_ROOT (git rev-parse --show-toplevel)
  3. CWD
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


STOP_WORDS = {
    "a", "an", "and", "are", "as", "be", "by", "for", "from", "in", "into",
    "is", "it", "of", "on", "or", "the", "to", "use", "using", "when", "with",
    "build", "create", "add", "make", "new", "page", "app",
}


def detect_root(explicit_root: str | None) -> Path:
    """Resolve project root with fallback chain: --root → git → CWD."""
    if explicit_root:
        return Path(explicit_root).resolve()
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(git_root).resolve()
    except Exception:
        return Path.cwd().resolve()


def resolve_manifest(explicit_path: str | None, root: Path) -> Path:
    """Find the manifest file — explicit path, or default under root."""
    if explicit_path:
        return Path(explicit_path).resolve()
    # Default: .cursor/skills/skills-manifest.json relative to root
    default = root / ".cursor" / "skills" / "skills-manifest.json"
    if default.exists():
        return default
    # Fallback: try relative to this script's location (legacy behaviour)
    legacy = Path(__file__).resolve().parent.parent / "skills-manifest.json"
    if legacy.exists():
        return legacy
    return default  # let load_manifest() report the missing-file error


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+-]*", text.lower())
    return {t.replace("_", "-") for t in tokens if t not in STOP_WORDS}


def load_manifest(path: Path) -> dict:
    if not path.exists():
        sys.exit(
            f"error: manifest not found at {path}\n"
            f"  Looked for: {path}\n"
            f"  Run from the project root, or use --root / --manifest-path to specify locations."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def score_skill(skill: dict, terms: set[str]) -> tuple[float, list[str]]:
    skill_terms = {k.lower() for k in skill.get("keywords", [])}
    hits = sorted(terms & skill_terms)
    score = len(hits) * 1.0 + (0.5 if skill["id"].lower() in terms else 0.0)
    return score, hits


def match_references(skill: dict, terms: set[str], skills_root: str) -> list[dict]:
    """Match reference files by keyword. Returns paths only, never content."""
    refs = []
    ref_keywords: dict = skill.get("refKeywords", {})
    refs_dir = skill.get("referencesDir", "")
    for filename, keywords in ref_keywords.items():
        hits = sorted(terms & {k.lower() for k in keywords})
        if hits:
            refs.append({
                "skill": skill["id"],
                "path": f"{skills_root}/{refs_dir}/{filename}",
                "reason": f"matched: {', '.join(hits)}",
                "hits": len(hits),
            })
    refs.sort(key=lambda r: r["hits"], reverse=True)
    for r in refs:
        r.pop("hits")
    return refs


def collect_skills(manifest: dict) -> list[dict]:
    """Collect all skills from both portableSkills and skills arrays."""
    skills = []
    skills.extend(manifest.get("portableSkills", []))
    skills.extend(manifest.get("skills", []))
    return skills


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase-based skill loader")
    parser.add_argument("--phase", required=True, help="Execution phase")
    parser.add_argument("--task", default="", help="Task description")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--agent", default="", help="Agent id (optional filter boost)")
    parser.add_argument("--limit", type=int, default=4, help="Max skills returned")
    parser.add_argument("--ref-limit", type=int, default=8, help="Max references returned")
    parser.add_argument("--root", default="", help="Project root path (default: git root or CWD)")
    parser.add_argument("--manifest-path", default="", help="Explicit path to skills-manifest.json")
    args = parser.parse_args()

    root = detect_root(args.root or None)
    manifest_path = resolve_manifest(args.manifest_path or None, root)
    manifest = load_manifest(manifest_path)

    skills_root = manifest.get("skillsRoot", ".cursor/skills")

    if args.phase not in manifest.get("phases", []):
        sys.exit(f"error: unknown phase '{args.phase}'. Valid: {manifest.get('phases')}")

    keyword_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    terms = tokenize(args.task) | {k.lower().replace("_", "-") for k in keyword_list}

    all_skills = collect_skills(manifest)
    matched_skills = []
    matched_refs = []

    for skill in all_skills:
        if args.phase not in skill.get("phases", []):
            continue
        score, hits = score_skill(skill, terms)
        if args.agent and args.agent in skill.get("agents", []):
            score += 2.0  # agent-designated skills are near-mandatory
        if score <= 0 and not (args.agent and args.agent in skill.get("agents", [])):
            continue
        matched_skills.append({
            "id": skill["id"],
            "entry": f"{skills_root}/{skill['entry']}",
            "portable": skill.get("portable", True),
            # omit domainTag when null to keep output clean
            **({"domainTag": skill["domainTag"]} if skill.get("domainTag") else {}),
            "score": round(score, 2),
            "matchedTerms": hits,
            "scripts": skill.get("scripts", []),
        })
        matched_refs.extend(match_references(skill, terms, skills_root))

    matched_skills.sort(key=lambda s: s["score"], reverse=True)

    result = {
        "phase": args.phase,
        "agent": args.agent or None,
        "projectRoot": str(root),
        "manifestPath": str(manifest_path),
        "matchedSkills": matched_skills[: args.limit],
        "referenceFiles": matched_refs[: args.ref_limit],
        "usage": [
            "Read matchedSkills[].entry (SKILL.md) for skills you will actually use.",
            "referenceFiles are LINKS. Read one only when its knowledge is required mid-task.",
            "Run scripts[] commands when the skill workflow requires them.",
            "Never bulk-read every reference file.",
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
