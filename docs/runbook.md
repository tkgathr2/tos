# TOS v0.3 Runbook

**本ドキュメントは運用者向けです。** 日常的に TOS を使用する人を対象としています。

初見の方は [README.md](../README.md) を先にお読みください。

---

## S-6 Stable 運用ステータス

**S-6 stable フェーズは 2025-12-14 に開始しました。現行の運用フェーズです。**

### S-6 運用開始条件

S-6 stable 運用を開始するには、以下の条件を満たす必要があります：

1. S-5 closeout が完了していること
2. 正史コンテキスト v1.0 に準拠していること
3. 本 runbook の運用ルールを理解していること
4. API キー（OPENAI_API_KEY / ANTHROPIC_API_KEY）が設定されていること
5. checkpoint を作成してから実行を開始すること

### S-6 と S-5 の違い

| 項目 | S-5 (experimental) | S-6 (stable) |
|------|-------------------|--------------|
| ステータス | 履歴（凍結） | 現行（運用中） |
| 目的 | 機能開発・検証 | 安定運用 |
| 変更 | 禁止 | 運用ルール内で許可 |
| 新機能追加 | なし | なし |
| バグ修正 | 禁止 | 承認後に許可 |
| ドキュメント修正 | 禁止 | 許可 |

---

## S-5 運用ステータス（履歴）

**S-5 は運用対象外です。S-5 は履歴フェーズとして凍結されました。**

### S-5 変更禁止

S-5 フェーズに対するすべての変更は禁止されています。以下を含みます：

- 新機能追加
- 仕様変更
- 設定スキーマ変更
- 破壊的変更
- 暗黙仕様の導入

### rollback 専用扱い

S-5 の実行手順は **rollback による復旧確認目的でのみ** 使用されます。

- 新規運用での S-5 実行は禁止
- 問題発生時の切り戻し確認のみ許可
- 切り戻し後は速やかに S-6 運用に復帰

詳細は [S-5 Closeout](s5_closeout.md) を参照してください。

---

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

test mode warnings (do not affect exit code):
- WARNING: job_loop enabled but not completed - when job_loop.enabled=true and completed=false
- WARNING: job_payload_present=false - when job_loop enabled but no job_input.json
- WARNING: job_index (X) > max_jobs (Y) - when job_index exceeds max_jobs
- WARNING: job_result_written=false - when job_loop completed but no job_result.json

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
- job_result_exists (true/false)
- job_result_written (true/false)
- job_result_path (only if job_result_exists=true)
- job_payload_present (true/false)
- job_payload_size (bytes)
- job_loop (object with enabled, max_jobs, job_name, current_job_index, completed)
- end_reason

TXT content
- 1 line format
- phase=done step=1 done=True latest_step=step_001.json step_count=1 phase_summary=exists job_result=none
- when job_result.json exists: job_result=exists job_result_path=<path>
- job_loop=enabled|disabled job_name=sample job_index=1 max_jobs=3
- job_payload=present|none job_result_written=true|false job_payload_size=123

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

---

## 参考情報: S-4 完了基準

> 以下は S-4 フェーズで達成した基準です。S-5 以降も維持されています。

- run/test/cleanrun/checkpoint/rollback modes work correctly
- deny/fatal_error/stopped states are distinguishable
- SummaryFile outputs both JSON and TXT formats

### S-4 completion checklist

- [x] run/test/cleanrun modes pass
- [x] deny/fatal_error/stopped states are distinguishable
- [x] checkpoint/rollback modes pass
- [x] SummaryFile outputs JSON and TXT

---

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

## S-5 job payload

job_input.json allows external input to be passed to the orchestrator.
job_result.json is output when job_loop_complete.

### job_input configuration

```json
"s5_settings": {
  "job_loop": {
    "enabled": true,
    "max_jobs": 3,
    "job_name": "sample",
    "job_input": {
      "path": "workspace/artifacts/job_input.json",
      "required": false
    },
    "job_result": {
      "path": "workspace/artifacts/job_result.json"
    }
  }
}
```

### job_input.json specification

- path: workspace/artifacts/job_input.json (configurable)
- required: false (if file not found, execution continues without payload)
- format: JSON object

example:
```json
{
  "job_name": "custom_job",
  "target": "some_target",
  "params": {
    "key1": "value1"
  }
}
```

- job_name: overrides config job_name if specified
- other fields: passed to draft_prompt as {job_payload_json}

### job_result.json specification

- path: workspace/artifacts/job_result.json (configurable)
- output: created when job_loop_complete
- format: JSON object

example:
```json
{
  "job_name": "sample",
  "max_jobs": 3,
  "jobs_executed": 3,
  "end_reason": "job_loop_complete: max_jobs(3)に到達",
  "last_phase": "job_loop_complete",
  "last_step": 1,
  "timestamp": "2025-12-13T23:19:06.517283"
}
```

fields:
- job_name: job name (from config or job_input override)
- max_jobs: configured max_jobs value
- jobs_executed: actual number of jobs executed (max_jobs)
- end_reason: reason for job_loop completion
- last_phase: phase when job_loop ended
- last_step: step number when job_loop ended
- timestamp: ISO format timestamp

### step_log job_payload field

- job_payload is saved in step_log (sanitized, max 2000 chars)
- truncated payloads end with "...(truncated)"

### cc_run.ps1 job_result handling

- cleanrun mode: deletes job_result.json
- test mode: checks job_result.json exists when job_loop_complete
- run mode: displays job_result.json exists status when job_loop_complete

### S-5 completion checklist

- [ ] experimental mode displays correctly
- [ ] is_experimental flag saved in step_log
- [ ] phase_summary includes previous_phase=S-4
- [ ] test mode warning displayed
- [ ] job_loop mode works correctly
- [ ] job_loop_complete handled properly

---

## S-5 Closeout チェックリスト

S-5 フェーズのクローズアウトにあたり、以下を確認してください：

### 必須確認項目

- [ ] config_v0_3.json の s5_settings が正しく設定されている
- [ ] orchestrator_v0_3.py が正常に動作する
- [ ] checkpoint/rollback が正常に動作する
- [ ] job_loop が正常に動作する（job_loop_complete まで）
- [ ] job_input.json → job_result.json の連携が動作する
- [ ] phase_summary.json が正しく生成される
- [ ] last_run_summary.json/txt が正しく生成される

### ドキュメント確認項目

- [ ] README.md に S-5 の目的が明記されている
- [ ] README.md に「S-6 は未定義」が明記されている
- [ ] runbook.md に S-5 closeout チェックリストが存在する
- [ ] runbook.md に「S-5 でやってはいけないこと」が存在する
- [ ] docs に experimental フラグの定義が存在する

---

## S-5 でやってはいけないこと

以下の変更は S-5 フェーズでは **禁止** されています：

### 絶対禁止

1. **新機能の追加**
   - 既存機能の拡張も含む
   - 新しい設定項目の追加
   - 新しいモードの追加

2. **仕様変更**
   - 入出力フォーマットの変更
   - 処理ロジックの変更
   - エラーハンドリングの変更

3. **依存関係の変更**
   - 新しいライブラリの追加
   - 既存ライブラリのバージョン変更

4. **設定フォーマットの変更**
   - config_v0_3.json のスキーマ変更
   - 既存設定項目の削除

5. **破壊的な変更**
   - 既存データの削除
   - 後方互換性を壊す変更

### 許可される変更

- ドキュメントの修正・追加
- バグ修正（動作に影響を与えない範囲）
- ログメッセージの修正
- コメントの追加・修正
- テストの追加

---

## S-5 はこれ以上育てない

**S-5 はこれ以上育てません。**

- 新機能追加なし
- 仕様変更なし
- 大規模リファクタリングなし

変更が必要な場合は S-6 を検討してください。S-6 は別ドキュメントで検討します。

---

## 正史コンテキスト v1.0

**本 Runbook は正史コンテキスト v1.0 に準拠しています。**

### 正史が前提である理由

TOS v0.3 は experimental フェーズの集大成として S-5 で凍結されました。以下の理由により、正史コンテキストが前提となります：

1. **再現性の保証**
   - 正史に従うことで、誰が実行しても同じ結果を得られる
   - ドキュメントと実装の乖離を防ぐ

2. **品質の維持**
   - 検証済みの動作のみを使用する
   - 未検証の拡張による不具合を防ぐ

3. **サポート範囲の明確化**
   - 正史に沿った使用のみサポート対象
   - 逸脱した使用は自己責任

### 正史に反する運用の禁止

以下の運用は **禁止** されています：

1. **ドキュメントに記載のない設定の使用**
   - config_v0_3.json に未定義のキーを追加しない
   - 未定義の環境変数に依存しない

2. **独自拡張の適用**
   - orchestrator_v0_3.py の独自改変
   - cc_run.ps1 の独自改変
   - 未定義のモードの追加

3. **正史外のワークフローの実行**
   - ドキュメントに記載のない実行順序
   - 未定義の入出力形式の使用

4. **S-5 で定義されていない機能の使用**
   - S-6 以降の機能（未定義）
   - 実験的に追加された未ドキュメント機能

### 逸脱が発生した場合

正史から逸脱した運用を行った場合：

1. **即座に rollback を実行**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode rollback
   ```

2. **正史に沿った手順で再実行**

3. **逸脱の原因を特定し、再発防止策を講じる**

詳細は [S-5 Closeout](s5_closeout.md) を参照してください。
