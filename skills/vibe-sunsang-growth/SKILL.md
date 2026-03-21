---
name: vibe-sunsang-growth
description: 바선생 성장 리포트 — AI 활용 세션 데이터를 분석하여 성장 리포트를 자동 생성합니다. v2 레벨 시스템(6축×7단계, 0.5 단위)으로 분석합니다. "성장 리포트", "성장 분석", "얼마나 성장했는지", "레벨 체크", "성장 트래킹", "growth" 같은 요청에 사용됩니다.
---

# Growth - 성장 리포트 생성 스킬

> AI 활용 세션 데이터를 분석하여 성장 리포트를 자동 생성 (Subagent 위임, 유형별 맞춤, v2 6축 분석)

## 참조 경로

- **대화 로그**: `"$HOME/vibe-sunsang/conversations/"`
- **지식 베이스**: `${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/`
- **유형 설정**: `"$HOME/vibe-sunsang/config/workspace_types.json"`
- **결과 저장**: `"$HOME/vibe-sunsang/exports/"`

## 실행 방식: Subagent 위임

이 스킬은 대량의 세션 파일을 분석해야 하므로, **메인 컨텍스트를 보호**하기 위해
`vibe-sunsang:growth-analyst` 서브에이전트에게 작업을 위임합니다.

### Step 0: 사전 확인

`"$HOME/vibe-sunsang/config/workspace_types.json"` 파일이 있는지 확인합니다.

없으면:
> "아직 바선생 초기 설정이 되지 않았어요. `/vibe-sunsang 시작`을 먼저 실행해주세요."
> → 여기서 종료

### Step 1: 범위 선택

사용자의 요청에 범위가 명시되어 있으면 그대로 사용합니다.
**범위가 없으면 EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다:

```json
{
  "questions": [{
    "question": "성장 리포트를 어떤 범위로 생성할까요?",
    "header": "범위 선택",
    "options": [
      {"label": "이번 주", "description": "빠른 주간 리뷰 (최근 1주)", "markdown": "## 이번 주 리뷰\n\n**범위**: 최근 7일\n**분석 내용**:\n- 이번 주 세션 요약\n- 6축 기술 차원 분석\n- 빠른 피드백\n\n**소요 시간**: ~1분"},
      {"label": "최근 2주 (추천)", "description": "일반적인 리뷰 주기 (최근 2주)", "markdown": "## 최근 2주 리뷰 (추천)\n\n**범위**: 최근 14일\n**분석 내용**:\n- 세션 트렌드 분석\n- 6축 기술 차원 분석 + 레이더 차트\n- 안티패턴 진단\n- v2 레벨 판정 (Fit Score + 게이트 조건)\n- 행동 계획 제안\n\n**소요 시간**: ~2분"},
      {"label": "이번 달", "description": "월간 성장 확인 (최근 1달)", "markdown": "## 이번 달 리뷰\n\n**범위**: 최근 30일\n**분석 내용**:\n- 월간 성장 추이\n- 6축 차원별 심층 분석\n- 레벨 변화 추적\n- 정체기/돌파구 분석\n- 상세 행동 계획\n\n**소요 시간**: ~3분"},
      {"label": "특정 프로젝트", "description": "프로젝트별 심층 분석", "markdown": "## 프로젝트별 분석\n\n**범위**: 선택한 프로젝트의 전체 기간\n**분석 내용**:\n- 프로젝트 전용 심층 분석\n- 해당 워크스페이스 유형 맞춤 6축 평가\n- 프로젝트별 성장 곡선\n\n**소요 시간**: ~2분"}
    ],
    "multiSelect": false
  }]
}
```

"특정 프로젝트" 선택 시 → `"$HOME/vibe-sunsang/conversations/INDEX.md"`에서 프로젝트 목록을 보여주고 선택하게 합니다.

### Step 2: 워크스페이스 유형 확인

`"$HOME/vibe-sunsang/config/workspace_types.json"`을 읽어 분석 대상 프로젝트의 유형을 확인합니다.

- 특정 프로젝트 분석 → 해당 프로젝트의 유형 사용
- 기간 기반 분석 → 포함된 프로젝트들의 유형 목록 수집
- 유형이 등록되지 않은 프로젝트 → `default_type` (builder) 사용

### Step 3: 변환 확인

서브에이전트에 위임하기 전, 최신 데이터가 있는지 확인합니다:

1. `"$HOME/vibe-sunsang/conversations/INDEX.md"`를 확인
2. 필요하면 변환 스크립트를 먼저 실행:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations" 2>/dev/null || python ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations"
   ```

### Step 4: Subagent 위임

사용자에게 진행 상황을 알린 후, `vibe-sunsang:growth-analyst` 에이전트를 spawn합니다:

**진행 메시지 (spawn 전 반드시 출력):**
> "성장 리포트를 생성하고 있습니다. v2 레벨 시스템(6축 기술 차원 분석)으로 세션 데이터를 분석하는 중이니 잠시만 기다려주세요..."

```
Task(
  subagent_type="vibe-sunsang:growth-analyst",
  prompt="성장 리포트를 생성해주세요.
         범위: [파악한 범위].
         워크스페이스 유형: [workspace_types.json에서 파악한 유형 정보].
         유형별 지식 베이스 경로: ${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/{type}/.
         공통 지식 베이스: ${CLAUDE_PLUGIN_ROOT}/skills/vibe-sunsang-knowledge/references/common/.
         대화 로그 경로: $HOME/vibe-sunsang/conversations/.

         [v2 레벨 시스템 지침]
         - 6대 기술 차원(DECOMP/VERIFY/ORCH/FAIL/CTX/META)별로 행동 신호를 감지하세요.
         - 유형별 동적 가중치를 적용하세요:
           Builder: DECOMP 25%, VERIFY 25%, ORCH 15%, FAIL 15%, CTX 10%, META 10%
           Explorer: DECOMP 15%, VERIFY 15%, ORCH 10%, FAIL 20%, CTX 20%, META 20%
           Designer: DECOMP 20%, VERIFY 15%, ORCH 10%, FAIL 10%, CTX 25%, META 20%
           Operator: DECOMP 15%, VERIFY 20%, ORCH 25%, FAIL 20%, CTX 10%, META 10%
         - Fit Score 공식: F_L = SUM(w_i * S_i)
         - 바닥 효과 보정: 첫 세션 ≥ L1.5, 3세션 + 도구 2종 ≥ L2.0
         - 게이트 조건 확인: L3(구체성>0.5), L4(검증>0.15), L5(도구>8+전략), L6(멀티에이전트), L7(외부기여)
         - 내부 소수점 2자리, 공식 0.5 단위 반올림
         - 6축 레이더 차트(텍스트), 레벨 카드, 게이트 상태 테이블 포함
         - 승급 시 승급 메시지 포함 (L4→L5는 '80%의 벽' 특별 이벤트)

         $HOME/vibe-sunsang/conversations/ 디렉토리에서 세션 파일을 읽고,
         해당 유형의 지식 베이스 기준에 따라 분석한 후,
         $HOME/vibe-sunsang/exports/growth-report-YYYY-MM-DD.md로 저장해주세요.",
  description="성장 리포트 생성 (v2 6축 분석)"
)
```

**중요**: 유형 정보, 경로, v2 지표 지침을 반드시 서브에이전트에 전달합니다.

### Step 5: 결과 전달

서브에이전트가 반환한 결과를 사용자에게 전달합니다:
- 저장된 리포트 파일 경로
- 현재 레벨과 6축 점수 요약
- 레이더 차트 (텍스트)
- 주요 성장 포인트
- 다음 단계 제안 (최대 3개, 가장 약한 축 중심)

메인 컨텍스트에는 **요약만** 남기고, 상세 분석은 리포트 파일을 참조하도록 안내합니다.

### Step 6: 종단 추적 확인

서브에이전트가 리포트를 저장한 후:

1. `$HOME/vibe-sunsang/growth-log/TIMELINE.md`가 업데이트되었는지 확인
2. 업데이트되지 않았으면 수동으로 업데이트 (6축 점수 열 포함):

```markdown
| 날짜 | 레벨 | DECOMP | VERIFY | ORCH | FAIL | CTX | META | 요청품질 | 주요 안티패턴 | 변화 포인트 |
```

3. 사용자에게 종단 요약 제공:
   - "N주 전 대비 레벨 LX.X → LY.Y"
   - "가장 크게 성장한 축: [축명] (X.X → Y.Y)"
   - "해소된 안티패턴: [목록]"
   - "다음 레벨까지: [게이트 조건 또는 약한 축]"

### Gotchas

- 서브에이전트가 TIMELINE.md 업데이트에 실패할 수 있다. Step 6에서 반드시 확인하고 보완한다.
- 첫 리포트일 경우 종단 요약 대신 "첫 리포트가 생성되었습니다. 다음 리포트부터 6축 성장 추이를 비교할 수 있어요."라고 안내한다.
- v1.x 이전 리포트와의 종단 비교 시 6축 데이터가 없을 수 있다. 이 경우 레벨과 요청 품질만 비교한다.

### 에러 처리

문제 발생 시 비개발자가 이해할 수 있게 안내합니다:

| 상황 | 사용자에게 보여줄 메시지 |
|------|------------------------|
| 세션 파일이 없음 | "아직 변환된 대화가 없어요. `/vibe-sunsang 변환`을 먼저 실행해주세요." |
| 변환 스크립트 실패 | "대화 파일 변환에 문제가 생겼어요. 프로젝트 폴더(`"$HOME/.claude/projects/"`)가 있는지 확인해주세요." |
| 서브에이전트 실패 | "분석 중 문제가 발생했어요. 다시 한번 시도해볼까요?" |
| INDEX.md 없음 | "인덱스 파일이 없어요. `/vibe-sunsang 변환`으로 먼저 대화를 변환해주세요." |
| 유형 정보 없음 | "워크스페이스 유형이 설정되지 않았어요. `/vibe-sunsang 시작`을 먼저 실행해주세요." |
