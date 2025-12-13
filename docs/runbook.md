# TOS v0.3 Runbook

## cc_run.ps1

TOS orchestrator launcher

### run mode

orchestrator execution

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
```

### test mode

orchestrator execution with verification

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test
```

### cleanrun mode

cleanup then orchestrator execution

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun
```

### SummaryFile option

save execution summary to JSON and TXT

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run -SummaryFile logs\last_run_summary.json
```

output files
- logs/last_run_summary.json
- logs/last_run_summary.txt

### Clean option

cleanup before execution

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run -Clean
```
