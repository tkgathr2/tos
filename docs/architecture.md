# S-5 アーキテクチャ概要

## 1. システム構成

```
TOS v0.3 (S-5 experimental)
├── orchestrator_v0_3.py    # メインオーケストレーター
├── config_v0_3.json        # 設定ファイル
├── tools/
│   ├── cc_run.ps1          # ランチャースクリプト
│   └── checkpoint.ps1      # チェックポイント作成
├── workspace/
│   ├── phase_state.json    # フェーズ状態（自動生成）
│   └── artifacts/
│       ├── job_input.json  # ジョブ入力（任意）
│       ├── job_result.json # ジョブ結果（自動生成）
│       └── phase_summary.json  # フェーズサマリー（自動生成）
├── logs/
│   ├── step_*.json         # ステップログ（自動生成）
│   ├── last_run_summary.json  # 実行サマリー（自動生成）
│   └── last_checkpoint.txt # 最終チェックポイント（自動生成）
└── docs/
    ├── runbook.md          # 運用手順書
    ├── release_notes.md    # リリースノート
    ├── architecture.md     # 本ファイル
    ├── s5_definition.md    # S-5 定義書
    └── phase_summary_schema.md  # スキーマ定義
```

## 2. 処理フロー

```
[cc_run.ps1] → [orchestrator_v0_3.py] → [AI API] → [コマンド実行]
     ↓                    ↓
  モード判定          フェーズ管理
     ↓                    ↓
  run/test/         job_loop 制御
  cleanrun/              ↓
  checkpoint/       job_input.json 読込
  rollback               ↓
                    ステップ実行
                         ↓
                    phase_state.json 更新
                         ↓
                    job_result.json 出力
```

## 3. コンポーネント説明

### 3.1 cc_run.ps1

TOS のエントリーポイント。以下のモードを提供：

| モード | 説明 |
|--------|------|
| run | オーケストレーター実行 |
| test | 実行＋検証 |
| cleanrun | クリーンアップ後に実行 |
| checkpoint | Git チェックポイント作成 |
| rollback | チェックポイントへロールバック |

### 3.2 orchestrator_v0_3.py

メイン処理を担当：

- AI API 呼び出し（OpenAI / Anthropic）
- コマンド実行と結果収集
- フェーズ状態管理
- job_loop 制御

### 3.3 config_v0_3.json

設定を一元管理：

- execution_policy: コマンド実行ポリシー
- s5_settings: S-5 実験機能設定
  - job_loop: ジョブループ設定
  - job_input/job_result: ペイロード設定

## 4. 想定利用者像

### 4.1 主要利用者

**AI タスク自動化を行う開発者・運用者**

| 属性 | 内容 |
|------|------|
| 技術レベル | PowerShell / Python の基本操作が可能 |
| 業務内容 | AI を活用したタスク自動化 |
| 使用頻度 | 週数回〜日次 |

### 4.2 想定ユースケース

1. **単発タスク実行**
   - `cc_run.ps1 -Mode run` で 1 回のタスク実行
   - 結果は logs/ に保存

2. **連続ジョブ実行**
   - job_loop で複数ジョブを順次実行
   - job_input.json で外部パラメータを渡す
   - job_result.json で結果を受け取る

3. **実験と復旧**
   - checkpoint で安全地点を作成
   - 問題発生時は rollback で復旧

### 4.3 非対象ユースケース

- GUI ベースの操作（CLI のみ）
- リアルタイム監視（バッチ処理向け）
- 大規模分散処理（単一マシン向け）

## 5. 用語定義

| 用語 | 定義 |
|------|------|
| experimental | 動作保証あり・仕様保証なし |
| job_loop | 複数ジョブの順次実行機能 |
| job_loop_complete | job_loop が max_jobs に到達した状態 |
| checkpoint | Git コミットによる復旧点 |
| phase_state | 現在のフェーズと状態を保持するファイル |
| step_log | 各ステップの実行ログ |

## 6. S-5 固有の制約

- **仕様凍結**: 新機能追加なし
- **設定固定**: config_v0_3.json スキーマ変更なし
- **後方互換**: 既存動作の維持が必須
