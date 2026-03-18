---
name: vibe-sunsang-knowledge
description: 바선생 지식 베이스 — 바선생의 레벨 시스템, 안티패턴, 워크스페이스 유형 등 바선생 고유 개념에 대한 질문에 응답합니다. "바선생 안티패턴이 뭐야?", "바선생 레벨 시스템 설명해줘", "바선생 성장 지표" 같은 요청에 사용됩니다.
---

# 바선생 지식 베이스

바선생의 핵심 개념, 용어, 프레임워크에 대한 질문에 답변합니다.

## 참조 경로

- **지식 베이스**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/`
- **유형 설정**: `"$HOME/vibe-sunsang/config/workspace_types.json"`

### 공통 (모든 워크스페이스 유형)
- **요청 품질 가이드**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/prompt-quality.md`
- **멘토링 체크리스트**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/mentoring-checklist.md`
- **회고 프레임워크**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/retrospective-frameworks.md`

### 유형별 (Builder / Explorer / Designer / Operator)
- **안티패턴**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/antipatterns.md`
- **핵심 개념**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/concepts.md`
- **성장 지표 & 레벨**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/growth-metrics.md`

## 실행 흐름

### Step 0: 워크스페이스 유형 확인

유형별 질문인 경우 사용자의 워크스페이스 유형을 먼저 확인합니다:

1. `"$HOME/vibe-sunsang/config/workspace_types.json"`을 읽어 확인
2. 파일이 없거나 유형 정보가 없으면 **EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다:

```json
{
  "questions": [{
    "question": "어떤 유형의 워크스페이스에 대해 알고 싶으신가요?",
    "header": "유형 선택",
    "options": [
      {"label": "Builder (코딩)", "description": "코딩/개발 프로젝트"},
      {"label": "Explorer (리서치/학습)", "description": "리서치/Q&A/스터디"},
      {"label": "Designer (기획)", "description": "기획/아이디에이션"},
      {"label": "Operator (자동화)", "description": "업무 자동화/데이터처리"}
    ],
    "multiSelect": false
  }]
}
```

공통 주제 질문(요청 품질, 멘토링, 회고)은 유형 확인 없이 바로 진행합니다.

### Step 1: 개념 선택

사용자의 질문에서 관련 주제를 파악합니다. 질문이 모호하면 **EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다:

```json
{
  "questions": [{
    "question": "어떤 개념에 대해 알고 싶으신가요?",
    "header": "개념 선택",
    "options": [
      {"label": "안티패턴", "description": "AI 활용 시 피해야 할 나쁜 습관들"},
      {"label": "레벨 시스템", "description": "5단계 성장 레벨과 각 단계의 특징"},
      {"label": "워크스페이스 유형", "description": "Builder/Explorer/Designer/Operator 유형 설명"},
      {"label": "요청 품질", "description": "AI에게 좋은 요청을 하는 방법"},
      {"label": "성장 지표", "description": "유형별 성장을 측정하는 기준"},
      {"label": "멘토링 방법", "description": "효과적인 AI 활용 멘토링/코칭 방법"}
    ],
    "multiSelect": false
  }]
}
```

### Step 2: 지식 베이스 로딩

주제별 참조 매핑에 따라 해당 reference 파일을 읽습니다:

| 질문 유형 | 참조 파일 |
|-----------|----------|
| 안티패턴, 나쁜 습관 | `{type}/antipatterns.md` |
| 레벨 시스템, 성장 단계 | `{type}/growth-metrics.md` |
| 개념, 용어 설명 | `{type}/concepts.md` |
| 요청 잘 하는 법, 프롬프트 | `common/prompt-quality.md` |
| 멘토링, 코칭 방법 | `common/mentoring-checklist.md` |
| 회고, 리뷰 방법 | `common/retrospective-frameworks.md` |

모든 경로의 base: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/`

### Step 3: 설명

읽은 reference 파일을 기반으로 사용자에게 설명합니다:

1. 핵심 개념을 **한 문장**으로 요약
2. 비유나 일상 예시로 쉽게 풀어 설명
3. 관련된 다른 개념이 있으면 연결 (예: "안티패턴을 이해했으니, 레벨 시스템도 궁금하시면 알려드릴게요")

## 대화 스타일

- 전문 용어에는 항상 **쉬운 설명**을 함께 제공
- 비유와 일상 예시를 적극 활용
- 한국어로 응답 (기술 용어는 영어 병기 가능)
- 한 번에 너무 많은 정보를 주지 않고, 핵심만 전달한 뒤 추가 질문을 유도
