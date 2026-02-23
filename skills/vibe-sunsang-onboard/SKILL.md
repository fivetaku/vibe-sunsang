---
name: vibe-sunsang-onboard
description: 바선생 초기 설정 — 프로젝트 연결, 워크스페이스 유형 분류, 첫 변환까지 안내합니다. "바선생 시작", "온보딩", "초기 설정", "처음이에요", "셋업", "setup" 같은 요청에 사용됩니다.
---

## 바선생 온보딩

### Step 0: 사용자 데이터 디렉토리 준비

`~/vibe-sunsang/` 디렉토리가 있는지 확인합니다.

**이미 존재하는 경우 (재온보딩):**
> "이전에 설정한 바선생 데이터가 있습니다. 기존 설정을 유지하면서 새 프로젝트만 추가할까요, 아니면 처음부터 다시 설정할까요?"

AskUserQuestion:
- "새 프로젝트만 추가" → 기존 config 파일을 읽어 매핑된 프로젝트를 건너뛰고 새 프로젝트만 진행
- "처음부터 다시" → 기존 config 파일을 백업(`*.bak`) 후 새로 생성

**존재하지 않는 경우:**

```bash
mkdir -p ~/vibe-sunsang/config ~/vibe-sunsang/conversations ~/vibe-sunsang/exports
```

### Step 1: 환영 & 설명

다음 메시지를 사용자에게 보여줍니다:

---

**바선생에 오신 것을 환영합니다!**

바선생은 Claude Code와 나눈 대화를 돌아보고, **AI와 더 잘 협업하는 법**을 배우게 해주는 AI 멘토 에이전트입니다.

매주 한 번 여기서 이번 주 대화를 리뷰하면:
- 내가 어떤 실수를 반복하고 있는지
- AI에게 어떻게 요청하면 더 효과적인지
- 어떤 개념을 모르고 넘어갔는지

를 발견할 수 있습니다.

지금부터 초기 설정을 진행하겠습니다.

---

### Step 2: Claude Code 세션 확인

`~/.claude/projects/` 디렉토리를 확인하여 사용 가능한 프로젝트 목록을 가져옵니다.

```bash
ls ~/.claude/projects/
```

프로젝트가 없으면:
> "아직 Claude Code 대화 기록이 없습니다. 먼저 다른 프로젝트에서 Claude Code를 사용한 후 다시 와주세요."
> → 여기서 종료

프로젝트가 있으면 다음 단계로 진행합니다.

### Step 3: 프로젝트 이름 매핑

발견된 프로젝트 디렉토리 목록을 보여주고, 사용자에게 읽기 좋은 이름을 지정하도록 안내합니다.

**안내 메시지:**

> Claude Code가 저장한 프로젝트들을 발견했습니다.
> 각 프로젝트에 알아보기 쉬운 이름을 붙여주세요.
>
> 디렉토리 이름이 복잡해 보여도 걱정하지 마세요 - 실제 프로젝트 폴더 경로입니다.

각 프로젝트 디렉토리에 대해:
1. 디렉토리명에서 프로젝트명을 추측합니다 (경로의 마지막 의미 있는 부분 추출)
2. 사용자에게 AskUserQuestion으로 확인받습니다:
   - "이 프로젝트(`-Users-xxx-my-project`)의 이름을 뭐라고 할까요?"
   - 옵션: 자동 추측 이름 + "다른 이름" + "건너뛰기 (분석 안 함)"

**규칙:**
- 한 번에 5개까지만 질문합니다 (너무 많으면 피로)
- 세션이 5개 미만인 프로젝트는 자동으로 건너뜁니다 (사용자에게 알림)
- "건너뛰기"를 선택한 프로젝트는 매핑에서 제외
- **재온보딩 시**: 이미 매핑된 프로젝트는 건너뛰고 새 프로젝트만 질문

결과를 `~/vibe-sunsang/config/project_names.json`에 저장합니다.

### Step 4: 워크스페이스 유형 분류

**각 프로젝트의 CLAUDE.md 또는 README.md를 읽어서 유형을 추론합니다.**

분류 흐름:
1. 프로젝트 경로에서 `CLAUDE.md` 또는 `README.md`를 찾아 읽기
2. 내용을 기반으로 유형을 추론
3. 사용자에게 추론 결과를 보여주고 확인받기

**유형 분류 기준:**

| 유형 | 키워드/패턴 | 설명 |
|------|------------|------|
| **Builder** (구현자) | build, test, deploy, component, API, 코딩, 개발, 앱 | 코딩/개발 프로젝트 |
| **Explorer** (탐험자) | research, study, analyze, 리서치, 학습, 스터디, Q&A, 질문 | 리서치/Q&A/학습 |
| **Designer** (기획자) | plan, design, ideation, 기획, 아이디어, 콘텐츠, 글쓰기 | 기획/아이디에이션 |
| **Operator** (운영자) | automate, workflow, schedule, 자동화, 연동, 스크립트, MCP | 업무 자동화 |

**CLAUDE.md/README를 찾을 수 없는 경우:**
- 해당 프로젝트의 파일 구조를 간단히 확인 (`.py`, `.js` 파일이 많으면 Builder 등)
- 추론이 어려우면 사용자에게 직접 질문

**사용자 확인 (AskUserQuestion):**

각 프로젝트에 대해:
> "[프로젝트명]의 CLAUDE.md를 분석해보니 **[유형]** 워크스페이스로 보입니다. 맞나요?"
> 옵션: "Builder (코딩)", "Explorer (리서치/학습)", "Designer (기획)", "Operator (자동화)"

**규칙:**
- 프로젝트가 여러 목적이면 주된 목적 1개를 선택
- 같은 유형이 여러 프로젝트에 반복되면 묶어서 한 번에 확인

결과를 `~/vibe-sunsang/config/workspace_types.json`에 저장:

```json
{
  "schema_version": 1,
  "type_definitions": {
    "builder": "코딩/개발",
    "explorer": "리서치/Q&A/스터디",
    "designer": "기획/아이디에이션",
    "operator": "자동화/데이터처리"
  },
  "default_type": "builder",
  "workspaces": {
    "-Users-xxx-my-app": {
      "type": "builder",
      "name": "my-app",
      "detected_from": "CLAUDE.md",
      "confirmed": true
    }
  }
}
```

### Step 5: 첫 변환 실행

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py --force --names-file ~/vibe-sunsang/config/project_names.json --output-dir ~/vibe-sunsang/conversations
```

변환 진행 상황을 보여주고, 완료되면 결과를 요약합니다:
- 총 프로젝트 수
- 총 세션 수
- 가장 활발한 프로젝트 TOP 3
- **유형별 분포** (Builder N개, Explorer N개, ...)

### Step 6: 사용법 안내

---

**설정 완료!**

프로젝트 유형별로 맞춤 분석을 받을 수 있습니다:

| 유형 | 분석 내용 |
|------|----------|
| Builder (구현자) | 코딩 요청 품질, 에러 대응, 코드 이해도 |
| Explorer (탐험자) | 질문 깊이, 출처 검증, 비판적 사고 |
| Designer (기획자) | 기획 구체성, 구조화, 실현 가능성 |
| Operator (운영자) | 자동화 품질, 에러 처리, 재사용성 |

사용할 수 있는 기능:

| 명령 | 설명 |
|------|------|
| `/vibe-sunsang 변환` | 새 대화 변환 (매주 실행 권장) |
| `/vibe-sunsang 멘토링` | AI 활용 능력 코칭 (유형별 맞춤) |
| `/vibe-sunsang 성장` | 성장 분석 리포트 (유형별 맞춤) |

**추천 루틴:**
1. 매주 금요일, `/vibe-sunsang 변환` 으로 이번 주 대화 변환
2. "멘토링해줘" 로 이번 주 리뷰
3. 행동 계획 실천

---

### Step 7: 바로 시작할지 물어보기

AskUserQuestion으로 물어봅니다:
- "바로 이번 주 리뷰를 시작해볼까요?"
- 옵션: "멘토링 시작", "성장 리포트 생성", "나중에 할게요"

선택에 따라:
- "멘토링 시작" → vibe-sunsang-mentor 스킬 실행
- "성장 리포트 생성" → vibe-sunsang-growth 스킬 실행
- "나중에 할게요" → 종료
