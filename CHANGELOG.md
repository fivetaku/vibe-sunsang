# Changelog

## [1.4.0] - 2026-03-18

### Added
- `/vibe-sunsang 지식` 커맨드: 바선생 고유 개념(레벨 시스템, 안티패턴, 워크스페이스 유형) 학습 기능
  - knowledge SKILL.md Step 0~3 실행 흐름으로 재구성
  - commands/vibe-sunsang.md에 `지식/knowledge/개념/용어` 인자 + AskUserQuestion 옵션 추가
- 성장 리포트 종단 추적: Step 6 종단비교 + TIMELINE.md 자동 업데이트
- 온보딩 Init 통합: Step 0.5에서 CLAUDE.md, .gitignore, git init 자동 생성
- 마이그레이션 자동 감지: v1.3.x 이전 워크스페이스 구조 감지 시 안내
- 대화 변환 프로젝트 선택 UI: retro SKILL.md에 AskUserQuestion 기반 프로젝트 선택 추가
- CLAUDE-MD-TEMPLATE.md: 워크스페이스용 CLAUDE.md 템플릿 (references/에 저장)
- 각 스킬에 Gotchas 섹션 추가 (growth, onboard, growth-analyst)

### Changed
- knowledge SKILL.md description 트리거 범위 축소 (바선생 고유 개념으로 한정)
- onboard Step 3 프로젝트 매핑: 5개 초과 시 "5개씩 나눠서 반복" 처리 명확화
- growth-analyst 에이전트: 종단비교 섹션 + TIMELINE.md 자동 업데이트 추가
- README.md: Init, 종단추적, growth-log 구조, SSOT 안내 반영

## [1.2.0] - 2026-02-25

### Changed
- CCPS v2.0 호환: 에이전트 예시, gitignore 추가

## [1.1.0] - 2026-02-24

### Added
- 워크스페이스 유형별 멘토링 시스템 (Builder/Explorer/Designer/Operator)

### Changed
- 워크스페이스 → 에이전트 리브랜딩
- 워크스페이스 → 플러그인 전환

## [1.0.0] - 2026-02-20

### Added
- 최초 릴리스 (바선생 v1.0.0)
- 바이브 코딩 멘토링 스킬
- 바선생 마스코트 이미지
- Windows WSL2 요구사항 안내
