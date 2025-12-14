# TOS v0.3

Takagi Orchestration System - AI-powered task orchestrator

**本ドキュメントは初見者向けです。** TOS の概要と Quick Start を提供します。

運用詳細は [Runbook](docs/runbook.md) を参照してください。

---

## S-5 の目的

**S-5 = experimental 最終段階**

S-5 フェーズは TOS の experimental フェーズの最終段階です。以下を達成しています：

- job_loop 機能の実装完了
- job_input/job_result によるペイロード連携
- checkpoint/rollback による安全な実験環境
- 動作の安定性確認済み

**重要: S-6 は未定義です**

S-5 の次フェーズ（S-6）は現時点で定義されていません。S-5 をもって experimental フェーズは凍結されます。新機能追加や仕様変更は行いません。

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

## Documentation

- [Runbook](docs/runbook.md) - Detailed usage guide
- [Release Notes](docs/release_notes.md) - Version history
