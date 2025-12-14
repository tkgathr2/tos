# TOS v0.3

Takagi Orchestration System - AI-powered task orchestrator

**このリポジトリは完成品です。TOS v0.3 は 2025-12-14 に完結・封印されました。**

**本ドキュメントは初見者向けです。** TOS の概要と Quick Start を提供します。

運用詳細は [Runbook](docs/runbook.md) を参照してください。

**全ドキュメントの索引は [docs/index.md](docs/index.md) を参照してください。**

---

## TOS v0.3 完結・封印

**TOS v0.3 S-6 stable は 2025-12-14 に完結・封印されました。**

**以後は運用のみが許可されます。機能追加・仕様変更は禁止です。**

封印宣言の詳細は [S-6 最終封印宣言](docs/s6_sealed.md) を参照してください。

---

## S-6 Stable 完成・封印

**S-6 stable フェーズは 2025-12-14 に完成・封印されました。**

**S-6 の目的**: S-5 で確立した機能を安定運用し、実運用環境での継続的な利用を可能にする。

**S-6 完成により達成されたこと**:
- 運用基盤・判断基準の確立
- 拡張可否ルールの明文化
- リスク・限界の明示
- 将来引き継ぎ耐性の確保

詳細は [S-6 Completion](docs/s6_completion.md) を参照してください。

### S-7 は実施しない

**S-7（拡張フェーズ）は 2025-12-14 に「不要」と確定しました。**

- 自動リトライ機能は S-6 で既に実装済み
- 残りの機能は外部ツール/手動運用で代替可能
- S-6 stable の安定運用を優先

再検討は 2025-06-14 以降、または明文化されたトリガー条件発生時のみ許可。
詳細は [S-7 検討結果](docs/s7_proposal.md) を参照してください。

### S-5 は履歴フェーズ

S-5 フェーズは 2025-12-14 に closeout 完了し、履歴フェーズとなりました。S-5 への変更は禁止されています。

S-5 で達成した内容：
- job_loop 機能の実装完了
- job_input/job_result によるペイロード連携
- checkpoint/rollback による安全な実験環境
- 動作の安定性確認済み

### フェーズ一覧（最終版）

| フェーズ | ステータス | 変更 | 目的 |
|---------|----------|------|------|
| S-4 | 履歴 | 禁止 | 基本機能実装 |
| S-5 | 履歴（凍結） | 禁止 | experimental |
| S-6 | **完成・封印** | **禁止** | 安定運用 |
| S-7 | 不要（確定） | N/A | 実施しない |

**S-6 は封印状態です。今後の変更は原則禁止されています。**

詳細は [S-6 Stable](docs/s6_stable.md)、[S-6 最終封印宣言](docs/s6_sealed.md) を参照してください。

---

## Requirements

- Python 3.12+
- PowerShell
- Environment variables:
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY

## Quick Start

```powershell
cd C:\Users\takag\00_dev\tos

# Run orchestrator
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run

# Run with test verification
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test

# Clean run (reset and run)
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun

# Create checkpoint
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName my_checkpoint

# Rollback to last checkpoint
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
```

## S-5 Experimental Mode

S-5 is an experimental phase. Results may be unstable.

主要機能:
- **job_loop**: 複数ジョブの順次実行（max_jobs で上限指定）
- **job_input/job_result**: 外部ペイロードの入出力

詳細な設定と使用方法は [Runbook](docs/runbook.md) を参照してください。

## Example（S-5 再現手順）

example を使用して S-5 の動作を再現できます。

### example の目的

- 第三者が S-5 の動作を最小手順で確認できる
- cleanrun → test → run の正しい実行順序を示す
- 入力から出力までの一連の流れを体験できる

### 最小 payload

`workspace/artifacts/job_input.example.json` を `job_input.json` にコピーして使用します：

```json
{
  "job_name": "example_job",
  "target": "example_target",
  "params": {
    "key1": "value1"
  }
}
```

job_name フィールドで config の job_name を上書きできます。

### 実行手順

```powershell
cd C:\Users\takag\00_dev\tos

# 1. checkpoint 作成（必須）
powershell -ExecutionPolicy Bypass -File .\tools\checkpoint.ps1 -Name "before_example"

# 2. example 用 job_input をコピー
Copy-Item workspace\artifacts\job_input.example.json workspace\artifacts\job_input.json

# 3. cleanrun で初期化実行
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun

# 4. test で状態確認
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test

# 5. run で継続実行（job_loop_complete まで繰り返し）
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
```

### 生成される成果物

| ファイル | 説明 |
|---------|------|
| logs/steps/step_*.json | 各ステップの実行ログ |
| workspace/phase_state.json | フェーズ状態 |
| workspace/artifacts/phase_summary.json | フェーズサマリー |
| workspace/artifacts/job_result.json | job_loop_complete 時の結果 |
| logs/last_run_summary.json | 実行サマリー（JSON） |
| logs/last_run_summary.txt | 実行サマリー（1行テキスト） |

### 想定ログ構成

正常終了時、logs/steps/ 配下には以下が生成されます：

- step_001.json: 最初のステップログ（job_index=1）
- step_002.json 以降: 継続実行時のステップログ

各 step_*.json には以下が含まれます：
- phase: 現在のフェーズ（done, job_loop_complete など）
- job_loop_enabled: true
- job_name: ジョブ名
- job_index: 現在のジョブインデックス

### 失敗時の切り分け

| 症状 | 原因 | 対処 |
|------|------|------|
| job_input.json not found | 入力不備 | job_input.example.json をコピー |
| config error | config 不備 | config_v0_3.json を確認 |
| API error | API キー不備 | 環境変数 OPENAI_API_KEY / ANTHROPIC_API_KEY を確認 |
| unexpected phase | 実行モード誤り | cleanrun で初期化してから再実行 |

### checkpoint / rollback

- **checkpoint 作成タイミング**: example 実行前に必ず作成
- **rollback 手順**:
  ```powershell
  # 最後の checkpoint に戻す
  powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
  ```
- **rollback 後の確認**: test モードで状態を確認

---

## 正史コンテキスト v1.0

**本リポジトリは正史コンテキスト v1.0 に準拠しています。**

正史コンテキストとは、TOS の開発・運用における唯一の正しい文脈を定義するものです。

### 正史の前提

- TOS v0.3 は S-6 stable フェーズで運用中
- S-5 は履歴フェーズとして凍結済み
- 新機能追加・仕様変更は行わない（安定維持優先）
- 本リポジトリのドキュメントが唯一の正しい情報源

### 禁止事項

- 正史を無視した運用は禁止
- ドキュメントに記載のない独自拡張は禁止
- S-5/S-6 で定義されていない機能の使用は禁止

### 正史更新履歴

- 2025-12-14: S-5 closeout 完了
- 2025-12-14: S-6 stable 開始
- 2025-12-14: S-6 stable 完成
- 2025-12-14: S-7 結論「やらない」を確定
- 2025-12-14: **TOS v0.3 完結・S-6 最終封印**

詳細は [S-6 Stable](docs/s6_stable.md)、[S-6 最終封印宣言](docs/s6_sealed.md)、[S-7 検討結果](docs/s7_proposal.md) を参照してください。

---

## Documentation

**全ドキュメントの索引: [docs/index.md](docs/index.md)**

### S-6 Stable（完成・封印）

- [S-6 最終封印宣言](docs/s6_sealed.md) - TOS v0.3 完結・封印宣言
- [S-6 Stable](docs/s6_stable.md) - S-6 フェーズ定義・運用ルール
- [S-6 Operations](docs/s6_operations.md) - 安定運用ガイド（運用フロー・ログ・組織）
- [S-6 Governance](docs/s6_governance.md) - ガバナンス・判断基準・拡張ルール
- [S-6 Environment](docs/s6_environment.md) - 実行環境標準（PowerShell・改行）
- [S-6 Completion](docs/s6_completion.md) - S-6 完成宣言
- [S-6 Routines](docs/s6_routines.md) - 日次/週次/月次/障害対応ルーチン
- [S-6 Stable Checklist](docs/s6_stable_checklist.md) - 運用チェックリスト
- [Runbook](docs/runbook.md) - 運用手順ガイド
- [Glossary](docs/glossary.md) - 用語集
- [Failure Report Template](docs/failure_report_template.md) - 障害報告テンプレート
- [Release Notes](docs/release_notes.md) - 変更履歴
- [S-6 1枚資料](docs/s6_one_pager.md) - 運用者向けクイックリファレンス
- [周知メッセージ雛形](docs/ops_announcement_slack.md) - Slack/Teams 周知テンプレート
- [30分研修](docs/s6_training_30min.md) - 運用者向け最短研修コース
- [エスカレーション](docs/ops_escalation.md) - 障害レベル・連絡先・判断基準

### S-5（履歴フェーズ）

- [S-5 Closeout](docs/s5_closeout.md) - S-5 closeout 宣言
- [S-5 Definition](docs/s5_definition.md) - S-5 フェーズ定義
- [S-5 Closeout Checklist](docs/s5_closeout_checklist.md) - closeout チェックリスト

### 引き継ぎ時の推奨読み順

1. **README.md**（本ファイル）- 概要把握
2. **docs/s6_stable.md** - S-6 運用ルールの確認
3. **docs/s6_operations.md** - 安定運用ガイド
4. **docs/s6_governance.md** - ガバナンス・判断基準
5. **docs/s6_environment.md** - 実行環境標準
6. **docs/runbook.md** - 運用手順の確認
7. **docs/glossary.md** - 用語の確認
8. **docs/s6_stable_checklist.md** - 運用チェックリスト
9. **docs/release_notes.md** - 変更履歴の確認

---

## 改行差分（LF/CRLF）の扱い

### 方針

- リポジトリ内は LF を標準とする
- `.gitattributes` で改行方針を管理
- 改行差分のみのコミットは避ける

### 改行差分が出た場合

1. 内容に変更がなければ無視してよい（警告のみ）
2. `.gitattributes` の設定を確認
3. 必要に応じて `git checkout -- <file>` で元に戻す
