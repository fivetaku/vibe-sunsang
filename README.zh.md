[English](README.md) | [한국어](README.ko.md) | 中文 | [日本語](README.ja.md) | [Español](README.es.md)

# vibe-sunsang (바선생)

<p align="center">
  <img src="assets/vibe-sunsang-hero-01.png" alt="vibe-sunsang" width="320">
</p>

> **把你的 Claude Code 对话历史变成成长引擎的 AI 导师智能体。**

vibe-sunsang 会自动收集、转换并分析你与 Claude Code 的每一次对话——让你随着时间推移成为更高效的 AI 协作者。

[快速开始](#快速开始) • [为什么选 vibe-sunsang？](#为什么选-vibe-sunsang) • [工作原理](#工作原理) • [功能模式](#功能模式) • [等级系统](#等级系统) • [环境要求](#环境要求)

---

## 快速开始

### 1. 安装

```
/plugin marketplace add https://github.com/fivetaku/gptaku_plugins.git
/plugin install vibe-sunsang
```

然后**重启 Claude Code**。

### 2. 运行引导流程

在任意项目中：

```
/vibe-sunsang 시작
```

引导流程会：

1. 创建 `~/vibe-sunsang/` 工作区（含 `CLAUDE.md`、`.gitignore` 和 `git init`）
2. 扫描 `~/.claude/projects/` 中的 Claude Code 对话历史
3. 让你为发现的每个项目指定易读的名称
4. 按工作区类型（Builder / Explorer / Designer / Operator）对每个项目分类
5. 首次将所有 JSONL 日志转换为 Markdown
6. 询问是直接进入导师辅导，还是先生成成长报告

### 3. 每周使用

```
/vibe-sunsang 변환      ← convert this week's conversations
/vibe-sunsang 멘토링    ← get coaching on your AI usage patterns
/vibe-sunsang 성장      ← generate a growth report
/vibe-sunsang 지식      ← explore the level system and concepts
```

---

## 为什么选 vibe-sunsang？

- **数据早已在你的对话里** —— Claude Code 把每个会话都存为 JSONL。vibe-sunsang 直接读取这些文件，无需额外记录任何东西
- **不只看"做了什么"，更看"怎么做的"** —— 分析聚焦于你的请求质量、错误恢复习惯和战略思维，而不只是产出数量
- **感知工作区类型** —— 等级系统会根据你实际在做的事（编码、调研、规划或自动化）自适应
- **六个维度，而非一个分数** —— DECOMP、VERIFY、ORCH、FAIL、CTX、META 各自独立测量，让你精确知道下一步该提升哪项能力
- **纵向追踪** —— 每份成长报告都会更新 `TIMELINE.md`，让你看到跨越数月的进步，而不只是单次会话
- **对非开发者友好** —— 用比喻讲解的平实辅导，没有术语门槛

---

## 工作原理

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

对话数据与插件代码存放在完全独立的目录中，插件更新永远不会触碰你的数据。

---

## 功能模式

### 引导 (`시작`)

创建 `~/vibe-sunsang/` 工作区，映射项目名称，分类工作区类型，并执行首次完整转换。

---

### 转换 (`변환`)

把 Claude Code 的 JSONL 日志转换为按项目组织、易于阅读的 Markdown 文件。

| 命令 | 行为 |
|------|------|
| `/vibe-sunsang 변환` | 增量转换 —— 只处理新会话 |
| `/vibe-sunsang 변환 force` | 完整重新转换 |
| `/vibe-sunsang 변환 <project name>` | 仅转换单个项目 |

每个转换后的文件都带有元数据 frontmatter：日期、token 数、所用模型、调用过的工具。`INDEX.md` 让你一眼掌握全貌。

---

### 导师辅导 (`멘토링`)

四种辅导模式，各自聚焦不同的能力维度：

| 模式 | 触发语 | 作用 | 核心轴 |
|------|--------|------|--------|
| **A —— 请求质量** | "요청 코칭해줘" | 按清晰度和上下文给你的提示词打 A–D 等级 | DECOMP + CTX |
| **B —— 反模式诊断** | "뭘 잘못하고 있는지" | 结合具体案例和改进策略，检测坏习惯 | FAIL + VERIFY |
| **C —— 概念学习** | "이게 뭐야" | 用平实语言讲解你最近会话中出现的概念 | META |
| **D —— 全面辅导**（默认） | "멘토링해줘" | 完整的 6 轴体检、等级判定和行动计划 | 全部 6 轴 |

模式 D 会输出文本雷达图和三步行动计划：现在就做的一件事、本周做的一件事、一个月内完成的一件事。

辅导结果可保存到 `~/vibe-sunsang/exports/mentor-YYYY-MM-DD.md`。

---

### 成长报告 (`성장`)

把分析委托给专用的 `growth-analyst` 子智能体，保持主上下文轻量。该智能体读取你的会话文件，为全部六个维度打分，并写出完整报告。

**时间范围选项：**

| 范围 | 覆盖 |
|------|------|
| 本周 | 最近 7 天 |
| 最近两周（推荐） | 最近 14 天 |
| 本月 | 最近 30 天 |
| 特定项目 | 项目全部历史 |

**报告内容包括：**

1. 基础统计 —— 会话数、消息数、token 用量
2. 带分数与权重的 6 轴技术维度分析
3. 文本雷达图
4. 门槛条件达成状态表（进入下一等级的要求）
5. 反模式检测（按你的工作区类型校准）
6. 与以往所有报告的纵向对比
7. 带进度条的等级卡片
8. 升级时的晋级消息（L4→L5 有特别的"80% 之墙"事件）
9. `TIMELINE.md` 自动更新

---

### 知识 (`지식`)

回答关于 vibe-sunsang 框架本身的问题：

| 主题 | 说明 |
|------|------|
| 等级系统 | 7 级成长体系（0.5 级递增）及各等级的含义 |
| 六个轴 | DECOMP、VERIFY、ORCH、FAIL、CTX、META 的定义与示例 |
| 工作区类型 | Builder / Explorer / Designer / Operator 对你的分析意味着什么 |
| 反模式 | 按工作区类型校准的、需要警惕的坏习惯 |
| 请求质量 | 如何写出更好的提示词 |
| 成长指标 | Fit Score 公式、门槛条件、类型专属权重 |

---

## 等级系统

### 6 个技术维度

| 代码 | 维度 | 一句话定义 |
|------|------|-----------|
| **DECOMP** | 任务分解 | 把复杂请求拆成 AI 能处理的单元 |
| **VERIFY** | 验证策略 | 批判性地审查 AI 输出，而不是照单全收 |
| **ORCH** | 编排 | 组合工具、智能体与工作流 |
| **FAIL** | 失败恢复 | 诊断错误并找到替代方案 |
| **CTX** | 上下文管理 | 向 AI 提供背景、约束与目标 |
| **META** | 元认知 | 觉察并战略性地调整自己的 AI 使用模式 |

### 工作区类型与权重

分析权重会随你实际在做的事而变化：

| 维度 | Builder | Explorer | Designer | Operator |
|------|---------|----------|----------|----------|
| DECOMP | **25%** | 15% | 20% | 15% |
| VERIFY | **25%** | 15% | 15% | 20% |
| ORCH | 15% | 10% | 10% | **25%** |
| FAIL | 15% | **20%** | 10% | **20%** |
| CTX | 10% | **20%** | **25%** | 10% |
| META | 10% | **20%** | **20%** | 10% |

### 7 级成长体系（按工作区类型）

| 等级 | Builder | Explorer | Designer | Operator |
|------|---------|----------|----------|----------|
| L1 | Observer | Asker | Dreamer | User |
| L2 | Tinkerer | Curious | Sketcher | Repeater |
| L3 | Collaborator | Digger | Shaper | Optimizer |
| L4 | Pilot | Investigator | Planner | Builder |
| L5 | Architect | Analyst | Strategist | Engineer |
| L6 | Conductor | Synthesizer | Director | Orchestrator |
| L7 | Forgemaster | Scholar | Visionary | Automator |

等级在内部精确到小数点后两位，展示时按 0.5 级取整。判定标准不是"你能不能做到"，而是"你是否始终如一地这样做"。

### 门槛条件

| 门槛 | 要求 |
|------|------|
| L3 | 上下文具体性比率 > 0.5 |
| L4 | 验证比率 > 0.15 且修正比率 > 0.05 |
| L5 | 工具多样性 > 8（或使用过编排工具）且战略性比率 > 0.05 |
| L6 | 具备多智能体经验 |
| L7 | 通过 L6 门槛 + 有外部贡献的证据 |

---

## 推荐例行安排

**每周五（15 分钟）**

```
1. /vibe-sunsang 변환      ← convert this week's sessions
2. 멘토링해줘               ← weekly review
3. Pick one thing to try next week
```

**每月一次（30 分钟）**

```
1. /vibe-sunsang 변환 force  ← full re-convert
2. 성장 리포트 만들어줘        ← monthly growth report
3. Compare with previous reports — trends are shown automatically
```

---

## 文件结构

所有用户数据都存放在 `~/vibe-sunsang/`，插件代码存放在别处。

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

## 环境要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.8+

### 对话来源路径

vibe-sunsang 默认从 `~/.claude/projects/` 读取会话。解析顺序：

1. `--projects-dir <path>` 参数（传给 `convert_sessions.py`）
2. 如果设置了 `CLAUDE_CONFIG_DIR` 环境变量，则用 `$CLAUDE_CONFIG_DIR/projects`
3. `~/.claude/projects/`（默认）
4. WSL 回退：`/mnt/c/Users/$USER/.claude/projects`（仅当 1–3 都无法解析时）

跨环境运行（如 WSL ↔ Windows）或 Claude 配置不在 `~/.claude/` 时，请使用 `--projects-dir`：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py \
  --projects-dir /custom/path/.claude/projects \
  --output-dir "$HOME/vibe-sunsang/conversations"
```

---

## 许可证

MIT

---

<div align="center">

**别再猜怎么提升了。让你自己的对话告诉你答案。**

</div>
