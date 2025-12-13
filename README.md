# TOS v0.3

Takagi Orchestration System - AI-powered task orchestrator

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

### job_loop

job_loop allows running multiple jobs sequentially (max_jobs limit). Each run executes one job cycle.

```json
"s5_settings": {
  "enabled": true,
  "job_loop": {
    "enabled": true,
    "max_jobs": 3,
    "job_name": "sample"
  }
}
```

## Documentation

- [Runbook](docs/runbook.md) - Detailed usage guide
- [Release Notes](docs/release_notes.md) - Version history
