# TOS v0.3 用語集（Glossary）

**S-6 stable 用語集**

本ドキュメントは TOS v0.3 で使用される用語を定義します。

---

## フェーズ関連

### S-4 / S-5 / S-6

TOS v0.3 の開発フェーズを示す識別子。

| フェーズ | 状態 | 説明 |
|---------|------|------|
| S-4 | 履歴 | 基本機能実装フェーズ |
| S-5 | 履歴（凍結） | experimental フェーズ |
| S-6 | 現行（完成） | stable フェーズ |
| S-7 | 未定義 | 必要時に検討 |

**表記ルール**: ハイフン付き `S-6` を標準とする（`S6` は非推奨）。

### experimental（実験的）

S-5 フェーズの特性を示す。機能が不安定である可能性がある。

### stable（安定）

S-6 フェーズの特性を示す。機能が安定しており、本番運用に適している。

### closeout（クローズアウト）

フェーズを正式に終了し、履歴フェーズとして凍結すること。

**表記ルール**: 小文字 `closeout` を標準とする（`Closeout` は見出しのみ許可）。

---

## job_loop 関連

### job_loop

複数ジョブを順次実行する機能。S-5 で実装された。

### job_index

現在実行中のジョブ番号（1-based）。実行ごとにインクリメントされる。

### max_jobs

実行するジョブの最大数。job_index が max_jobs を超えると job_loop_complete となる。

### job_loop_complete

job_loop が正常に完了した状態。phase として記録される。エラーではない。

### job_name

ジョブの識別名。config で設定、job_input.json で上書き可能。

---

## ペイロード関連

### job_input.json

外部からオーケストレーターに渡す入力ペイロード。

- パス: `workspace/artifacts/job_input.json`
- 形式: JSON
- 必須: false

### job_result.json

job_loop_complete 時に出力される結果ファイル。

- パス: `workspace/artifacts/job_result.json`
- 形式: JSON
- 出力条件: job_loop_complete 時のみ

### job_payload

job_input.json の内容。step_log に保存される（最大 2000 文字）。

---

## サマリー関連

### SummaryFile

実行結果のサマリーを出力するファイル群の総称。

- `last_run_summary.json`: JSON 形式
- `last_run_summary.txt`: 1行テキスト形式

### phase_summary.json

フェーズ全体の状態を記録するファイル。

- パス: `workspace/artifacts/phase_summary.json`
- 内容: phase, step_count, job_loop 情報など

### last_run_summary

最新の実行結果を記録するファイル。

- JSON 版: `logs/last_run_summary.json`
- TXT 版: `logs/last_run_summary.txt`

---

## 状態関連

### phase

現在の実行状態を示す識別子。

| phase | 説明 |
|-------|------|
| done | 正常完了 |
| job_loop_complete | job_loop 正常完了 |
| deny | コマンド拒否 |
| fatal_error | 致命的エラー |
| stopped | 実行停止 |

### end_reason

実行終了の理由を示す文字列。

例:
- `done (job X/Y completed)`
- `job_loop_complete: max_jobs(3) reached`
- `deny: <reason>`
- `fatal_error: <error>`

---

## ツール関連

### cc_run.ps1

TOS オーケストレーターのランチャースクリプト（PowerShell）。

モード:
- `run`: 通常実行
- `test`: 検証実行
- `cleanrun`: クリーン実行
- `checkpoint`: チェックポイント作成
- `rollback`: ロールバック

### checkpoint

git コミットとして保存される復元ポイント。

- 作成: `checkpoint.ps1 -Name <name>`
- 記録: `logs/last_checkpoint.txt`

### rollback

checkpoint に戻す操作。

- 実行: `cc_run.ps1 -Mode rollback`
- 動作: `git reset --hard` + `git clean -fd`

---

## 運用関連

### 正史コンテキスト（Canonical Context）

TOS の開発・運用における唯一の正しい文脈を定義するもの。

- バージョン: v1.0
- 情報源: 本リポジトリのドキュメント

### 正順

正しい実行順序: `cleanrun → test → run`

### 禁止順序

禁止されている実行順序: `run → test → cleanrun`（cleanrun なしで run を開始してはいけない）

---

## 環境関連

### PowerShell

Windows での標準実行環境。TOS v0.3 は PowerShell を標準とする。

### LF / CRLF

改行コード。

- LF: Unix 標準（\n）
- CRLF: Windows 標準（\r\n）

TOS v0.3 ではリポジトリ内は LF を標準とする（.gitattributes で管理）。

---

## 正史コンテキスト v1.0 との整合

本用語集は正史コンテキスト v1.0 に準拠しています。

用語の追加・変更は S-6 stable の運用ルール内で行われます。
