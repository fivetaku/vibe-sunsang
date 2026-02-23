---
name: vibe-sunsang
description: "바선생 — AI 활용 성장 멘토 에이전트"
argument-hint: "[시작|변환|멘토링|성장]"
allowed-tools:
  - Bash
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

# /vibe-sunsang Command

AI 활용 성장을 돕는 멘토 에이전트. 인자에 따라 적절한 스킬로 분기한다.

## Parse Arguments

| 인자 | 동작 | 해당 스킬 |
|------|------|----------|
| `시작`, `onboard`, `설정`, `setup` | 초기 설정 (프로젝트 매핑, 유형 분류, 첫 변환) | vibe-sunsang-onboard |
| `변환`, `retro`, `회고`, `대화변환` | 대화 로그 변환 + 분석 가이드 | vibe-sunsang-retro |
| `멘토링`, `mentor`, `코칭`, `coach` | AI 활용 능력 코칭 (4가지 모드) | vibe-sunsang-mentor |
| `성장`, `growth`, `리포트`, `레벨` | 성장 리포트 자동 생성 | vibe-sunsang-growth |
| (인자 없음) | 안내 메시지 출력 후 선택 | 아래 참조 |

## 인자 없이 실행한 경우

AskUserQuestion으로 선택지를 제시한다:

```
바선생이에요. 뭘 도와드릴까요?

1. "시작" — 초기 설정 (처음 한 번)
2. "변환" — 이번 주 대화를 변환
3. "멘토링" — AI 활용 능력 코칭
4. "성장" — 성장 리포트 생성
```

## Execute

인자를 파악한 뒤, 해당 스킬의 실행 순서를 그대로 따른다.
스킬 내용은 `${CLAUDE_PLUGIN_ROOT}/skills/` 하위의 각 SKILL.md를 참조한다.
