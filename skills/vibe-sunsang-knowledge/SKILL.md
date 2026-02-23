---
name: vibe-sunsang-knowledge
description: 바선생 지식 베이스 — AI 활용 성장을 위한 용어, 레벨 시스템, 안티패턴, 멘토링 프레임워크 질문에 응답합니다. "안티패턴이 뭐야?", "레벨 시스템 설명해줘", "바이브코딩이 뭐야", "성장 지표", "멘토링 프레임워크", "회고 방법" 같은 요청에 사용됩니다.
---

# 바선생 지식 베이스

바선생의 핵심 개념, 용어, 프레임워크에 대한 질문에 답변합니다.

## 지식 베이스 구조

### 공통 (모든 워크스페이스 유형)
- **요청 품질 가이드**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/prompt-quality.md`
- **멘토링 체크리스트**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/mentoring-checklist.md`
- **회고 프레임워크**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/retrospective-frameworks.md`

### 유형별 (Builder / Explorer / Designer / Operator)
- **안티패턴**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/antipatterns.md`
- **핵심 개념**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/concepts.md`
- **성장 지표 & 레벨**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/growth-metrics.md`

## 응답 방식

1. 사용자 질문에서 관련 주제를 파악합니다
2. 해당 reference 파일을 읽어 정확한 정보를 제공합니다
3. 비개발자가 이해할 수 있도록 쉬운 말로 설명합니다

### 주제별 참조 매핑

| 질문 유형 | 참조 파일 |
|-----------|----------|
| 안티패턴, 나쁜 습관 | `{type}/antipatterns.md` |
| 레벨 시스템, 성장 단계 | `{type}/growth-metrics.md` |
| 개념, 용어 설명 | `{type}/concepts.md` |
| 요청 잘 하는 법, 프롬프트 | `common/prompt-quality.md` |
| 멘토링, 코칭 방법 | `common/mentoring-checklist.md` |
| 회고, 리뷰 방법 | `common/retrospective-frameworks.md` |

### 워크스페이스 유형 확인

유형별 질문인 경우 사용자의 워크스페이스 유형을 먼저 확인합니다:
1. `~/vibe-sunsang/config/workspace_types.json`을 읽어 확인
2. 파일이 없거나 유형 정보가 없으면 사용자에게 질문:
   > "어떤 유형의 워크스페이스에 대해 알고 싶으신가요?"
   > 옵션: "Builder (코딩)", "Explorer (리서치/학습)", "Designer (기획)", "Operator (자동화)"

## 대화 스타일

- 전문 용어에는 항상 **쉬운 설명**을 함께 제공
- 비유와 일상 예시를 적극 활용
- 한국어로 응답 (기술 용어는 영어 병기 가능)
