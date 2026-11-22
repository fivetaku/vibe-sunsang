---
# 6축 가중치·게이트 정본 (v2.4). scripts/fit_score.py 가 이 frontmatter를 읽어 계산한다.
# 다른 문서(에이전트·스킬·growth-metrics)는 이 표를 복사하지 않고 이 파일을 가리킨다.
weights:
  builder:  {DECOMP: 0.25, VERIFY: 0.25, ORCH: 0.15, FAIL: 0.15, CTX: 0.10, META: 0.10}
  explorer: {DECOMP: 0.15, VERIFY: 0.15, ORCH: 0.10, FAIL: 0.20, CTX: 0.20, META: 0.20}
  designer: {DECOMP: 0.20, VERIFY: 0.15, ORCH: 0.10, FAIL: 0.10, CTX: 0.25, META: 0.20}
  operator: {DECOMP: 0.15, VERIFY: 0.20, ORCH: 0.25, FAIL: 0.20, CTX: 0.10, META: 0.10}
# 게이트: 레벨 N 이상이 되려면 해당 줄의 조건이 모두 참이어야 한다(줄 안의 "|"는 OR).
# 지표 이름은 convert_sessions.py frontmatter(기간 합계) 또는 분석가가 넘기는 비율 값이다.
gates:
  L3: ["context_specificity_ratio > 0.5"]
  L4: ["verification_ratio > 0.15 | verify_cmd_count >= 1", "correction_ratio > 0.05 | done_criteria_count >= 1"]
  L5: ["delegation_total >= 1 | orch_tool_count >= 1", "strategic_ratio > 0.05 | done_criteria_count >= 3"]
  L6: ["delegation_total >= 10 | orch_tool_count > 10"]
  L7: ["external_contribution >= 1"]
floor:
  first_session: 1.5
  three_sessions: 2.0
---

# 6축 가중치·게이트 정본

워크스페이스 유형별 가중치와 레벨 게이트의 **유일한 정본**이다. 계산은 손으로 하지 않고 `scripts/fit_score.py`가 이 파일의 frontmatter를 읽어 결정적으로 한다.

| 기술 차원 | Builder | Explorer | Designer | Operator |
|----------|---------|----------|----------|----------|
| DECOMP | **25%** | 15% | 20% | 15% |
| VERIFY | **25%** | 15% | 15% | 20% |
| ORCH | 15% | 10% | 10% | **25%** |
| FAIL | 15% | **20%** | 10% | **20%** |
| CTX | 10% | **20%** | **25%** | 10% |
| META | 10% | **20%** | **20%** | 10% |

## 계산 규칙 (fit_score.py)

1. `raw = Σ 가중치 × 축 점수` (축 점수는 1.0~7.0, 소수점 2자리)
2. 0.5 단위 반올림: x.00~x.24 → x.0 / x.25~x.74 → x.5 / x.75~x.99 → (x+1).0
3. 바닥 보정: 세션 1개 이상이면 최소 L1.5, 3개 이상이면 최소 L2.0
4. 게이트: 레벨 N 게이트를 통과하지 못하면 최대 L(N-0.5)로 제한한다. 게이트는 누적이다(L5가 되려면 L3·L4·L5 게이트 모두).

## 게이트가 보는 신호

| 게이트 | 조건 | 뜻 |
|--------|------|----|
| L3 | 맥락 구체성 > 0.5 | 무엇을 어디에 할지 말한다 |
| L4 | (검증 요청 > 0.15 또는 실제 검증 명령 실행 1회+) 그리고 (수정 요청 > 0.05 또는 완료 기준 1회+) | 결과를 확인하고, 끝의 기준을 말한다 |
| L5 | 위임 1회+(서브에이전트·스킬·워크플로·/goal·플랜 모드·워크트리) 그리고 (전략 논의 > 0.05 또는 완료 기준 3회+) | 목표와 완료 기준을 주고 맡긴다 |
| L6 | 위임 합계 10회+ | 위임이 습관이다 |
| L7 | L6 + 외부 기여 증거 | 남이 쓰는 방법론·도구를 만들었다 |

> 바뀐 점(v2.4): 권한 확인 생략 비율(bypass)과 도구 다양성(tool_diversity)은 에이전트가 고른 결과라 더는 게이트·신호로 쓰지 않는다. teamName 게이트는 위임 합계로 바꿨다.
