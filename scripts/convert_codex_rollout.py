#!/usr/bin/env python3
"""
Codex 세션 JSONL → Markdown 변환기 (convert_sessions.py의 Codex rollout 판)
- Codex rollout 로그(~/.codex/sessions/**/*.jsonl)를 작업 디렉토리(cwd) 단위 프로젝트로 묶어
  읽기 좋은 Markdown으로 변환
- 도구 호출은 한 줄 요약, 사람-AI 대화는 전문 보존
- 메타데이터·v2 P0 지표를 프론트매터로 포함 (본진 변환기와 동일한 출력 계약 —
  analysis_scope.py / growth / mentor 스킬이 그대로 소비한다)
"""

import argparse
import json
import os
import platform
import re
import sys
from datetime import datetime
from pathlib import Path

# Claude 변환기와 같은 v2.4 신호 정의를 공유한다 (출력 계약 동일)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_sessions import (  # noqa: E402
    SIGNAL_KEYS, DELEGATION_KEYS, _VERIFY_CMD_RE, _DONE_CRITERIA_RE, _HANDOFF_RE,
)


def _is_wsl() -> bool:
    try:
        return "microsoft" in platform.uname().release.lower()
    except Exception:
        return False


def _wsl_windows_sessions() -> Path | None:
    """WSL 환경에서 Windows 측 Codex 세션 디렉토리 추정."""
    user = os.environ.get("USER")
    if not user:
        return None
    candidate = Path("/mnt/c/Users") / user / ".codex" / "sessions"
    return candidate if candidate.exists() else None


def resolve_sessions_dir(override: Path | None = None) -> Path:
    """Codex 세션 디렉토리 결정.

    우선순위:
        1. override (--sessions-dir CLI 플래그)
        2. $CODEX_HOME/sessions (Codex 공식 컨벤션)
        3. ~/.codex/sessions (기본값, 존재 시)
        4. WSL 환경: /mnt/c/Users/$USER/.codex/sessions (폴백)
        5. 기본값 (~/.codex/sessions) — 호출부에서 부재 안내
    """
    if override:
        return override.expanduser()
    if env := os.environ.get("CODEX_HOME"):
        return Path(env).expanduser() / "sessions"
    default = Path.home() / ".codex" / "sessions"
    if default.exists():
        return default
    if _is_wsl() and (wsl_path := _wsl_windows_sessions()):
        return wsl_path
    return default


SESSIONS_DIR = resolve_sessions_dir()
DEFAULT_OUTPUT_DIR = Path.home() / "vibe-sunsang" / "conversations"
DEFAULT_NAMES_FILE = Path.home() / "vibe-sunsang" / "config" / "project_names.json"

# 오케스트레이션(멀티에이전트) 도구: Codex collaboration 네임스페이스 + 흔한 이름
ORCH_TOOLS = {"spawn_agent", "spawn_agents", "send_message", "wait_agent", "wait", "close_agent", "list_agents"}
ORCH_NAMESPACES = {"collaboration", "multi_agent"}

# 사용자 role로 기록되지만 사람이 쓴 게 아닌 주입 컨텍스트(환경 정보, AGENTS.md, 권한 안내 등)
INJECTED_USER_PREFIX = re.compile(r"^\s*<[a-z_]+(\s[^>]*)?>", re.IGNORECASE)

# 도구 결과에서 실패로 간주할 신호
ERROR_SIGNALS = re.compile(
    r"(Script failed|Script error|exit(?:ed)?(?: with)? code[:= ]+[1-9]\d*|"
    r"\"exit_code\"\s*:\s*[1-9]\d*|Traceback \(most recent call last\)|command not found)",
    re.IGNORECASE,
)


def _preview(value, limit: int = 80) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = text.replace("\n", " ").strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _tool_summary(name: str, args) -> str:
    """도구 호출 한 줄 요약. 셸/패치류는 핵심 인자만 보여준다."""
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            parsed = None
    else:
        parsed = args
    if isinstance(parsed, dict):
        for key in ("cmd", "command", "path", "file_path", "pattern", "query", "url", "prompt", "target", "description"):
            if key in parsed and parsed[key]:
                val = parsed[key]
                if isinstance(val, list):
                    val = " ".join(str(v) for v in val)
                return f"*[Tool: {name} → `{_preview(val)}`]*"
        return f"*[Tool: {name}]*"
    if isinstance(args, str) and args.strip():
        return f"*[Tool: {name} → `{_preview(args)}`]*"
    return f"*[Tool: {name}]*"


def load_project_names(names_file: Path) -> dict:
    """Load project name mappings (cwd → display name) from JSON config file."""
    if names_file.exists():
        try:
            with open(names_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_project_name(cwd: str, project_names: dict) -> str:
    """cwd(프로젝트 키)를 사람이 읽기 좋은 이름으로 변환."""
    if cwd in project_names:
        return project_names[cwd]
    base = Path(cwd).name if cwd else ""
    name = re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", base).replace("-", "_").lower().strip("_")
    return name or "unknown"


def build_display_names(groups: dict, project_names: dict) -> dict:
    """cwd → 표시 이름. 자동 생성 이름이 충돌하면(같은 폴더명이 다른 경로에) 부모 폴더명을 붙여 구분한다.

    명시 매핑(project_names.json)은 그대로 존중한다.
    """
    names = {cwd: get_project_name(cwd, project_names) for cwd in groups}
    by_name: dict = {}
    for cwd, name in names.items():
        by_name.setdefault(name, []).append(cwd)
    for name, cwds in by_name.items():
        if len(cwds) < 2:
            continue
        # 세션 수가 가장 많은 cwd가 짧은 이름을 가져가고, 나머지는 부모 폴더명을 접두로 붙인다
        cwds_sorted = sorted(cwds, key=lambda c: len(groups[c]), reverse=True)
        for cwd in cwds_sorted[1:]:
            if cwd in project_names:
                continue
            parent = Path(cwd).parent.name
            parent = re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", parent).replace("-", "_").lower().strip("_")
            names[cwd] = f"{parent}_{name}" if parent else name
    return names


def _resolve_target(value: str, display_names: dict) -> list:
    """--project 인자 해석: cwd 키면 그대로, 표시 이름이면 역매핑(동명이면 전부).

    스킬은 INDEX.md의 표시 이름을 넘기지만 세션은 cwd로 묶인다. 불일치를 여기서 흡수한다.
    """
    if value in display_names:
        return [value]
    expanded = str(Path(value).expanduser())
    if expanded in display_names:
        return [expanded]
    return [cwd for cwd, name in display_names.items() if name == value]


def _content_text(content) -> str:
    """Codex message content(list of {type,text}) → 텍스트."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text") or item.get("input_text") or item.get("output_text")
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts).strip()


def _output_text(output) -> str:
    """function_call_output / custom_tool_call_output의 output → 텍스트."""
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        return _content_text(output)
    if isinstance(output, dict):
        return json.dumps(output, ensure_ascii=False)
    return ""


def format_timestamp(ts) -> str:
    """타임스탬프를 읽기 좋은 형태로"""
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return ts
    if isinstance(ts, (int, float)):
        try:
            if ts > 1e12:  # milliseconds
                dt = datetime.utcfromtimestamp(ts / 1000)
            else:
                dt = datetime.utcfromtimestamp(ts)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(ts)
    return str(ts)


def get_session_date(ts) -> str:
    """타임스탬프에서 날짜만 추출"""
    formatted = format_timestamp(ts)
    if re.match(r"^\d{4}-\d{2}-\d{2}", formatted):
        return formatted[:10]
    return "unknown-date"


def read_session_meta(jsonl_path: Path) -> dict:
    """세션 첫 부분만 읽어 id·cwd·시작 시각을 얻는다 (그룹핑용, 전체 파싱 없이)."""
    meta = {"session_id": None, "cwd": None, "timestamp": None}
    try:
        with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i > 50 and meta["cwd"]:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = entry.get("payload") or {}
                if entry.get("type") == "session_meta":
                    meta["session_id"] = payload.get("id") or payload.get("session_id")
                    meta["cwd"] = payload.get("cwd") or meta["cwd"]
                    meta["timestamp"] = payload.get("timestamp") or entry.get("timestamp")
                elif entry.get("type") == "turn_context" and not meta["cwd"]:
                    meta["cwd"] = payload.get("cwd")
                if meta["session_id"] and meta["cwd"]:
                    break
    except OSError:
        pass
    if not meta["session_id"]:
        stem = jsonl_path.stem
        m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", stem)
        meta["session_id"] = m.group(1) if m else stem
    return meta


def group_sessions(sessions_dir: Path) -> dict:
    """세션 파일들을 cwd → [jsonl_path, ...]로 묶는다."""
    groups: dict = {}
    for jsonl in sorted(sessions_dir.rglob("*.jsonl")):
        meta = read_session_meta(jsonl)
        cwd = meta["cwd"] or "unknown"
        groups.setdefault(cwd, []).append(jsonl)
    return groups


def convert_session(jsonl_path: Path, verbose: bool = False) -> dict:
    """단일 Codex rollout JSONL을 파싱"""
    messages = []
    metadata = {
        "session_id": jsonl_path.stem,
        "models_used": set(),
        "tools_used": set(),
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "start_time": None,
        "end_time": None,
        "git_branch": None,
        "cwd": None,
    }

    # --- v2 P0 지표 수집용 카운터 ---
    user_msg_lengths = []      # 실제 사용자 발화 글자 수
    user_turn_count = 0        # 주입 컨텍스트 제외 사용자 발화 턴 수
    bypass_turns = 0           # 승인 없이(approval never / full-access sandbox) 돈 턴 수
    turn_count = 0             # turn_context 수 (bypass 비율 분모)
    orch_tool_count = 0        # 멀티에이전트(collaboration) 도구 호출 수
    tool_error_count = 0       # 실패 신호가 있는 도구 결과 수
    compact_count = 0          # 컨텍스트 압축(compacted) 수
    assistant_turn_count = 0   # assistant 메시지 수
    thinking_turn_count = 0    # 직전에 reasoning 항목이 있던 assistant 메시지 수
    sig = {k: 0 for k in SIGNAL_KEYS}  # v2.4 신호 (Codex에서 관측 가능한 것만 채운다)
    saw_reasoning = False
    pending_tool_lines = []    # assistant 메시지 앞에 붙일 도구 요약들
    last_total_usage = None

    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")
            payload = entry.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}
            timestamp = entry.get("timestamp", "")

            if metadata["start_time"] is None and timestamp:
                metadata["start_time"] = timestamp
            if timestamp:
                metadata["end_time"] = timestamp

            if entry_type == "session_meta":
                metadata["session_id"] = payload.get("id") or payload.get("session_id") or metadata["session_id"]
                if payload.get("cwd"):
                    metadata["cwd"] = payload["cwd"]
                if payload.get("timestamp"):
                    metadata["start_time"] = payload["timestamp"]
                continue

            if entry_type == "turn_context":
                turn_count += 1
                if payload.get("cwd"):
                    metadata["cwd"] = payload["cwd"]
                if payload.get("model"):
                    metadata["models_used"].add(payload["model"])
                sandbox = payload.get("sandbox_policy") or {}
                if payload.get("approval_policy") == "never" or sandbox.get("type") == "danger-full-access":
                    bypass_turns += 1
                continue

            if entry_type == "compacted":
                compact_count += 1
                continue

            if entry_type == "event_msg":
                if payload.get("type") == "token_count":
                    info = payload.get("info") or {}
                    total = info.get("total_token_usage")
                    if isinstance(total, dict):
                        last_total_usage = total
                continue

            if entry_type != "response_item":
                continue

            ptype = payload.get("type")

            if ptype == "reasoning":
                saw_reasoning = True
                continue

            if ptype in ("function_call", "custom_tool_call", "local_shell_call", "web_search_call"):
                name = payload.get("name") or ptype.replace("_call", "")
                namespace = payload.get("namespace") or ""
                if ptype == "local_shell_call":
                    action = payload.get("action") or {}
                    args = {"command": action.get("command")}
                    name = "shell"
                elif ptype == "web_search_call":
                    args = payload.get("action") or {}
                    name = "web_search"
                else:
                    args = payload.get("arguments") if ptype == "function_call" else payload.get("input")
                metadata["tools_used"].add(name)
                _cmd = (args.get("command") or args.get("cmd")) if isinstance(args, dict) else args
                if isinstance(_cmd, str) and _cmd.lstrip().startswith("{"):
                    try:
                        _j = json.loads(_cmd)
                        _cmd = _j.get("cmd") or _j.get("command") if isinstance(_j, dict) else _cmd
                    except json.JSONDecodeError:
                        pass
                if isinstance(_cmd, list):
                    _cmd = " ".join(str(c) for c in _cmd)
                if isinstance(_cmd, str) and _VERIFY_CMD_RE.search(_cmd):
                    sig["verify_cmd_count"] += 1
                if name in ORCH_TOOLS or namespace in ORCH_NAMESPACES:
                    orch_tool_count += 1
                pending_tool_lines.append(_tool_summary(name, args))
                continue

            if ptype in ("function_call_output", "custom_tool_call_output"):
                out_text = _output_text(payload.get("output"))
                if out_text and ERROR_SIGNALS.search(out_text[:2000]):
                    tool_error_count += 1
                if out_text.strip():
                    if verbose:
                        pending_tool_lines.append(f"\n> *[Result]:*\n> {out_text}\n")
                    else:
                        pending_tool_lines.append(f"\n> *[Result]: {_preview(out_text, 200)}*\n")
                continue

            if ptype == "agent_message":
                # 에이전트 간 메시지 = 멀티에이전트 오케스트레이션 신호
                orch_tool_count += 1
                continue

            if ptype != "message":
                continue

            role = payload.get("role", "")
            text = _content_text(payload.get("content"))
            if not text:
                continue

            if role == "user":
                if INJECTED_USER_PREFIX.match(text):
                    continue  # 환경 컨텍스트/AGENTS.md 주입 — 사람 발화 아님
                # 사용자 발화 전에 쌓인 도구 요약은 앞선 assistant 턴에 귀속
                if pending_tool_lines and messages and messages[-1]["role"] == "assistant":
                    messages[-1]["content"] += "\n" + "\n".join(pending_tool_lines)
                pending_tool_lines = []
                user_turn_count += 1
                if _DONE_CRITERIA_RE.search(text):
                    sig["done_criteria_count"] += 1
                if _HANDOFF_RE.search(text):
                    sig["handoff_count"] += 1
                user_msg_lengths.append(len(text))
                messages.append({"role": "user", "content": text, "time": format_timestamp(timestamp)})
            elif role == "assistant":
                assistant_turn_count += 1
                if saw_reasoning:
                    thinking_turn_count += 1
                saw_reasoning = False
                body = text
                if pending_tool_lines:
                    body = "\n".join(pending_tool_lines) + "\n\n" + text
                    pending_tool_lines = []
                messages.append({"role": "assistant", "content": body, "time": format_timestamp(timestamp)})
            # developer/system role은 무시

    if pending_tool_lines and messages and messages[-1]["role"] == "assistant":
        messages[-1]["content"] += "\n" + "\n".join(pending_tool_lines)

    if last_total_usage:
        metadata["total_input_tokens"] = int(last_total_usage.get("input_tokens", 0) or 0)
        metadata["total_output_tokens"] = int(last_total_usage.get("output_tokens", 0) or 0)

    metadata["models_used"] = sorted(metadata["models_used"])
    metadata["tools_used"] = sorted(metadata["tools_used"])
    metadata["message_count"] = len(messages)

    # --- v2 P0 지표 계산 (본진과 동일한 필드명) ---
    metadata["avg_user_msg_len"] = (
        round(sum(user_msg_lengths) / len(user_msg_lengths)) if user_msg_lengths else 0
    )
    metadata["user_turn_count"] = user_turn_count
    metadata["bypass_permission_ratio"] = (
        round(bypass_turns / turn_count, 2) if turn_count > 0 else 0.0
    )
    metadata["has_orchestration"] = orch_tool_count > 0
    metadata["orch_tool_count"] = orch_tool_count
    metadata["tool_error_count"] = tool_error_count
    metadata["compact_boundaries"] = compact_count
    metadata.update(sig)
    metadata["delegation_total"] = orch_tool_count + sum(sig[k] for k in DELEGATION_KEYS)
    metadata["thinking_turn_ratio"] = (
        round(thinking_turn_count / assistant_turn_count, 2) if assistant_turn_count > 0 else 0.0
    )

    return {"messages": messages, "metadata": metadata}


def session_to_markdown(session_data: dict, project_name: str) -> str:
    """파싱된 세션을 Markdown으로 변환"""
    meta = session_data["metadata"]
    messages = session_data["messages"]

    if not messages:
        return ""

    date = get_session_date(meta["start_time"])

    lines = []
    lines.append("---")
    lines.append(f"project: {project_name}")
    lines.append(f"session_id: {meta['session_id']}")
    lines.append(f"date: {date}")
    lines.append(f"start: {format_timestamp(meta['start_time'])}")
    lines.append(f"end: {format_timestamp(meta['end_time'])}")

    if meta["models_used"]:
        lines.append("models:")
        for m in meta["models_used"]:
            lines.append(f"  - {m}")
    else:
        lines.append("models: unknown")

    if meta["tools_used"]:
        lines.append("tools:")
        for t in meta["tools_used"]:
            lines.append(f"  - {t}")
    else:
        lines.append("tools: none")

    lines.append(f"messages: {meta['message_count']}")
    lines.append(f"input_tokens: {meta['total_input_tokens']}")
    lines.append(f"output_tokens: {meta['total_output_tokens']}")
    if meta["git_branch"]:
        lines.append(f"git_branch: {meta['git_branch']}")
    if meta["cwd"]:
        lines.append(f"working_dir: {meta['cwd']}")

    lines.append(f"avg_user_msg_len: {meta['avg_user_msg_len']}")
    lines.append(f"user_turn_count: {meta['user_turn_count']}")
    lines.append(f"bypass_permission_ratio: {meta['bypass_permission_ratio']}")
    lines.append(f"has_orchestration: {str(meta['has_orchestration']).lower()}")
    lines.append(f"orch_tool_count: {meta['orch_tool_count']}")
    lines.append(f"tool_error_count: {meta['tool_error_count']}")
    lines.append(f"compact_boundaries: {meta['compact_boundaries']}")
    lines.append(f"thinking_turn_ratio: {meta['thinking_turn_ratio']}")
    for key in SIGNAL_KEYS:
        lines.append(f"{key}: {meta[key]}")
    lines.append(f"delegation_total: {meta['delegation_total']}")
    lines.append("---")
    lines.append("")

    first_msg = messages[0]["content"][:80].replace("\n", " ")
    lines.append(f"# {date} | {project_name}")
    lines.append(f"> 첫 메시지: {first_msg}...")
    lines.append("")

    for msg in messages:
        if msg["role"] == "user":
            lines.append(f"## User ({msg['time']})")
        else:
            lines.append(f"## Assistant ({msg['time']})")
        lines.append("")
        lines.append(msg["content"])
        lines.append("")

    return "\n".join(lines)


def _short_id(session_id: str) -> str:
    """파일명용 짧은 id. Codex 세션 id는 UUIDv7(앞 8자가 시간)이라 같은 날 세션끼리 앞자리가 겹친다 →
    뒤쪽 무작위 12자를 쓴다."""
    compact = re.sub(r"[^0-9a-zA-Z]", "", session_id or "")
    return compact[-12:] if len(compact) >= 12 else (compact or "unknown")


def _has_current_schema(md_path: Path) -> bool:
    """v2.4 신호가 없는 옛 변환본이면 False → 증분 모드에서도 다시 변환한다."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("delegation_total:"):
                    return True
                if line.startswith("# "):
                    return False
    except OSError:
        pass
    return False


def _find_existing_output(output_dir: Path, short_id: str) -> Path | None:
    for f in output_dir.glob(f"*_{short_id}.md"):
        return f
    return None


def convert_project(
    project_name: str,
    jsonl_files: list,
    output_base: Path,
    force: bool = False,
    verbose: bool = False,
) -> int:
    """한 프로젝트(cwd)의 모든 세션을 변환"""
    output_dir = output_base / project_name
    dir_created = False

    converted = 0
    skipped = 0

    for jsonl_file in jsonl_files:
        try:
            meta = read_session_meta(jsonl_file)
            short_id = _short_id(meta["session_id"] or jsonl_file.stem)

            if not force and output_dir.exists():
                existing = _find_existing_output(output_dir, short_id)
                if existing and existing.stat().st_mtime >= jsonl_file.stat().st_mtime and _has_current_schema(existing):
                    skipped += 1
                    continue

            session_data = convert_session(jsonl_file, verbose=verbose)
            if not session_data["messages"]:
                continue

            md_content = session_to_markdown(session_data, project_name)
            if not md_content:
                continue

            if not dir_created:
                output_dir.mkdir(parents=True, exist_ok=True)
                dir_created = True

            date = get_session_date(session_data["metadata"]["start_time"])
            output_file = output_dir / f"{date}_{short_id}.md"
            output_file.write_text(md_content, encoding="utf-8")
            converted += 1
        except Exception as e:
            print(f"  [ERROR] {jsonl_file.name}: {e}")

    if output_dir.exists() and not any(output_dir.iterdir()):
        output_dir.rmdir()

    skip_msg = f", {skipped} skipped (up-to-date)" if skipped else ""
    print(f"  [{project_name}] {converted}/{len(jsonl_files)} 세션 변환 완료{skip_msg}")
    return converted


def _project_last_active(md_files) -> str | None:
    """프로젝트 내 세션들의 frontmatter `end`(마지막 활동) 중 최대 날짜(YYYY-MM-DD)."""
    latest = None
    for md in md_files:
        try:
            with open(md, "r", encoding="utf-8") as f:
                if f.readline().strip() != "---":
                    continue
                for line in f:
                    if line.strip() == "---":
                        break
                    if line.startswith("end:"):
                        day = line.split(":", 1)[1].strip()[:10]
                        if day and (latest is None or day > latest):
                            latest = day
                        break
        except OSError:
            continue
    return latest


def generate_index(output_base: Path):
    """전체 인덱스 파일 생성"""
    if not output_base.exists():
        print("\n[INDEX] No output directory, skipping index generation.")
        return

    lines = []
    lines.append("# 바선생 대화 회고록 (Codex)")
    lines.append(f"\n생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    total_sessions = 0
    project_stats = []

    for project_dir in sorted(output_base.iterdir()):
        if not project_dir.is_dir():
            continue
        md_files = sorted(project_dir.glob("*.md"))
        if not md_files:
            continue
        total_sessions += len(md_files)
        dates = [f.stem[:10] for f in md_files]
        last_active = _project_last_active(md_files) or max(dates)
        project_stats.append({
            "name": project_dir.name,
            "count": len(md_files),
            "first": min(dates),
            "last": max(dates),
            "last_active": last_active,
        })

    lines.append(f"**총 {total_sessions}개 세션** | {len(project_stats)}개 프로젝트\n")
    lines.append("| 프로젝트 | 세션 수 | 기간 | 최근 활동 |")
    lines.append("|----------|---------|------|----------|")

    for stat in sorted(project_stats, key=lambda x: (x["last_active"], x["count"]), reverse=True):
        lines.append(
            f"| [{stat['name']}](./{stat['name']}/) | {stat['count']} | "
            f"{stat['first']} ~ {stat['last']} | {stat['last_active']} |"
        )

    lines.append("\n---\n")
    lines.append("바선생과 함께 과거 대화를 분석하고 회고할 수 있습니다.")

    index_path = output_base / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[INDEX] {index_path} 생성 완료 (총 {total_sessions}개 세션)")


def list_projects(groups: dict, display_names: dict) -> None:
    """온보딩용: 발견된 프로젝트(cwd)·세션 수·표시 이름을 TSV로 출력 (세션 수 내림차순)."""
    print("cwd\tsessions\tdisplay_name")
    for cwd, files in sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True):
        print(f"{cwd}\t{len(files)}\t{display_names[cwd]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex 세션 JSONL → Markdown 변환기")
    parser.add_argument("projects", nargs="*", help="특정 프로젝트(cwd 또는 표시 이름). 미지정 시 전체 변환")
    parser.add_argument("--force", action="store_true", help="Force full reconversion (ignore incremental cache)")
    parser.add_argument("--verbose", action="store_true", help="Include full tool results (not just 200 char preview)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Custom output directory path")
    parser.add_argument("--names-file", type=Path, default=None,
                        help="Path to project_names.json (default: ~/vibe-sunsang/config/project_names.json)")
    parser.add_argument("--project", type=str, default=None,
                        help="Convert a specific project only (cwd or display name from INDEX.md)")
    parser.add_argument("--sessions-dir", "--projects-dir", dest="sessions_dir", type=Path, default=None,
                        help="Codex 세션 디렉토리 직접 지정 (기본 우선순위: $CODEX_HOME/sessions → ~/.codex/sessions → WSL fallback)")
    parser.add_argument("--list-projects", action="store_true",
                        help="변환 없이 발견된 프로젝트(cwd)와 세션 수만 출력 (온보딩용)")
    return parser.parse_args()


def main():
    args = parse_args()

    output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR
    names_file = args.names_file if args.names_file else DEFAULT_NAMES_FILE

    global SESSIONS_DIR
    SESSIONS_DIR = resolve_sessions_dir(args.sessions_dir)

    if not SESSIONS_DIR.exists():
        print(
            f"[ERROR] Codex 세션 디렉토리를 찾지 못했습니다: {SESSIONS_DIR}\n"
            f"  - $CODEX_HOME: {os.environ.get('CODEX_HOME', '(unset)')}\n"
            f"  - WSL 감지: {_is_wsl()}\n"
            f"  --sessions-dir <경로> 로 직접 지정하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    project_names = load_project_names(names_file)
    groups = group_sessions(SESSIONS_DIR)
    display_names = build_display_names(groups, project_names)

    if args.list_projects:
        list_projects(groups, display_names)
        return

    requested = [args.project] if args.project else list(args.projects)
    if requested:
        targets = []
        for value in requested:
            matched = _resolve_target(value, display_names)
            if not matched:
                print(f"  [SKIP] {value} - 일치하는 프로젝트 없음")
            targets.extend(c for c in matched if c not in targets)
    else:
        targets = list(groups.keys())

    print("=== Codex 세션 → Markdown 변환 ===")
    print(f"소스: {SESSIONS_DIR}")
    print(f"출력: {output_dir}")
    print(f"이름 매핑: {names_file}")
    print(f"대상: {len(targets)}개 프로젝트")
    if args.force:
        print("모드: --force (전체 재변환)")
    if args.verbose:
        print("모드: --verbose (전체 도구 결과 포함)")
    print()

    total = 0
    for cwd in sorted(targets):
        total += convert_project(
            display_names[cwd],
            groups[cwd],
            output_dir,
            force=args.force,
            verbose=args.verbose,
        )

    generate_index(output_dir)
    print(f"\n=== 완료: 총 {total}개 세션 변환 ===")


if __name__ == "__main__":
    main()
