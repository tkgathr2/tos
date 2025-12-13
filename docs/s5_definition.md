# S-5 定義書

## 1. experimental フラグの定義

### experimental とは

`experimental` とは、TOS の開発ステータスを示すフラグです。

**experimental = 動作保証あり／仕様保証なし**

これは以下を意味します：

| 項目 | 保証レベル |
|------|-----------|
| 動作 | 保証あり（現在の入力に対して正しく動作する） |
| 仕様 | 保証なし（将来の変更により動作が変わる可能性がある） |
| API | 保証なし（関数シグネチャ等は変更される可能性がある） |
| 設定形式 | 保証なし（config_v0_3.json の形式は変更される可能性がある） |

### S-5 experimental の意味

S-5 は experimental フェーズの最終段階です。

- **S-4**: 基盤機能の安定化
- **S-5**: experimental 機能の最終段階
- **S-6**: 未定義

S-5 以降、experimental フラグは解除されず、そのまま凍結されます。

---

## 2. S-5 が依存しているファイル一覧

### ソースコード

| ファイル名 | 役割 | 必須 |
|-----------|------|------|
| orchestrator_v0_3.py | メインオーケストレーター | 必須 |
| config_v0_3.json | 設定ファイル | 必須 |

### ツール（tools/）

| ファイル名 | 役割 | 必須 |
|-----------|------|------|
| cc_run.ps1 | ランチャースクリプト | 必須 |
| checkpoint.ps1 | チェックポイント作成 | 必須 |

### ワークスペース（workspace/）

| ファイル名 | 役割 | 必須 |
|-----------|------|------|
| workspace/phase_state.json | フェーズ状態 | 自動生成 |
| workspace/artifacts/job_input.json | ジョブ入力 | 任意 |
| workspace/artifacts/job_result.json | ジョブ結果 | 自動生成 |
| workspace/artifacts/phase_summary.json | フェーズサマリー | 自動生成 |

### ログ（logs/）

| ファイル名 | 役割 | 必須 |
|-----------|------|------|
| logs/last_checkpoint.txt | 最終チェックポイント | 自動生成 |
| logs/last_run_summary.json | 実行サマリー（JSON） | 自動生成 |
| logs/last_run_summary.txt | 実行サマリー（TXT） | 自動生成 |

### 外部依存

| パッケージ | 用途 |
|-----------|------|
| openai | OpenAI API |
| anthropic | Anthropic API |

---

## 3. S-5 で生成される成果物一覧

### workspace/artifacts/

| ファイル | 説明 |
|---------|------|
| phase_summary.json | フェーズ終了時のサマリー |
| job_result.json | job_loop_complete 時の結果 |

### logs/

| ファイル | 説明 |
|---------|------|
| last_run_summary.json | 最新実行のサマリー（JSON） |
| last_run_summary.txt | 最新実行のサマリー（1行テキスト） |
| last_checkpoint.txt | 最終チェックポイントのコミットハッシュ |
| step_*.json | 各ステップのログ |

### workspace/

| ファイル | 説明 |
|---------|------|
| phase_state.json | 現在のフェーズ状態 |

---

## 4. S-5 の完了条件

S-5 フェーズの完了条件は以下の通りです：

### 機能完了条件

- [x] orchestrator_v0_3.py が正常に動作する
- [x] run/test/cleanrun モードが動作する
- [x] checkpoint/rollback モードが動作する
- [x] job_loop が正常に動作する
- [x] job_loop_complete まで到達できる
- [x] job_input.json → job_result.json の連携が動作する
- [x] phase_summary.json が正しく生成される

### ドキュメント完了条件

- [x] README.md に S-5 の目的が明記されている
- [x] README.md に「S-6 は未定義」が明記されている
- [x] runbook.md に S-5 closeout チェックリストが存在する
- [x] runbook.md に「S-5 でやってはいけないこと」が存在する
- [x] docs/s5_definition.md が存在する

### 品質完了条件

- [x] 主要な処理パスでエラーが発生しない
- [x] ログが正しく出力される
- [x] 既存データを破壊しない

---

## 5. S-5 と S-6 の境界

### S-5 で行うこと

- ドキュメント整備
- バグ修正（動作に影響を与えない範囲）
- closeout 作業

### S-6 で行うこと（未定義）

S-6 は現時点で未定義です。以下は S-6 が定義された場合の候補です：

- 新機能追加
- 仕様変更
- パフォーマンス改善
- リファクタリング

**注意**: S-6 の検討は別ドキュメントで行います。本ドキュメントは S-5 のみを対象とします。
