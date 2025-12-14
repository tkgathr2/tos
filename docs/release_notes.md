# TOS v0.3 Release Notes

## S-7 結論確定

**S-7（拡張フェーズ）は 2025-12-14 に「不要」と確定しました。**

### S-7 検討の結論

- **結論**: やらない（S-7 は不要）
- **理由**: 自動リトライは既存、残りは代替可能、安定運用優先
- **再検討時期**: 2025-06-14 以降、またはトリガー条件発生時

詳細は [S-7 検討結果](s7_proposal.md) を参照してください。

---

## S-6 Stable 完成

**S-6 stable フェーズは 2025-12-14 に完成しました。**

S-6 は TOS v0.3 の安定運用フェーズです。S-5 で確立した機能を安定運用し、実運用環境での継続的な利用を可能にします。

### S-6 完成により達成されたこと

- 運用基盤・判断基準の確立
- 拡張可否ルールの明文化
- リスク・限界の明示
- 将来引き継ぎ耐性の確保

### S-6 Changes

- S-6 stable フェーズ開始（2025-12-14）
- S-5 を履歴フェーズとして固定
- 運用ルールの明文化
- docs/s6_stable.md 新設
- docs/s6_operations.md 新設（安定運用ガイド）
- docs/s6_governance.md 新設（ガバナンス・判断基準）
- docs/s6_completion.md 新設（完成宣言）
- docs/s6_environment.md 新設（実行環境標準）
- docs/index.md 新設（ドキュメント索引）
- docs/glossary.md 新設（用語集）
- docs/failure_report_template.md 新設（障害報告テンプレート）
- .gitattributes 新設（改行コード方針）
- .editorconfig 新設（編集環境標準）
- runbook.md に実行前/実行後チェック追加
- runbook.md に PowerShell 実行テンプレート追加
- README.md に改行差分の扱いを追記
- **S-6 stable 完成（2025-12-14）**
- **S-6 stable 実行D 完了（2025-12-14）**

---

## S-5 Closeout 完了（履歴）

**S-5 closeout は 2025-12-14 に完了しました。**

**S-5 は履歴フェーズです。以後の変更は禁止されています。**

### 目的

S-5 closeout は、experimental フェーズを正式に終了し、以下を確定させることを目的としています：

- job_loop 機能の安定動作
- job_input/job_result によるペイロード連携
- checkpoint/rollback による安全な実験環境
- ドキュメントの整備

### 凍結される内容

- 機能仕様（新機能追加なし）
- 設定フォーマット（config_v0_3.json スキーマ）
- 入出力形式（job_input.json, job_result.json）

### 許可される変更

- ドキュメントの修正・追加
- バグ修正（動作に影響を与えない範囲）
- ログメッセージの修正

### 次フェーズ

S-6 stable フェーズが開始・完成しました。詳細は上記を参照してください。

---

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
