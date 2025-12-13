# TOS v0.3 Runbook

See also: [README.md](../README.md) for quick start guide.

## cc_run.ps1

TOS orchestrator launcher

### usage

```
usage cc_run.ps1 -Mode run|test|cleanrun|checkpoint|rollback -Clean -SummaryFile path
  checkpoint: -CheckpointName <text>
  rollback: -TargetCommit <hash> (optional, uses last_checkpoint.txt if not specified)
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

### checkpoint mode

create a git checkpoint commit

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName S4_before_big_change
```

- creates commit with message "CHECKPOINT <name>"
- saves commit hash to logs/last_checkpoint.txt
- output: checkpoint <hash>

### rollback mode

rollback to a previous checkpoint

```powershell
# rollback to last checkpoint
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback

# rollback to specific commit
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback -TargetCommit abc1234
```

- requires clean working tree (no uncommitted changes)
- if -TargetCommit not specified, uses logs/last_checkpoint.txt
- runs git fetch, git reset --hard, git clean -fd
- auto runs test mode after rollback
- output: rollback <hash>

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

## checkpoint and rollback

### checkpoint naming convention

use prefix CHECKPOINT_S4_ for sprint 4 checkpoints

examples:
- CHECKPOINT_S4_before_big_change
- CHECKPOINT_S4_api_integration
- CHECKPOINT_S4_rollback_ready

### last_checkpoint.txt

- location: logs/last_checkpoint.txt
- contains the commit hash of the last checkpoint
- created automatically by checkpoint mode
- used by rollback mode when -TargetCommit is not specified
- ignored by git (.gitignore)

### example workflow

```powershell
# 1. create checkpoint before risky change
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName S4_before_big_change

# 2. make changes and test
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test

# 3a. if test passed, continue working
# 3b. if test failed, rollback to last checkpoint
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback

# or rollback to specific commit
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback -TargetCommit abc1234
```

### rollback auto test

rollback mode runs test automatically after rollback completes:
- uses -Clean flag to ensure clean state
- uses same -SummaryFile if specified
- exits with code 1 if test fails

### rollback verification procedure

1. create checkpoint
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName S4_before_verify
```

2. intentionally cause failure (example: add deny pattern)
```json
"deny_if_contains": [
  "Remove-Item",
  "Set-Content"
]
```

3. run test (should fail)
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test
```

4. rollback to checkpoint
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
```

5. test runs automatically after rollback and should pass

## S-4 completion criteria

- run/test/cleanrun/checkpoint/rollback modes work correctly
- deny/fatal_error/stopped states are distinguishable
- SummaryFile outputs both JSON and TXT formats

## representative commands

```powershell
# run mode
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run

# test mode
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test

# cleanrun mode
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun

# checkpoint mode
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName S4_example

# rollback mode
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
```

## S-4 completion checklist

- [x] run/test/cleanrun modes pass
- [x] deny/fatal_error/stopped states are distinguishable
- [x] checkpoint/rollback modes pass
- [x] SummaryFile outputs JSON and TXT

## S-5 experimental phase

S-5 is an experimental phase for testing new features.

### experimental mode

- config_v0_3.json s5_settings.enabled=true enables experimental mode
- is_experimental flag is saved in step_log
- phase_summary.json includes current_phase=S-5 and previous_phase=S-4
- cc_run.ps1 displays "(experimental)" when phase is S-5
- test mode shows warning when is_experimental=true

### caution

- experimental features may be unstable
- results may differ from stable phases
- use checkpoint before testing experimental features
- rollback if unexpected behavior occurs

### recommended workflow for S-5 experimental

1. **checkpoint before changes**: always create a checkpoint before running experimental features
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode checkpoint -CheckpointName S5_before_experiment
   ```

2. **run experimental**: execute with cleanrun to ensure clean state
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun
   ```

3. **verify results**: check test mode for experimental warnings
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test
   ```

4. **rollback if needed**: if unexpected behavior occurs, rollback immediately
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
   ```

### s5_settings configuration

```json
"s5_settings": {
  "enabled": true,
  "description": "S-5 experimental features",
  "experimental_warning": true,
  "job_loop": {
    "enabled": true,
    "max_jobs": 3,
    "job_name": "sample"
  }
}
```

## S-5 job_loop

job_loop is an experimental feature for running multiple jobs sequentially.

### job_loop configuration

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

- enabled: enable job_loop mode
- max_jobs: maximum number of jobs to run
- job_name: name prefix for job identification

### behavior

- each run executes 1 job (1 step execution cycle)
- job_index starts at 1 and increments after each done
- job_index is saved in phase_state.json for continuation
- when job_index > max_jobs, phase becomes job_loop_complete

### job_loop_complete

- phase_state.current_phase = "job_loop_complete"
- not an error state, treated as passed in test mode
- end_reason shows max_jobs reached message

### step_log fields

- job_loop_enabled: true/false
- job_name: job name from config
- job_index: current job index (1-based)

### phase_summary fields

- job_loop_enabled: true/false
- job_loop: object with enabled, max_jobs, job_name, current_job_index, completed

### example workflow

```powershell
# 1. first job run
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun
# job_index=1, after done job_index becomes 2

# 2. second job run
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
# job_index=2, after done job_index becomes 3

# 3. third job run
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
# job_index=3, after done job_index becomes 4

# 4. fourth run - job_loop_complete
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
# job_index=4 > max_jobs=3, ends with job_loop_complete
```

### end_reason values for job_loop

- done (job X/Y completed): normal job completion
- job_loop_complete: max_jobs(...) reached
- deny: command was denied
- fatal_error: API or system error

### S-5 completion checklist

- [ ] experimental mode displays correctly
- [ ] is_experimental flag saved in step_log
- [ ] phase_summary includes previous_phase=S-4
- [ ] test mode warning displayed
- [ ] job_loop mode works correctly
- [ ] job_loop_complete handled properly
