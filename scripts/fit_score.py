#!/usr/bin/env python3
"""6축 점수 → 가중 Fit Score·공식 레벨을 결정적으로 계산한다.

가중치·게이트·바닥 보정은 references/common/weights.md frontmatter가 정본이다.
에이전트는 축별 점수(1.0~7.0)와 비율 지표만 판단하고, 산술은 이 스크립트에 맡긴다.

사용 예:
  python3 fit_score.py --type builder \
      --scores '{"DECOMP":4.0,"VERIFY":3.5,"ORCH":3.0,"FAIL":4.0,"CTX":4.5,"META":3.0}' \
      --sessions "$HOME/vibe-sunsang/conversations/proj/2026-11-*.md" \
      --signals '{"context_specificity_ratio":0.62,"verification_ratio":0.1,"strategic_ratio":0.06}'
출력: JSON (raw_score, official_level, gates, weighted 등)
"""

import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

DIMS = ("DECOMP", "VERIFY", "ORCH", "FAIL", "CTX", "META")
DEFAULT_WEIGHTS = (
    Path(__file__).resolve().parent.parent
    / "skills" / "vibe-sunsang-knowledge" / "references" / "common" / "weights.md"
)
_COND_RE = re.compile(r"^\s*([a-z_]+)\s*(>=|<=|>|<|==)\s*(-?[\d.]+)\s*$")


def _parse_scalar(text: str):
    text = text.strip().strip('"').strip("'")
    try:
        return float(text) if "." in text else int(text)
    except ValueError:
        return text


def load_rubric(path: Path) -> dict:
    """weights.md frontmatter(제한된 YAML: 인라인 맵·인라인 리스트)를 읽는다."""
    lines = path.read_text(encoding="utf-8").split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"frontmatter 없음: {path}")
    data, section = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.rstrip()
        if not stripped.strip() or stripped.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            section = stripped.rstrip(":").strip()
            data[section] = {}
            continue
        key, _, value = stripped.strip().partition(":")
        value = value.strip()
        if value.startswith("{"):
            data[section][key] = {
                k.strip(): _parse_scalar(v)
                for k, v in (item.split(":", 1) for item in value.strip("{}").split(","))
            }
        elif value.startswith("["):
            data[section][key] = json.loads(value)
        else:
            data[section][key] = _parse_scalar(value)
    for t, w in data.get("weights", {}).items():
        total = sum(w[d] for d in DIMS)
        if not math.isclose(total, 1.0, abs_tol=1e-6):
            raise ValueError(f"{t} 가중치 합이 1이 아님: {total}")
    return data


def round_half(raw: float) -> float:
    base = math.floor(raw)
    frac = round(raw - base, 2)
    if frac < 0.25:
        return float(base)
    if frac < 0.75:
        return base + 0.5
    return float(base + 1)


def aggregate_sessions(patterns) -> dict:
    """변환된 세션 md frontmatter의 숫자 지표를 기간 합계로 모은다."""
    totals, count = {}, 0
    files = sorted({f for p in patterns for f in glob.glob(str(Path(p).expanduser()))})
    for f in files:
        if Path(f).name == "INDEX.md":
            continue
        text = Path(f).read_text(encoding="utf-8").split("\n")
        if not text or text[0].strip() != "---":
            continue
        count += 1
        for line in text[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if not sep or key.startswith(" "):
                continue
            value = value.strip()
            if value in ("true", "false"):
                totals[key] = totals.get(key, 0) + (value == "true")
            elif re.fullmatch(r"-?\d+", value):
                totals[key] = totals.get(key, 0) + int(value)
    totals["session_count"] = count
    return totals


def eval_condition(cond: str, signals: dict) -> bool:
    for alt in cond.split("|"):
        m = _COND_RE.match(alt)
        if not m:
            raise ValueError(f"게이트 조건 해석 불가: {alt!r}")
        key, op, num = m.group(1), m.group(2), float(m.group(3))
        val = signals.get(key)
        if val is None:
            continue
        if {">": val > num, ">=": val >= num, "<": val < num, "<=": val <= num, "==": val == num}[op]:
            return True
    return False


def compute(rubric: dict, wtype: str, scores: dict, signals: dict) -> dict:
    weights = rubric["weights"][wtype]
    missing = [d for d in DIMS if d not in scores]
    if missing:
        raise ValueError(f"축 점수 누락: {missing}")
    weighted = {d: round(weights[d] * float(scores[d]), 4) for d in DIMS}
    raw = round(sum(weighted.values()), 2)
    level = round_half(raw)

    sessions = signals.get("session_count", 0)
    floor = rubric.get("floor", {})
    if sessions >= 3:
        level = max(level, float(floor.get("three_sessions", 2.0)))
    elif sessions >= 1:
        level = max(level, float(floor.get("first_session", 1.5)))

    gates, cap = {}, 7.0
    for name in sorted(rubric.get("gates", {}), key=lambda g: int(g[1:])):
        n = int(name[1:])
        conds = rubric["gates"][name]
        passed = all(eval_condition(c, signals) for c in conds)
        gates[name] = {"passed": passed, "conditions": conds}
        if not passed and cap == 7.0:
            cap = n - 0.5
    official = min(level, cap)
    return {
        "type": wtype,
        "weights": weights,
        "weighted": weighted,
        "raw_score": raw,
        "rounded_level": level,
        "gate_cap": cap,
        "official_level": official,
        "gates": gates,
        "signals_used": signals,
    }


def _load_json_arg(value: str) -> dict:
    if not value:
        return {}
    p = Path(value).expanduser()
    return json.loads(p.read_text(encoding="utf-8") if p.exists() else value)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="vibe-sunsang Fit Score 계산기")
    ap.add_argument("--type", required=True, choices=["builder", "explorer", "designer", "operator"])
    ap.add_argument("--scores", required=True, help='축 점수 JSON 또는 파일 경로 ({"DECOMP":4.0,...})')
    ap.add_argument("--signals", default="", help="게이트용 비율 지표 JSON 또는 파일 (세션 합계를 덮어씀)")
    ap.add_argument("--sessions", nargs="*", default=[], help="변환된 세션 md glob (frontmatter 합계)")
    ap.add_argument("--weights-file", type=Path, default=DEFAULT_WEIGHTS)
    args = ap.parse_args(argv)
    try:
        rubric = load_rubric(args.weights_file)
        signals = aggregate_sessions(args.sessions)
        signals.update(_load_json_arg(args.signals))
        result = compute(rubric, args.type, _load_json_arg(args.scores), signals)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
