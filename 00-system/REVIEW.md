# 바선생 (Vibe Sunsang) - 시스템 정보

## 버전
- v1.0.0 (2026-02-19)

## 요구사항
- Claude Code CLI
- Python 3.8+
- `~/.claude/projects/` 디렉토리에 Claude Code 대화 기록

## 구성 요소

| 이름 | 타입 | 설명 |
|------|------|------|
| `/onboard` | Command | 초기 설정 - 프로젝트 연결, 이름 매핑, 첫 변환 |
| `/retro` | Command | JSONL → Markdown 변환 + 분석 템플릿 제안 |
| `/mentor` | Skill | AI 활용 능력 코칭 (4모드: 요청품질/안티패턴/개념학습/종합코칭) |
| `/growth` | Skill→Agent | 성장 리포트 생성 (growth-analyst 에이전트에 위임) |

## 레벨 시스템

| Level | 이름 | 설명 |
|-------|------|------|
| 1 | Observer | "만들어줘"만 요청, 결과 무비판 수용 |
| 2 | Questioner | "왜?"라고 물음, 에러 메시지 읽기 시도 |
| 3 | Collaborator | 구체적 요구사항, 대안 질문, 에러 추측 |
| 4 | Orchestrator | 작업 분할 지시, 아키텍처 참여, 검증 주도 |
| 5 | Conductor | 멀티 에이전트 조율, 기술적 의사결정 |
