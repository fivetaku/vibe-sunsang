---
name: vibe-sunsang
description: "바선생 — AI 활용 성장 멘토 에이전트. 인자(시작·변환·멘토링·성장·지식)에 따라 해당 스킬로 분기한다."
---

<!-- first-run setup: Claude Code는 commands/vibe-sunsang.md의 Step 0이 처리한다. -->

## 실행 환경 (Claude Code / Codex)

- **Claude Code**: `AskUserQuestion`으로 묻는다.
- **Codex**: 시작 전에 이 플러그인 루트(이 SKILL.md에서 두 단계 위 폴더)의 `references/codex.md`를 읽는다. async 호출 형식: `{"questions":[{"title":"헤더 — 질문","options":["추천안 (추천) — 설명","대안 — 설명"]}]}` — 문항에는 `title`·`options`만, `question`·`header`·`id`는 넣지 않는다.
- Codex에서는 `${CLAUDE_PLUGIN_ROOT}`를 이 플러그인 루트(이 SKILL.md에서 두 단계 위 폴더)로 바꿔 읽는다.

# 바선생 — 진입점

AI 활용 성장을 돕는 멘토 에이전트. 인자(또는 사용자가 요청에 쓴 말)에 따라 적절한 스킬로 분기한다.

## Parse Arguments

| 인자 | 동작 | 해당 스킬 |
|------|------|----------|
| `시작`, `onboard`, `설정`, `setup`, `init`, `초기화` | 초기 설정 (워크스페이스 생성, 프로젝트 매핑, 유형 분류, 첫 변환) | vibe-sunsang-onboard |
| `변환`, `retro`, `회고`, `대화변환` | 대화 로그 변환 + 분석 가이드 | vibe-sunsang-retro |
| `멘토링`, `mentor`, `코칭`, `coach` | AI 활용 능력 코칭 (4가지 모드) | vibe-sunsang-mentor |
| `성장`, `growth`, `리포트`, `레벨` | 성장 리포트 자동 생성 | vibe-sunsang-growth |
| `지식`, `knowledge`, `개념`, `용어` | 워크스페이스 유형별 개념/용어 학습 | vibe-sunsang-knowledge |
| (인자 없음) | 안내 메시지 출력 후 선택 | 아래 참조 |

## 인자 없이 실행한 경우

**EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다:

```json
{
  "questions": [{
    "question": "바선생이에요. 뭘 도와드릴까요?",
    "header": "바선생",
    "options": [
      {"label": "시작", "description": "초기 설정 (프로젝트 매핑, 워크스페이스 유형 분류, 첫 변환) — 처음 한 번만 하면 돼요"},
      {"label": "멘토링", "description": "AI 활용 능력 코칭 — 요청 품질, 안티패턴, 개념 학습, 종합 코칭 4가지 모드"},
      {"label": "성장", "description": "AI 활용 세션 데이터를 분석해서 성장 리포트를 자동 생성해요"},
      {"label": "기타 (변환·지식)", "description": "대화 로그 변환 또는 개념/용어 학습 — 다음 단계에서 하나를 골라요"}
    ],
    "multiSelect": false
  }]
}
```

`기타 (변환·지식)`을 선택한 경우에만 **EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 한 번 더 호출한다:

```json
{
  "questions": [{
    "question": "둘 중에 뭘 도와드릴까요?",
    "header": "바선생",
    "options": [
      {"label": "변환", "description": "이번 주 대화 로그를 Markdown으로 변환하고 분석 가이드를 제공해요"},
      {"label": "지식", "description": "바선생의 레벨 시스템, 안티패턴, 워크스페이스 유형 등 개념을 학습해요"}
    ],
    "multiSelect": false
  }]
}
```

## Execute

인자를 파악한 뒤, 해당 스킬의 SKILL.md(`${CLAUDE_PLUGIN_ROOT}/skills/<스킬 이름>/SKILL.md`)를 읽고 그 실행 순서를 그대로 따른다.
