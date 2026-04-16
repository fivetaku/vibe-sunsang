[한국어](README.ko.md)

# vibe-sunsang (바선생)

<p align="center">
  <img src="assets/logo.jpeg" alt="vibe-sunsang" width="240">
</p>

> **An AI mentor agent that turns your Claude Code conversation history into a growth engine.**

vibe-sunsang automatically collects, converts, and analyzes every conversation you have with Claude Code — so you can become a more effective AI collaborator over time.

[Quick Start](#quick-start) • [Why vibe-sunsang?](#why-vibe-sunsang) • [How it works](#how-it-works) • [Modes](#modes) • [Level system](#level-system) • [Requirements](#requirements)

---

## Quick Start

### 1. Install

```
/plugin marketplace add https://github.com/fivetaku/gptaku_plugins.git
/plugin install vibe-sunsang
```

Then **restart Claude Code**.

### 2. Run onboarding

In any project:

```
/vibe-sunsang 시작
```

Onboarding will:

1. Create `~/vibe-sunsang/` workspace (with `CLAUDE.md`, `.gitignore`, and `git init`)
2. Scan your Claude Code conversation history at `~/.claude/projects/`
3. Let you assign readable names to each discovered project
4. Classify each project by workspace type (Builder / Explorer / Designer / Operator)
5. Convert all JSONL logs to Markdown for the first time
6. Ask whether to jump straight into mentoring or a growth report

### 3. Use it weekly

```
/vibe-sunsang 변환      ← convert this week's conversations
/vibe-sunsang 멘토링    ← get coaching on your AI usage patterns
/vibe-sunsang 성장      ← generate a growth report
/vibe-sunsang 지식      ← explore the level system and concepts
```

---

## Why vibe-sunsang?

- **Your conversations already hold the data** — Claude Code stores every session as JSONL. vibe-sunsang reads those files so nothing new needs to be logged
- **Not just "what did I build" — "how did I build it"** — analysis focuses on your request quality, error recovery habits, and strategic thinking, not just output volume
- **Workspace-type-aware** — the level system adapts to what you are actually doing (coding, researching, planning, or automating)
- **Six dimensions, not one score** — DECOMP, VERIFY, ORCH, FAIL, CTX, META are measured independently so you know exactly which skill to develop next
- **Longitudinal tracking** — each growth report updates `TIMELINE.md` so you can see progress across months, not just a single session
- **Non-developer friendly** — plain-language coaching with analogies, no jargon wall

---

## How it works

```
Claude Code conversation logs (~/.claude/projects/)
                    |
                    | /vibe-sunsang 변환
                    v
     Readable Markdown files (~/vibe-sunsang/conversations/)
                    |
                    | 6-axis analysis
                    | (DECOMP / VERIFY / ORCH / FAIL / CTX / META)
                    v
     Mentoring session  ←→  Growth report  ←→  Concept learning
                    |
                    | Fit Score  ×  workspace-type weights
                    v
     Level judgment: L1.0 – L7.0 (0.5-step increments)
                    |
                    v
     TIMELINE.md (longitudinal growth tracking)
```

Conversation data and plugin code live in separate directories, so plugin updates never touch your data.

---

## Modes

### Onboard (`시작`)

Sets up the `~/vibe-sunsang/` workspace, maps project names, classifies workspace types, and runs the first full conversion.

---

### Convert (`변환`)

Converts Claude Code JSONL logs to readable Markdown files organized by project.

| Command | Behavior |
|---------|----------|
| `/vibe-sunsang 변환` | Incremental — only new sessions |
| `/vibe-sunsang 변환 force` | Full re-convert |
| `/vibe-sunsang 변환 <project name>` | Single project only |

Each converted file includes metadata frontmatter: date, token counts, model used, and tools called. An `INDEX.md` gives you the full overview at a glance.

---

### Mentor (`멘토링`)

Four coaching modes, each focused on different skill dimensions:

| Mode | Trigger | What it does | Core axes |
|------|---------|--------------|-----------|
| **A — Request quality** | "요청 코칭해줘" | Grades your prompts A–D for clarity and context | DECOMP + CTX |
| **B — Antipattern diagnosis** | "뭘 잘못하고 있는지" | Detects bad habits with specific examples and fix strategies | FAIL + VERIFY |
| **C — Concept learning** | "이게 뭐야" | Explains concepts from your recent sessions in plain language | META |
| **D — Full coaching** (default) | "멘토링해줘" | Complete 6-axis checkup, level judgment, and action plan | all 6 axes |

Mode D outputs a text radar chart and a three-step action plan: one thing to do right now, one this week, one within a month.

Coaching results can be saved to `~/vibe-sunsang/exports/mentor-YYYY-MM-DD.md`.

---

### Growth report (`성장`)

Delegates analysis to a dedicated `growth-analyst` subagent to keep the main context lean. The agent reads your session files, scores all six dimensions, and writes a full report.

**Time range options:**

| Range | Coverage |
|-------|----------|
| This week | Last 7 days |
| Last 2 weeks (recommended) | Last 14 days |
| This month | Last 30 days |
| Specific project | Full project history |

**Report includes:**

1. Basic stats — session count, message count, token usage
2. 6-axis technical dimension analysis with scores and weights
3. Text radar chart
4. Gate condition status table (requirements to reach the next level)
5. Antipattern detection (calibrated to your workspace type)
6. Longitudinal comparison against all previous reports
7. Level card with progression bar
8. Level-up message if you advanced (L4→L5 gets a special "80% wall" event)
9. `TIMELINE.md` auto-update

---

### Knowledge (`지식`)

Answers questions about the vibe-sunsang framework itself:

| Topic | Description |
|-------|-------------|
| Level system | 7-level progression (0.5 increments) and what each level means |
| Six axes | Definitions and examples for DECOMP, VERIFY, ORCH, FAIL, CTX, META |
| Workspace types | What Builder / Explorer / Designer / Operator means for your analysis |
| Antipatterns | Bad habits to watch for, calibrated to your workspace type |
| Request quality | How to write better prompts |
| Growth metrics | Fit Score formula, gate conditions, type-specific weights |

---

## Level system

### 6 technical dimensions

| Code | Dimension | One-line definition |
|------|-----------|---------------------|
| **DECOMP** | Task decomposition | Breaking complex requests into units AI can handle |
| **VERIFY** | Verification strategy | Critically reviewing AI output rather than accepting it |
| **ORCH** | Orchestration | Combining tools, agents, and workflows |
| **FAIL** | Failure recovery | Diagnosing errors and finding alternatives |
| **CTX** | Context management | Supplying background, constraints, and goals to AI |
| **META** | Metacognition | Recognizing and strategically adjusting your AI usage patterns |

### Workspace types and weights

Analysis weights differ by what you are actually doing:

| Dimension | Builder | Explorer | Designer | Operator |
|-----------|---------|----------|----------|----------|
| DECOMP | **25%** | 15% | 20% | 15% |
| VERIFY | **25%** | 15% | 15% | 20% |
| ORCH | 15% | 10% | 10% | **25%** |
| FAIL | 15% | **20%** | 10% | **20%** |
| CTX | 10% | **20%** | **25%** | 10% |
| META | 10% | **20%** | **20%** | 10% |

### 7-level progression (per workspace type)

| Level | Builder | Explorer | Designer | Operator |
|-------|---------|----------|----------|----------|
| L1 | Observer | Asker | Dreamer | User |
| L2 | Tinkerer | Curious | Sketcher | Repeater |
| L3 | Collaborator | Digger | Shaper | Optimizer |
| L4 | Pilot | Investigator | Planner | Builder |
| L5 | Architect | Analyst | Strategist | Engineer |
| L6 | Conductor | Synthesizer | Director | Orchestrator |
| L7 | Forgemaster | Scholar | Visionary | Automator |

Levels are scored to two decimal places internally, then rounded to 0.5 increments for display. The criterion is not "can you do this" but "do you do this consistently."

### Gate conditions

| Gate | Requirement |
|------|-------------|
| L3 | Context specificity ratio > 0.5 |
| L4 | Verification ratio > 0.15 AND correction ratio > 0.05 |
| L5 | Tool diversity > 8 (or orchestration tool present) AND strategic ratio > 0.05 |
| L6 | Multi-agent experience present |
| L7 | L6 gate + evidence of external contribution |

---

## Suggested routine

**Every Friday (15 min)**

```
1. /vibe-sunsang 변환      ← convert this week's sessions
2. 멘토링해줘               ← weekly review
3. Pick one thing to try next week
```

**Monthly (30 min)**

```
1. /vibe-sunsang 변환 force  ← full re-convert
2. 성장 리포트 만들어줘        ← monthly growth report
3. Compare with previous reports — trends are shown automatically
```

---

## File structure

All user data lives in `~/vibe-sunsang/`. Plugin code lives separately.

```
~/vibe-sunsang/
├── CLAUDE.md                 ← workspace description (created by onboarding)
├── .gitignore
├── config/                   ← project name map, workspace type classifications
├── conversations/            ← converted Markdown sessions
│   └── INDEX.md              ← full project index
├── exports/                  ← growth reports, mentor session saves
└── growth-log/
    ├── TIMELINE.md           ← level and 6-axis history across all reports
    └── weekly/               ← weekly retrospective notes
```

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.8+

---

## License

MIT

---

<div align="center">

**Stop guessing how to improve. Let your own conversations show you.**

</div>
