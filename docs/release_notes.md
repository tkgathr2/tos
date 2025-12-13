# TOS v0.3 Release Notes

## S-4 Changes

- Added run/test/cleanrun/checkpoint/rollback modes to cc_run.ps1
- Implemented deny/fatal_error/stopped state tracking
- Added execution_policy with deny_if_contains and deny_patterns
- SummaryFile outputs both JSON and TXT formats
- Added stop_on_deny configuration option
- Implemented checkpoint and rollback tools for version control
- Added auto test after rollback with -Clean flag
- Enhanced phase_summary with stopped_steps and end_reason

## Key Commits

- 8d69abd CHECKPOINT S4 before finalize
- 6d1404c TOS v0.3 S-4 rollback verify
- 977d1c0 CHECKPOINT S4 rollback test
