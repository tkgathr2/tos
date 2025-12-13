# TOS v0.3 Release Notes

## S-5 Changes

- Started S-5 experimental phase
- Added s5_settings configuration section
- Added is_experimental flag to step_log
- Added previous_phase=S-4 to phase_summary.json
- cc_run.ps1 displays "(experimental)" for S-5 phase
- test mode shows warning when is_experimental=true
- Updated runbook.md with S-5 section

## S-4 Changes

- Added run/test/cleanrun/checkpoint/rollback modes to cc_run.ps1
- Implemented deny/fatal_error/stopped state tracking
- Added execution_policy with deny_if_contains and deny_patterns
- SummaryFile outputs both JSON and TXT formats
- Added stop_on_deny configuration option
- Implemented checkpoint and rollback tools for version control
- Added auto test after rollback with -Clean flag
- Enhanced phase_summary with stopped_steps and end_reason

## S-4 Completion Summary

- deny/fatal_error/stopped: distinct states with proper tracking
- stop_on_deny: configurable behavior on deny (stop or continue)
- checkpoint/rollback: git-based version control integration
- SummaryFile JSON/TXT: dual format output for automation

## Commit History

- 3a37fb1 CHECKPOINT S4 before close
- b93125c TOS v0.3 S-4 finalize
- 8d69abd CHECKPOINT S4 before finalize
- 6d1404c TOS v0.3 S-4 rollback verify
- 977d1c0 CHECKPOINT S4 rollback test
- a1dd3ae TOS v0.3 S-4 rollback tooling FG FM
- d64e560 CHECKPOINT S4 before rollback implement
- 955a93e TOS v0.3 S-4 rollback tooling
- 523b282 CHECKPOINT S4 before rollback tools
- 83ee172 TOS v0.3 S-4 stop and deny policy
