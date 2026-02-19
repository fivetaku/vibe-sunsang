# 바선생 (Vibe Sunsang)

바이브코더를 위한 AI 협업 성장 워크스페이스.

Claude Code와 나눈 대화를 돌아보고, **더 잘 요청하는 법**을 배우는 공간입니다.

---

## 이런 분을 위한 도구입니다

- 개발 지식 없이 AI로 코딩하는 **바이브코더**
- "나는 뭘 잘못하고 있는 거지?" 궁금한 사람
- 매주 내가 한 작업을 돌아보며 **AI 활용 실력을 키우고 싶은** 사람

---

## 설치 방법

### 1. 이 저장소를 다운로드합니다

```bash
git clone https://github.com/fivetaku/vibe-sunsang
```

### 2. 이 폴더에서 Claude Code를 실행합니다

```bash
cd vibe-sunsang
claude
```

### 3. 초기 설정을 시작합니다

```
/onboard
```

끝! 온보딩이 프로젝트 연결, 이름 지정, 첫 변환을 모두 안내합니다.

---

## 사용법

매주 금요일, 이 폴더에서 `claude`를 실행하고:

| 명령어 | 설명 |
|--------|------|
| `/retro` | 이번 주 대화를 변환하고 분석 가이드 제공 |
| `멘토링해줘` | AI 활용 능력 코칭 (요청 품질, 안티패턴, 개념 학습) |
| `성장 리포트 만들어줘` | 레벨 판정 + 성장 분석 리포트 자동 생성 |

### 추천 루틴

```
1. /retro          ← 이번 주 대화 변환
2. 멘토링해줘       ← 이번 주 리뷰
3. 성장 리포트      ← 월 1회 성장 체크
```

---

## 레벨 시스템

바선생은 당신의 AI 활용 수준을 5단계로 진단합니다:

| Level | 이름 | 특징 |
|-------|------|------|
| 1 | **Observer** | "만들어줘"만 요청, 결과를 그대로 수용 |
| 2 | **Questioner** | "왜?"라고 물어보기 시작, 에러를 읽어보려 함 |
| 3 | **Collaborator** | 구체적으로 요청, 대안을 질문, 에러 원인 추측 |
| 4 | **Orchestrator** | 작업을 나눠서 지시, 검증을 직접 주도 |
| 5 | **Conductor** | 여러 AI를 조율, 기술적 의사결정 참여 |

---

## 기능 구성

```
vibe-sunsang/
├── CLAUDE.md                      ← 워크스페이스 가이드
├── .claude/
│   ├── commands/onboard.md        ← /onboard (초기 설정)
│   ├── commands/retro.md          ← /retro (변환 + 분석)
│   ├── skills/mentor/SKILL.md     ← 멘토링 코칭
│   ├── skills/growth/SKILL.md     ← 성장 리포트
│   └── agents/growth-analyst.md   ← 분석 서브에이전트
├── 10-scripts/                    ← 변환 스크립트
├── 20-knowledge-base/             ← 성장 지식 베이스 (6개 문서)
├── 40-conversations/              ← 변환된 대화 (자동 생성)
└── 90-exports/                    ← 리포트 저장 (자동 생성)
```

---

## 요구사항

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.8+

---

## Claude Code에게 설치 요청하기

이미 Claude Code를 사용 중이라면, 아무 프로젝트에서 이렇게 말해보세요:

> "이 저장소의 URL 이 저장소를 내 홈 디렉토리에 클론하고, 폴더로 이동해서 /onboard 실행해줘"

---

## 라이선스

MIT
