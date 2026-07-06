[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | 日本語 | [Español](README.es.md)

# vibe-sunsang (바선생)

<p align="center">
  <img src="assets/vibe-sunsang-hero-01.png" alt="vibe-sunsang" width="320">
</p>

> **Claude Code の会話履歴を成長エンジンに変える AI メンターエージェント。**

vibe-sunsang は、あなたが Claude Code と交わしたすべての会話を自動で収集・変換・分析します。時間をかけて、より効果的な AI コラボレーターになるために。

[クイックスタート](#クイックスタート) • [なぜ vibe-sunsang？](#なぜ-vibe-sunsang) • [仕組み](#仕組み) • [モード](#モード) • [レベルシステム](#レベルシステム) • [動作要件](#動作要件)

---

## クイックスタート

### 1. インストール

```
/plugin marketplace add https://github.com/fivetaku/gptaku_plugins.git
/plugin install vibe-sunsang
```

その後、**Claude Code を再起動**してください。

### 2. オンボーディングを実行

任意のプロジェクトで：

```
/vibe-sunsang 시작
```

オンボーディングが行うこと：

1. `~/vibe-sunsang/` ワークスペースを作成（`CLAUDE.md`、`.gitignore`、`git init` 込み）
2. `~/.claude/projects/` にある Claude Code の会話履歴をスキャン
3. 見つかったプロジェクトに読みやすい名前を付与
4. 各プロジェクトをワークスペースタイプ（Builder / Explorer / Designer / Operator）で分類
5. すべての JSONL ログを初回 Markdown 変換
6. そのままメンタリングに進むか、成長レポートを作るかを選択

### 3. 毎週使う

```
/vibe-sunsang 변환      ← convert this week's conversations
/vibe-sunsang 멘토링    ← get coaching on your AI usage patterns
/vibe-sunsang 성장      ← generate a growth report
/vibe-sunsang 지식      ← explore the level system and concepts
```

---

## なぜ vibe-sunsang？

- **データはすでに会話の中にある** —— Claude Code はすべてのセッションを JSONL で保存しています。vibe-sunsang はそのファイルを読むので、新たに記録するものは何もありません
- **「何を作ったか」ではなく「どう作ったか」** —— 分析の焦点は、成果物の量ではなく、リクエストの質・エラーからの立て直し方・戦略的思考です
- **ワークスペースタイプを考慮** —— コーディング、リサーチ、企画、自動化——実際に何をしているかに合わせてレベルシステムが適応します
- **単一スコアではなく 6 つのディメンション** —— DECOMP、VERIFY、ORCH、FAIL、CTX、META を独立に測定するので、次に伸ばすべきスキルが正確にわかります
- **縦断トラッキング** —— 成長レポートのたびに `TIMELINE.md` が更新され、単一セッションではなく数か月単位の進歩が見えます
- **非開発者にもやさしい** —— たとえ話を交えた平易な言葉のコーチング。専門用語の壁はありません

---

## 仕組み

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

会話データとプラグインコードは別々のディレクトリに置かれるため、プラグインを更新してもデータには一切触れません。

---

## モード

### オンボード (`시작`)

`~/vibe-sunsang/` ワークスペースをセットアップし、プロジェクト名をマッピングし、ワークスペースタイプを分類し、初回のフル変換を実行します。

---

### 変換 (`변환`)

Claude Code の JSONL ログを、プロジェクトごとに整理された読みやすい Markdown ファイルに変換します。

| コマンド | 動作 |
|---------|------|
| `/vibe-sunsang 변환` | 増分変換 —— 新しいセッションのみ |
| `/vibe-sunsang 변환 force` | フル再変換 |
| `/vibe-sunsang 변환 <project name>` | 単一プロジェクトのみ |

変換された各ファイルにはメタデータの frontmatter が付きます：日付、トークン数、使用モデル、呼び出したツール。`INDEX.md` で全体像を一目で把握できます。

---

### メンター (`멘토링`)

それぞれ異なるスキルディメンションに焦点を当てた 4 つのコーチングモード：

| モード | トリガー | 内容 | 中心軸 |
|------|---------|------|--------|
| **A —— リクエスト品質** | "요청 코칭해줘" | プロンプトの明確さと文脈を A–D で採点 | DECOMP + CTX |
| **B —— アンチパターン診断** | "뭘 잘못하고 있는지" | 具体例と改善策つきで悪い習慣を検出 | FAIL + VERIFY |
| **C —— 概念学習** | "이게 뭐야" | 最近のセッションに登場した概念を平易な言葉で解説 | META |
| **D —— フルコーチング**（デフォルト） | "멘토링해줘" | 6 軸の総合チェック、レベル判定、行動計画 | 6 軸すべて |

モード D は、テキストのレーダーチャートと 3 段階の行動計画を出力します：今すぐやること 1 つ、今週やること 1 つ、1 か月以内にやること 1 つ。

コーチング結果は `~/vibe-sunsang/exports/mentor-YYYY-MM-DD.md` に保存できます。

---

### 成長レポート (`성장`)

メインコンテキストを軽く保つため、分析を専用の `growth-analyst` サブエージェントに委任します。エージェントはセッションファイルを読み、6 つのディメンションすべてを採点し、完全なレポートを書き上げます。

**期間オプション：**

| 期間 | 対象 |
|------|------|
| 今週 | 直近 7 日 |
| 直近 2 週間（推奨） | 直近 14 日 |
| 今月 | 直近 30 日 |
| 特定プロジェクト | プロジェクトの全履歴 |

**レポートに含まれるもの：**

1. 基本統計 —— セッション数、メッセージ数、トークン使用量
2. スコアと重みつきの 6 軸技術ディメンション分析
3. テキストのレーダーチャート
4. ゲート条件の充足状況テーブル（次のレベルに到達するための要件）
5. アンチパターン検出（ワークスペースタイプに合わせて調整）
6. 過去の全レポートとの縦断比較
7. 進行バーつきレベルカード
8. レベルアップ時の昇格メッセージ（L4→L5 には特別な「80% の壁」イベント）
9. `TIMELINE.md` の自動更新

---

### 知識 (`지식`)

vibe-sunsang のフレームワーク自体に関する質問に答えます：

| トピック | 説明 |
|---------|------|
| レベルシステム | 7 段階の成長レベル（0.5 刻み）と各レベルの意味 |
| 6 つの軸 | DECOMP、VERIFY、ORCH、FAIL、CTX、META の定義と例 |
| ワークスペースタイプ | Builder / Explorer / Designer / Operator が分析にとって何を意味するか |
| アンチパターン | ワークスペースタイプ別に注意すべき悪い習慣 |
| リクエスト品質 | より良いプロンプトの書き方 |
| 成長指標 | Fit Score の計算式、ゲート条件、タイプ別の重み |

---

## レベルシステム

### 6 つの技術ディメンション

| コード | ディメンション | 一行定義 |
|------|-----------|---------|
| **DECOMP** | タスク分解 | 複雑なリクエストを AI が扱える単位に分ける |
| **VERIFY** | 検証戦略 | AI の出力を鵜呑みにせず批判的にレビューする |
| **ORCH** | オーケストレーション | ツール、エージェント、ワークフローを組み合わせる |
| **FAIL** | 失敗からの回復 | エラーを診断し、代替手段を見つける |
| **CTX** | コンテキスト管理 | 背景、制約、目標を AI に供給する |
| **META** | メタ認知 | 自分の AI 活用パターンを認識し、戦略的に調整する |

### ワークスペースタイプと重み

実際に何をしているかによって分析の重みが変わります：

| ディメンション | Builder | Explorer | Designer | Operator |
|-----------|---------|----------|----------|----------|
| DECOMP | **25%** | 15% | 20% | 15% |
| VERIFY | **25%** | 15% | 15% | 20% |
| ORCH | 15% | 10% | 10% | **25%** |
| FAIL | 15% | **20%** | 10% | **20%** |
| CTX | 10% | **20%** | **25%** | 10% |
| META | 10% | **20%** | **20%** | 10% |

### 7 段階のレベル（ワークスペースタイプ別）

| レベル | Builder | Explorer | Designer | Operator |
|-------|---------|----------|----------|----------|
| L1 | Observer | Asker | Dreamer | User |
| L2 | Tinkerer | Curious | Sketcher | Repeater |
| L3 | Collaborator | Digger | Shaper | Optimizer |
| L4 | Pilot | Investigator | Planner | Builder |
| L5 | Architect | Analyst | Strategist | Engineer |
| L6 | Conductor | Synthesizer | Director | Orchestrator |
| L7 | Forgemaster | Scholar | Visionary | Automator |

レベルは内部的に小数点以下 2 桁まで採点され、表示時に 0.5 刻みに丸められます。基準は「できるか」ではなく「一貫してやっているか」です。

### ゲート条件

| ゲート | 要件 |
|------|------|
| L3 | コンテキスト具体性比率 > 0.5 |
| L4 | 検証比率 > 0.15 かつ 修正比率 > 0.05 |
| L5 | ツール多様性 > 8（またはオーケストレーションツールの使用）かつ 戦略的比率 > 0.05 |
| L6 | マルチエージェント経験あり |
| L7 | L6 のゲート + 外部貢献の証拠 |

---

## おすすめルーティン

**毎週金曜（15 分）**

```
1. /vibe-sunsang 변환      ← convert this week's sessions
2. 멘토링해줘               ← weekly review
3. Pick one thing to try next week
```

**毎月（30 分）**

```
1. /vibe-sunsang 변환 force  ← full re-convert
2. 성장 리포트 만들어줘        ← monthly growth report
3. Compare with previous reports — trends are shown automatically
```

---

## ファイル構成

ユーザーデータはすべて `~/vibe-sunsang/` に置かれます。プラグインコードは別の場所にあります。

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

## 動作要件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.8+

### 会話ソースのパス

デフォルトでは vibe-sunsang は `~/.claude/projects/` からセッションを読み込みます。解決順序：

1. `--projects-dir <path>` フラグ（`convert_sessions.py` に渡す）
2. `CLAUDE_CONFIG_DIR` 環境変数が設定されていれば `$CLAUDE_CONFIG_DIR/projects`
3. `~/.claude/projects/`（デフォルト）
4. WSL フォールバック：`/mnt/c/Users/$USER/.claude/projects`（1–3 で解決しない場合のみ）

クロス環境（WSL ↔ Windows など）で実行する場合や、Claude の設定が `~/.claude/` の外にある場合は `--projects-dir` を使ってください：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py \
  --projects-dir /custom/path/.claude/projects \
  --output-dir "$HOME/vibe-sunsang/conversations"
```

---

## ライセンス

MIT

---

<div align="center">

**どう成長すべきか、もう推測しない。あなた自身の会話が教えてくれる。**

</div>
