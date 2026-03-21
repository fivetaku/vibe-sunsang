---
name: vibe-sunsang-retro
description: 바선생 대화 변환 — Claude Code 대화 로그를 Markdown으로 변환하고 분석 가이드를 제공합니다. "변환", "retro", "대화 변환", "로그 변환", "회고", "이번 주 대화" 같은 요청에 사용됩니다.
---

## 실행: 대화 로그 변환

인자: $ARGUMENTS

### Step 0: 사전 확인

`"$HOME/vibe-sunsang/config/project_names.json"` 파일이 있는지 확인합니다.

없으면:
> "아직 바선생 초기 설정이 되지 않았어요. `/vibe-sunsang 시작`을 먼저 실행해주세요."
> → 여기서 종료

### Step 1: 변환 스크립트 실행

인자를 분석하여 적절한 옵션으로 실행합니다:

| 인자 | 동작 |
|------|------|
| (없음) | 증분 변환 (새 세션만) |
| "전체", "force", "다시" | `--force` 전체 재변환 |
| "상세", "verbose" | `--verbose` 에러 로그 포함 |
| 프로젝트명 | `--project <이름>` 해당 프로젝트만 |

**프로젝트명이 지정된 경우:** `"$HOME/vibe-sunsang/conversations/INDEX.md"`에서 프로젝트 목록을 읽어 일치하는 프로젝트를 찾습니다. 정확히 일치하는 프로젝트가 없으면 **EXECUTE:** 아래 JSON으로 AskUserQuestion 도구를 즉시 호출한다:

```json
{
  "questions": [{
    "question": "어떤 프로젝트의 대화를 변환할까요?",
    "header": "프로젝트 선택",
    "options": [
      {"label": "{프로젝트명1}", "description": "{세션 수}개 세션"},
      {"label": "{프로젝트명2}", "description": "{세션 수}개 세션"}
    ],
    "multiSelect": false
  }]
}
```

> options는 INDEX.md에서 읽은 프로젝트 목록으로 동적 생성한다. 세션 수가 많은 순으로 정렬한다.

```bash
# 기본: 증분 변환
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations" 2>/dev/null || python ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations"

# --force: 인자에 "전체", "force", "다시" 포함 시
# python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --force --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations" 2>/dev/null || python ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --force --names-file "$HOME/vibe-sunsang/config/project_names.json" --output-dir "$HOME/vibe-sunsang/conversations"

# --verbose: 인자에 "상세", "verbose" 포함 시 추가
# --project: 인자에 프로젝트명 포함 시 추가
```

### 에러 처리

변환 스크립트 실행 중 문제가 발생하면 비개발자가 이해할 수 있게 안내합니다:

| 상황 | 사용자에게 보여줄 메시지 |
|------|------------------------|
| Python 없음 | "Python이 설치되어 있지 않아요. 터미널에서 `python3 --version`을 실행해서 확인해주세요." |
| 프로젝트 폴더 없음 | "Claude Code 대화 기록을 찾을 수 없어요. 다른 프로젝트에서 Claude Code를 사용한 적이 있는지 확인해주세요." |
| 권한 오류 | "파일에 접근할 수 없어요. `"$HOME/.claude/projects/"` 폴더의 권한을 확인해주세요." |
| 변환 0건 | "새로 변환할 대화가 없어요. 이미 최신 상태입니다!" |

### Step 2: 인덱스 확인

변환 완료 후 인덱스를 읽어 현황을 보여줍니다:

`"$HOME/vibe-sunsang/conversations/INDEX.md"`를 Read 도구로 읽습니다.

변환 결과를 요약합니다:
- 총 프로젝트 수
- 총 세션 수
- 최근 변환된 세션

### Step 3: 분석 템플릿 제안

변환이 완료되면 다음 분석 옵션을 제안합니다:

**사용 가능한 분석:**

1. **프로젝트 패턴 분석**
   > "[프로젝트명] 세션들을 분석해줘. 주요 작업 유형, 반복 에러, 도구 활용 패턴을 정리해줘."

2. **성장 트래커** → "성장 리포트 만들어줘" 또는 `/vibe-sunsang 성장`
   > 성장 리포트를 생성합니다. (v2: 6축 기술 차원 분석 + 레이더 차트 포함)

3. **멘토링 세션** → "멘토링해줘" 또는 `/vibe-sunsang 멘토링`
   > AI 활용 능력을 코칭 받습니다. (v2: 6축 중심 맞춤 분석)

4. **버그/실수 패턴**
   > "모든 프로젝트에서 내가 겪은 실수 패턴을 찾아줘."

5. **팀 모드 리뷰**
   > "팀 모드 세션을 분석해서 코디네이션 효율을 평가해줘."

6. **비용 분석**
   > "프로젝트별 토큰 사용량과 모델 분포를 정리해줘."

7. **6축 분석**
   > "최근 세션을 6축(DECOMP/VERIFY/ORCH/FAIL/CTX/META) 기준으로 분석해줘."

### 데이터 경로

- **원본**: `"$HOME/.claude/projects/{프로젝트}/세션ID.jsonl"`
- **변환 결과**: `"$HOME/vibe-sunsang/conversations/{프로젝트명}/"`
- **인덱스**: `"$HOME/vibe-sunsang/conversations/INDEX.md"`
- **설정**: `"$HOME/vibe-sunsang/config/"`
- **리포트 저장**: `"$HOME/vibe-sunsang/exports/"`
