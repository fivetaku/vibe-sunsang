---
name: vibe-sunsang-growth
description: 바선생 성장 리포트 — AI 활용 세션 데이터를 분석하여 성장 리포트를 자동 생성합니다. "성장 리포트", "성장 분석", "얼마나 성장했는지", "레벨 체크", "성장 트래킹", "growth" 같은 요청에 사용됩니다.
---

# Growth - 성장 리포트 생성 스킬

> AI 활용 세션 데이터를 분석하여 성장 리포트를 자동 생성 (Subagent 위임, 유형별 맞춤)

## 참조 경로

- **대화 로그**: `~/vibe-sunsang/conversations/`
- **지식 베이스**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/`
- **유형 설정**: `~/vibe-sunsang/config/workspace_types.json`
- **결과 저장**: `~/vibe-sunsang/exports/`

## 실행 방식: Subagent 위임

이 스킬은 대량의 세션 파일을 분석해야 하므로, **메인 컨텍스트를 보호**하기 위해
`vibe-sunsang:growth-analyst` 서브에이전트에게 작업을 위임합니다.

### Step 0: 사전 확인

`~/vibe-sunsang/config/workspace_types.json` 파일이 있는지 확인합니다.

없으면:
> "아직 바선생 초기 설정이 되지 않았어요. `/vibe-sunsang 시작`을 먼저 실행해주세요."
> → 여기서 종료

### Step 1: 범위 선택

사용자의 요청에 범위가 명시되어 있으면 그대로 사용합니다.
**범위가 없으면 반드시 AskUserQuestion으로 물어봅니다:**

> "성장 리포트를 어떤 범위로 생성할까요?"

| 선택지 | 범위 | 설명 |
|--------|------|------|
| "이번 주" | 최근 1주 | 빠른 주간 리뷰 |
| "최근 2주 (기본)" | 최근 2주 | 일반적인 리뷰 주기 |
| "이번 달" | 최근 1달 | 월간 성장 확인 |
| "특정 프로젝트" | 프로젝트 지정 | 프로젝트별 심층 분석 |

"특정 프로젝트" 선택 시 → `~/vibe-sunsang/conversations/INDEX.md`에서 프로젝트 목록을 보여주고 선택하게 합니다.

### Step 2: 워크스페이스 유형 확인

`~/vibe-sunsang/config/workspace_types.json`을 읽어 분석 대상 프로젝트의 유형을 확인합니다.

- 특정 프로젝트 분석 → 해당 프로젝트의 유형 사용
- 기간 기반 분석 → 포함된 프로젝트들의 유형 목록 수집
- 유형이 등록되지 않은 프로젝트 → `default_type` (builder) 사용

### Step 3: 변환 확인

서브에이전트에 위임하기 전, 최신 데이터가 있는지 확인합니다:

1. `~/vibe-sunsang/conversations/INDEX.md`를 확인
2. 필요하면 변환 스크립트를 먼저 실행:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --names-file ~/vibe-sunsang/config/project_names.json --output-dir ~/vibe-sunsang/conversations
   ```

### Step 4: Subagent 위임

사용자에게 진행 상황을 알린 후, `vibe-sunsang:growth-analyst` 에이전트를 spawn합니다:

**진행 메시지 (spawn 전 반드시 출력):**
> "성장 리포트를 생성하고 있습니다. 세션 데이터를 분석하는 중이니 잠시만 기다려주세요..."

```
Task(
  subagent_type="vibe-sunsang:growth-analyst",
  prompt="성장 리포트를 생성해주세요.
         범위: [파악한 범위].
         워크스페이스 유형: [workspace_types.json에서 파악한 유형 정보].
         유형별 지식 베이스 경로: ${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/.
         공통 지식 베이스: ${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/.
         대화 로그 경로: ~/vibe-sunsang/conversations/.
         ~/vibe-sunsang/conversations/ 디렉토리에서 세션 파일을 읽고,
         해당 유형의 지식 베이스 기준에 따라 분석한 후,
         ~/vibe-sunsang/exports/growth-report-YYYY-MM-DD.md로 저장해주세요.",
  description="성장 리포트 생성"
)
```

**중요**: 유형 정보와 경로를 반드시 서브에이전트에 전달합니다.

### Step 5: 결과 전달

서브에이전트가 반환한 결과를 사용자에게 전달합니다:
- 저장된 리포트 파일 경로
- 현재 레벨과 주요 성장 포인트
- 다음 단계 제안 (최대 3개)

메인 컨텍스트에는 **요약만** 남기고, 상세 분석은 리포트 파일을 참조하도록 안내합니다.

### 에러 처리

문제 발생 시 비개발자가 이해할 수 있게 안내합니다:

| 상황 | 사용자에게 보여줄 메시지 |
|------|------------------------|
| 세션 파일이 없음 | "아직 변환된 대화가 없어요. `/vibe-sunsang 변환`을 먼저 실행해주세요." |
| 변환 스크립트 실패 | "대화 파일 변환에 문제가 생겼어요. 프로젝트 폴더(`~/.claude/projects/`)가 있는지 확인해주세요." |
| 서브에이전트 실패 | "분석 중 문제가 발생했어요. 다시 한번 시도해볼까요?" |
| INDEX.md 없음 | "인덱스 파일이 없어요. `/vibe-sunsang 변환`으로 먼저 대화를 변환해주세요." |
| 유형 정보 없음 | "워크스페이스 유형이 설정되지 않았어요. `/vibe-sunsang 시작`을 먼저 실행해주세요." |
