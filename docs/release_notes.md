# TOS v0.3 Release Notes

## S-5 Changes

- Started S-5 experimental phase
- Added s5_settings configuration section
- Added is_experimental flag to step_log
- Added s5_flag to step_log for S-5 identification
- Added previous_phase=S-4 to phase_summary.json and phase_state.json
- Added experimental=true to phase_summary.json
- cc_run.ps1 displays "S-5 experimental" for S-5 phase
- test mode shows "experimental mode active" when in S-5 phase
- test mode shows warning when is_experimental=true
- Updated runbook.md with S-5 section and recommended workflow
- Added experimental_warning setting to s5_settings

### S-5 job_loop

- Added job_loop configuration to s5_settings (enabled, max_jobs, job_name)
- Added job_loop_enabled, job_name, job_index to step_log
- job_index is saved to and restored from phase_state.json
- job_index increments after each done, enabling multi-job sequences
- job_loop_complete phase when job_index > max_jobs
- cc_run.ps1 displays job_loop_complete status (not an error)
- test mode treats job_loop_complete as passed
- phase_summary includes job_loop_enabled and job_loop object
- Updated runbook.md with job_loop documentation

### S-5 job payload

- Added job_input configuration to s5_settings.job_loop
- job_input.json allows external payload input (workspace/artifacts/job_input.json)
- job_payload is passed to draft_prompt as {job_payload_json} template variable
- job_name in job_input.json overrides config job_name
- job_payload is saved in step_log (sanitized, max 2000 chars)
- Added job_result configuration to s5_settings.job_loop
- job_result.json is output on job_loop_complete (workspace/artifacts/job_result.json)
- cc_run.ps1 cleanrun deletes job_result.json
- cc_run.ps1 test/run mode displays job_result.json exists status
- Updated runbook.md with job payload documentation

### S-5 SummaryFile job_result

- SummaryFile JSON includes job_result_exists (true/false)
- SummaryFile JSON includes job_result_path when job_result.json exists
- SummaryFile TXT includes job_result=exists|none
- SummaryFile TXT includes job_result_path when job_result.json exists
- step_log includes job_result_written (true/false)
- job_result_written=true only for job_loop_complete phase
- phase_summary includes job_result_path when job_result.json is output
- test mode passes when job_loop_complete + job_result.json exists

### S-5 指示書048 Summary/JobLoop/Payload完成度向上

- SummaryFile JSON/TXT に job_loop オブジェクト追加 (enabled, max_jobs, job_name, current_job_index, completed)
- SummaryFile JSON/TXT に job_payload_present, job_payload_size 追加
- SummaryFile JSON/TXT に job_result_written 追加
- SummaryFile TXT に end_reason 追加
- phase_summary に job_payload_present, job_result_written, job_result_path_posix 追加
- step_log に job_payload_present, job_payload_size, job_result_path 追加
- run/cleanrun/test サマリー表示に job_loop info 追加
- run/cleanrun で job_result_path_posix 表示
- test mode 警告追加: job_loop enabled but not completed
- test mode 警告追加: job_payload_present=false
- test mode 警告追加: job_index > max_jobs
- test mode 警告追加: job_result_written=false

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
