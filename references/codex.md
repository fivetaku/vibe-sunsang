# Codex에서 실행할 때 (vibe-sunsang)

SKILL.md 절차는 그대로 따르고, 아래 차이만 적용한다. 이 파일의 `<플러그인 루트>`는 이 파일에서 한 단계 위 폴더다.

## 질문 도구 (이번 세션 도구 목록으로 판단)

1. `request_user_input_async`가 있으면 질문 1콜 = 이 도구 1콜. 문항은 한 번에 ≤4개.
   - 형식: `{"questions":[{"title":"헤더 — 한 줄 질문","options":["추천안 (추천) — 설명","대안 — 설명"]}]}`
   - 문항에는 `title`·`options`(문자열 배열)만. `question`·`header`·`id`를 넣으면 파싱 오류가 난다. 추천안을 맨 앞에 두고 "기타" 옵션은 넣지 않는다.
   - 부른 뒤 "위 질문에 답해 주시면 이어서 진행합니다" 한 줄만 쓰고 턴을 끝낸다. 답은 다음 사용자 메시지로 온다.
2. Plan 모드라 `request_user_input`만 있으면: 1콜 3문항까지. `header`(12자 이내)·`id`(snake_case)·`question`, 선택지 2~3개(`label`·`description`), 추천 라벨 끝에 `(Recommended)`.
3. 둘 다 없으면 채팅에 번호 블록으로 낸다: `Q1. <질문>` 아래 `1. <추천안> (추천) — 설명`, `2. <대안>`, `3. 문장으로 직접 적기`, 끝에 `(답은 "Q1-1"처럼. 모르면 전부 1번으로 진행할게요)`.
4. `codex exec`처럼 사람이 답할 수 없는 실행이면 묻지 않고 추천안으로 진행하고, 가정한 내용을 결과에 적는다.

SKILL.md의 JSON 예시는 Claude Code용(`question`·`header`·`label`·`description`)이다. Codex에서는 그 내용(질문·선택지)을 위 형식으로 옮겨 쓴다. 프리뷰 필드는 쓰지 않는다.

## 대화 기록 변환기 고르기 (분기)

바선생이 읽는 원본이 다르다. 스크립트가 만드는 Markdown(프론트매터·파일 구조)은 같아서 `analysis_scope.py`·성장·멘토 스킬은 그대로 쓴다.

- Claude Code(기본): `scripts/convert_sessions.py` — 원본 `~/.claude/projects/**/*.jsonl`.
- Codex: `scripts/convert_codex_rollout.py` — 원본 `<codex 홈>/sessions/**/*.jsonl`(rollout).
- Codex 실행 판별: 플러그인 루트 경로가 `<codex 홈>/plugins/cache/<마켓>/<플러그인>/<버전>` 모양이고 `<codex 홈>/config.toml`이 있으며 `<codex 홈>/plugins/installed_plugins.json`은 없다. 이때 `<codex 홈>`은 루트에서 다섯 단계 위다(보통 `~/.codex`).
- SKILL.md의 `convert_sessions.py` 명령을 Codex에서는 `convert_codex_rollout.py`로 바꿔 실행하고, 인자(`--names-file`·`--output-dir`·`--force`·`--project`)는 그대로 쓴다. 원본 위치는 기본이 `$CODEX_HOME/sessions` 또는 `~/.codex/sessions`이고, 다르면 `--sessions-dir <경로>`로 준다. `--list-projects`로 프로젝트(작업 폴더 cwd 단위) 목록을 볼 수 있다.
- 두 변환기 출력이 같은 `~/vibe-sunsang/conversations/`에 섞이지 않게 하려면 도구별로 출력 폴더를 나눠도 된다(`--output-dir`).

## Codex에 없는 도구

- `Task`/`Agent`(성장 스킬의 `vibe-sunsang:growth-analyst` 위임): `agents/growth-analyst.md`는 Codex가 읽지 않는다. `spawn_agent`가 있으면 그 에이전트에게 "`<플러그인 루트>/agents/growth-analyst.md`의 본문(frontmatter 제외)을 읽고 따르라"와 SKILL.md가 넘기는 입력을 준다. 없으면 이 스킬이 같은 파일을 읽고 직접 분석한다. 결과물은 같다.
- `Skill`/다른 스킬 호출: `skills/<이름>/SKILL.md`를 열어 그 절차를 따른다.
- 첫 실행 설정(`setup/setup.sh`)은 Claude Code 전용이다. Codex에서는 실행해도 아무것도 하지 않으며, 별도 질문도 하지 않는다.
