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

## execution_policy

config_v0_3.json execution_policy settings

### default_action

- allow: commands are allowed by default
- deny: all commands are denied

### deny_if_contains

list of keywords that trigger command denial

```json
"execution_policy": {
  "default_action": "allow",
  "deny_if_contains": [
    "Remove-Item",
    "rmdir",
    "del "
  ]
}
```

### behavior

- deny check runs before allowlist check
- denied commands are not retried
- phase_state.current_phase becomes "deny" when all commands are denied
- cc_run.ps1 shows "deny <reason>" when phase is deny

## deny vs fatal_error

### deny

- triggered by execution_policy deny_if_contains or deny_patterns
- command was not allowed to execute
- recoverable: fix config or prompt to avoid denied commands
- exit code 1

### fatal_error

- triggered by unrecoverable errors (API failure, system error)
- command execution or API call failed
- may require manual intervention
- exit code 1

### stopped

- step_log.stopped=true indicates execution was halted
- stopped steps are not counted in success_count
- cc_run.ps1 shows "stopped phase=<phase> step=<step_num>" when stopped=true
- phase_summary includes stopped_steps and stopped_count

### phase_summary

- denied_steps: list of steps with phase=deny
- fatal_error_steps: list of steps with phase=fatal_error
- stopped_steps: list of steps with stopped=true
- denied_count: number of deny steps
- fatal_error_count: number of fatal_error steps
- stopped_count: number of stopped steps
- stop_on_deny: current stop_on_deny setting value
- end_reason: reason for execution termination

## stop_on_deny

### configuration

```json
"execution_policy": {
  "default_action": "allow",
  "stop_on_deny": true,
  "deny_if_contains": [
    "Remove-Item",
    "rmdir",
    "del "
  ]
}
```

### behavior

- stop_on_deny=true (default): execution stops immediately when deny occurs
- stop_on_deny=false: execution continues to next step after deny
- when stopped, step_log.stopped=true and end_reason is set

### example with stop_on_deny=false

```json
"execution_policy": {
  "default_action": "allow",
  "stop_on_deny": false,
  "deny_if_contains": ["Remove-Item"]
}
```

This allows the orchestrator to skip denied commands and continue with subsequent steps.
