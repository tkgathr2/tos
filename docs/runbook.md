# TOS v0.3 Runbook

## cc_run.ps1

TOS orchestrator launcher

### usage

```
usage cc_run.ps1 -Mode run|test|cleanrun -Clean -SummaryFile path
```

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

JSON content
- phase
- step
- done
- latest_step
- step_count
- phase_summary_exists

TXT content
- 1 line format
- phase=done step=1 done=True latest_step=step_001.json step_count=1 phase_summary=exists

### Clean option

cleanup before execution

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run -Clean
```
