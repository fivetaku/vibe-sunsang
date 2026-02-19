#!/usr/bin/env python3
"""
Claude Code 세션 JSONL → Markdown 변환기
- 프로젝트별로 대화를 읽기 좋은 Markdown으로 변환
- 도구 사용 로그는 요약, 사람-AI 대화는 전문 보존
- 메타데이터를 프론트매터로 포함
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "40-conversations"

# PROJECT_NAMES: loaded from scripts/project_names.json, fallback to auto-generation
_PROJECT_NAMES_FILE = Path(__file__).parent / "project_names.json"


def _load_project_names() -> dict:
    """Load project name mappings from JSON config file."""
    if _PROJECT_NAMES_FILE.exists():
        try:
            with open(_PROJECT_NAMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


PROJECT_NAMES = _load_project_names()

# Tool formatters: maps tool name -> lambda(input_dict) -> summary string
TOOL_FORMATTERS = {
    "Read":      lambda i: f"*[Tool: Read → `{i.get('file_path', '?')}`]*",
    "Write":     lambda i: f"*[Tool: Write → `{i.get('file_path', '?')}`]*",
    "Edit":      lambda i: f"*[Tool: Edit → `{i.get('file_path', '?')}`]*",
    "Bash":      lambda i: f"*[Tool: Bash → `{i.get('command', '?')[:80]}`]*",
    "Grep":      lambda i: f"*[Tool: Grep → `{i.get('pattern', '?')}`]*",
    "Glob":      lambda i: f"*[Tool: Glob → `{i.get('pattern', '?')}`]*",
    "WebSearch": lambda i: f"*[Tool: WebSearch → `{i.get('query', '?')}`]*",
    "WebFetch":  lambda i: f"*[Tool: WebFetch → `{i.get('url', '?')}`]*",
    "Task":      lambda i: f"*[Tool: Task → `{i.get('description', '?')}`]*",
}


def get_project_name(dir_name: str) -> str:
    """프로젝트 디렉토리명을 사람이 읽기 좋은 이름으로 변환"""
    if dir_name in PROJECT_NAMES:
        return PROJECT_NAMES[dir_name]
    # 매핑에 없으면 자동 정리
    # -Users-{username}-{project} 패턴에서 프로젝트명만 추출
    import re
    name = re.sub(r"^-Users-[^-]+-", "", dir_name).replace("-", "_").lower()
    return name or "unknown"


def extract_text_content(content, verbose: bool = False) -> str:
    """메시지 content에서 텍스트만 추출"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_name = block.get("name", "unknown")
                    tool_input = block.get("input", {})
                    formatter = TOOL_FORMATTERS.get(tool_name)
                    if formatter:
                        texts.append(formatter(tool_input))
                    else:
                        texts.append(f"*[Tool: {tool_name}]*")
                elif block.get("type") == "tool_result":
                    result_content = block.get("content", "")
                    if isinstance(result_content, str) and result_content.strip():
                        if verbose:
                            texts.append(f"\n> *[Result]:*\n> {result_content}\n")
                        else:
                            preview = result_content[:200].replace("\n", " ")
                            if len(result_content) > 200:
                                preview += "..."
                            texts.append(f"\n> *[Result]: {preview}*\n")
        return "\n".join(texts)
    return str(content)


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
            else:  # seconds
                dt = datetime.utcfromtimestamp(ts)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(ts)
    return str(ts)


def get_session_date(ts) -> str:
    """타임스탬프에서 날짜만 추출"""
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return "unknown-date"
    if isinstance(ts, (int, float)):
        try:
            if ts > 1e12:  # milliseconds
                dt = datetime.utcfromtimestamp(ts / 1000)
            else:  # seconds
                dt = datetime.utcfromtimestamp(ts)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return "unknown-date"
    return "unknown-date"


def convert_session(jsonl_path: Path, verbose: bool = False) -> dict:
    """단일 세션 JSONL을 파싱"""
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

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")
            timestamp = entry.get("timestamp", "")

            # 메타데이터 수집
            if metadata["start_time"] is None and timestamp:
                metadata["start_time"] = timestamp
            if timestamp:
                metadata["end_time"] = timestamp

            if entry.get("gitBranch"):
                metadata["git_branch"] = entry["gitBranch"]
            if entry.get("cwd"):
                metadata["cwd"] = entry["cwd"]

            msg = entry.get("message", {})
            role = msg.get("role", entry_type)
            model = msg.get("model", "")

            if model:
                metadata["models_used"].add(model)

            # 토큰 수집
            usage = msg.get("usage", {})
            metadata["total_input_tokens"] += usage.get("input_tokens", 0)
            metadata["total_output_tokens"] += usage.get("output_tokens", 0)

            # 대화 내용 추출
            content = msg.get("content", "")
            if not content:
                continue

            text = extract_text_content(content, verbose=verbose)
            if not text or not text.strip():
                continue

            # 도구 이름 수집
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        metadata["tools_used"].add(block.get("name", "unknown"))

            if role in ("user", "human"):
                messages.append({
                    "role": "user",
                    "content": text,
                    "time": format_timestamp(timestamp),
                })
            elif role in ("assistant",):
                messages.append({
                    "role": "assistant",
                    "content": text,
                    "time": format_timestamp(timestamp),
                })

    metadata["models_used"] = sorted(metadata["models_used"])
    metadata["tools_used"] = sorted(metadata["tools_used"])
    metadata["message_count"] = len(messages)

    return {"messages": messages, "metadata": metadata}


def session_to_markdown(session_data: dict, project_name: str) -> str:
    """파싱된 세션을 Markdown으로 변환"""
    meta = session_data["metadata"]
    messages = session_data["messages"]

    if not messages:
        return ""

    date = get_session_date(meta["start_time"])

    lines = []

    # 프론트매터
    lines.append("---")
    lines.append(f"project: {project_name}")
    lines.append(f"session_id: {meta['session_id']}")
    lines.append(f"date: {date}")
    lines.append(f"start: {format_timestamp(meta['start_time'])}")
    lines.append(f"end: {format_timestamp(meta['end_time'])}")

    # models as YAML list
    if meta["models_used"]:
        lines.append("models:")
        for m in meta["models_used"]:
            lines.append(f"  - {m}")
    else:
        lines.append("models: unknown")

    # tools as YAML list
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
    lines.append("---")
    lines.append("")

    # 제목
    first_msg = messages[0]["content"][:80].replace("\n", " ")
    lines.append(f"# {date} | {project_name}")
    lines.append(f"> 첫 메시지: {first_msg}...")
    lines.append("")

    # 대화 내용
    for msg in messages:
        if msg["role"] == "user":
            lines.append(f"## User ({msg['time']})")
        else:
            lines.append(f"## Assistant ({msg['time']})")

        lines.append("")
        lines.append(msg["content"])
        lines.append("")

    return "\n".join(lines)


def _find_existing_output(output_dir: Path, short_id: str) -> Path | None:
    """Find an existing markdown file matching the short_id pattern."""
    for f in output_dir.glob(f"*_{short_id}.md"):
        return f
    return None


def convert_project(
    project_dir: str,
    output_base: Path,
    project_name: str = None,
    force: bool = False,
    verbose: bool = False,
):
    """프로젝트 디렉토리의 모든 세션을 변환"""
    project_path = CLAUDE_PROJECTS_DIR / project_dir
    if not project_path.exists():
        print(f"  [SKIP] {project_dir} - 디렉토리 없음")
        return 0

    if project_name is None:
        project_name = get_project_name(project_dir)

    output_dir = output_base / project_name
    # Delay mkdir until first successful conversion
    dir_created = False

    jsonl_files = sorted(project_path.glob("*.jsonl"))
    converted = 0
    skipped = 0

    for jsonl_file in jsonl_files:
        try:
            short_id = jsonl_file.stem[:8]

            # Incremental conversion: skip if output already exists and is up-to-date
            if not force and output_dir.exists():
                existing = _find_existing_output(output_dir, short_id)
                if existing and existing.stat().st_mtime >= jsonl_file.stat().st_mtime:
                    skipped += 1
                    continue

            session_data = convert_session(jsonl_file, verbose=verbose)
            if not session_data["messages"]:
                continue

            md_content = session_to_markdown(session_data, project_name)
            if not md_content:
                continue

            # Create directory on first successful conversion
            if not dir_created:
                output_dir.mkdir(parents=True, exist_ok=True)
                dir_created = True

            date = get_session_date(session_data["metadata"]["start_time"])
            output_file = output_dir / f"{date}_{short_id}.md"
            output_file.write_text(md_content, encoding="utf-8")
            converted += 1
        except Exception as e:
            print(f"  [ERROR] {jsonl_file.name}: {e}")

    # Remove directory if it exists but is empty (no conversions happened)
    if output_dir.exists() and not any(output_dir.iterdir()):
        output_dir.rmdir()

    skip_msg = f", {skipped} skipped (up-to-date)" if skipped else ""
    print(f"  [{project_name}] {converted}/{len(jsonl_files)} 세션 변환 완료{skip_msg}")
    return converted


def generate_index(output_base: Path):
    """전체 인덱스 파일 생성"""
    if not output_base.exists():
        print("\n[INDEX] No output directory, skipping index generation.")
        return

    lines = []
    lines.append("# Claude Code 대화 회고록")
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

        # 날짜 범위 추출
        dates = [f.stem[:10] for f in md_files]
        project_stats.append({
            "name": project_dir.name,
            "count": len(md_files),
            "first": min(dates),
            "last": max(dates),
        })

    lines.append(f"**총 {total_sessions}개 세션** | {len(project_stats)}개 프로젝트\n")
    lines.append("| 프로젝트 | 세션 수 | 기간 |")
    lines.append("|----------|---------|------|")

    for stat in sorted(project_stats, key=lambda x: -x["count"]):
        lines.append(
            f"| [{stat['name']}](./{stat['name']}/) | {stat['count']} | {stat['first']} ~ {stat['last']} |"
        )

    lines.append("\n---\n")
    lines.append("이 워크스페이스에서 Claude Code를 실행하면 과거 대화를 분석하고 회고할 수 있습니다.")

    index_path = output_base / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[INDEX] {index_path} 생성 완료 (총 {total_sessions}개 세션)")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Claude Code 세션 JSONL → Markdown 변환기",
    )
    parser.add_argument(
        "projects",
        nargs="*",
        help="특정 프로젝트 디렉토리명 (미지정 시 전체 변환)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force full reconversion (ignore incremental cache)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include full tool results (not just 200 char preview)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Custom output directory path",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Convert a specific project only (by directory name)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    output_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR

    # Build target list: --project flag, positional args, or all projects
    if args.project:
        targets = [args.project]
    elif args.projects:
        targets = args.projects
    else:
        # 전체 프로젝트
        targets = [d.name for d in CLAUDE_PROJECTS_DIR.iterdir() if d.is_dir()]

    print(f"=== Claude Code 세션 → Markdown 변환 ===")
    print(f"소스: {CLAUDE_PROJECTS_DIR}")
    print(f"출력: {output_dir}")
    print(f"대상: {len(targets)}개 프로젝트")
    if args.force:
        print(f"모드: --force (전체 재변환)")
    if args.verbose:
        print(f"모드: --verbose (전체 도구 결과 포함)")
    print()

    total = 0
    for target in sorted(targets):
        total += convert_project(
            target,
            output_dir,
            force=args.force,
            verbose=args.verbose,
        )

    generate_index(output_dir)
    print(f"\n=== 완료: 총 {total}개 세션 변환 ===")


if __name__ == "__main__":
    main()
