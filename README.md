# TOS v0.3

Takagi Orchestration System - AI-powered task orchestrator

**本ドキュメントは初見者向けです。** TOS の概要と Quick Start を提供します。

運用詳細は [Runbook](docs/runbook.md) を参照してください。

---

## S-5 Closeout 完了

**S-5 フェーズは 2025-12-14 に closeout 完了しました。**

**S-5 は履歴フェーズです。以後の変更は禁止されています。**

S-5 フェーズは TOS の experimental フェーズの最終段階として、以下を達成しました：

- job_loop 機能の実装完了
- job_input/job_result によるペイロード連携
- checkpoint/rollback による安全な実験環境
- 動作の安定性確認済み

**重要: S-6 は未定義です**

S-5 の次フェーズ（S-6）は現時点で定義されていません。S-5 をもって experimental フェーズは凍結されました。新機能追加や仕様変更は行いません。

**注意**: 以下の Example セクションは S-5 動作確認用の履歴記録です。新規運用ではなく、rollback による復旧確認目的でのみ使用してください。

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

- TOS v0.3 は S-5 フェーズで凍結されています
- S-5 以降の新機能追加・仕様変更は行いません
- 本リポジトリのドキュメントが唯一の正しい情報源です

### 禁止事項

- 正史を無視した運用は禁止されています
- ドキュメントに記載のない独自拡張は禁止されています
- S-5 で定義されていない機能の使用は禁止されています

詳細は [S-5 Closeout](docs/s5_closeout.md) を参照してください。

---

## Documentation

- [Runbook](docs/runbook.md) - Detailed usage guide
- [Release Notes](docs/release_notes.md) - Version history
- [S-5 Closeout](docs/s5_closeout.md) - S-5 closeout declaration
- [S-5 Definition](docs/s5_definition.md) - S-5 phase definition
- [S-5 Closeout Checklist](docs/s5_closeout_checklist.md) - Closeout verification checklist

### 引き継ぎ時の推奨読み順

1. **README.md**（本ファイル）- 概要把握
2. **docs/s5_closeout.md** - closeout 宣言・禁止事項の確認
3. **docs/runbook.md** - 運用手順の確認（rollback 専用）
4. **docs/s5_definition.md** - S-5 の技術的定義
5. **docs/release_notes.md** - 変更履歴の確認
