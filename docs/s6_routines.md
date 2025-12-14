# S-6 安定運用ルーチン

**S-6 stable 定常運用マニュアル（最終版）**

**本ドキュメントは最終版です。ルーチンの追加・変更は禁止されています。**

本ドキュメントは S-6 stable の定常運用ルーチンを定義します。
「誰がやっても同じ運用」を実現するため、判断基準と手順を一義的に固定します。

---

## 目次

1. [日次ルーチン](#日次ルーチン)
2. [週次ルーチン](#週次ルーチン)
3. [月次ルーチン](#月次ルーチン)
4. [障害対応ルーチン](#障害対応ルーチン)

---

# 日次ルーチン

## 実施条件

**いつ実施するか**: TOS を使用して業務を実行する日の開始時

実施が必要な条件:
- TOS を使用する予定がある
- 前回の実行から 24 時間以上経過している
- 設定変更や環境変更を行った直後

## 事前チェック（10項目以内）

日次実行前に以下を確認する（すべて Yes であること）:

| # | チェック項目 | 確認方法 |
|---|-------------|---------|
| 1 | 作業ディレクトリが正しい | `C:\Users\takag\00_dev\tos` |
| 2 | API キーが設定されている | 環境変数 OPENAI_API_KEY / ANTHROPIC_API_KEY |
| 3 | git status がクリーン | 未コミット変更なし |
| 4 | checkpoint が作成済み | 重要な変更前は必須 |
| 5 | config_v0_3.json が正常 | JSON 構文エラーなし |
| 6 | logs/ に空き容量がある | ディスク容量 80% 未満 |
| 7 | 前回の実行が正常終了 | done または job_loop_complete |
| 8 | 他の人が実行中でない | 排他確認 |

## 標準コマンド列（PowerShell）

```powershell
# 1. 作業ディレクトリに移動
Set-Location 'C:\Users\takag\00_dev\tos'

# 2. git status 確認
git status

# 3. checkpoint 作成（日付付き）
powershell -ExecutionPolicy Bypass -File '.\tools\checkpoint.ps1' -Name "daily_$(Get-Date -Format 'yyyyMMdd')"

# 4. test モードで状態確認
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode test

# 5. 問題なければ run モードで実行
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode run
```

### ワンライナー版（PowerShell から実行）

```powershell
# 日次実行（checkpoint + test + run）
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; .\tools\checkpoint.ps1 -Name 'daily_$(Get-Date -Format yyyyMMdd)'; .\tools\cc_run.ps1 -Mode test; if ($LASTEXITCODE -eq 0) { .\tools\cc_run.ps1 -Mode run }"
```

## 成功判定

以下のすべてを満たせば成功:

| # | 判定項目 | 判定基準 |
|---|---------|---------|
| 1 | test モード成功 | exit code = 0 |
| 2 | phase が正常 | done または job_loop_complete |
| 3 | エラーログなし | fatal_error / deny / stopped がない |
| 4 | サマリファイル生成 | logs/last_run_summary.json が存在 |

## 失敗時分岐

| 症状 | 対応 |
|------|------|
| test モード失敗 | run を実行しない → 原因調査 |
| phase が deny | config_v0_3.json の deny_patterns を確認 |
| phase が fatal_error | API キー・ネットワークを確認 → rollback 検討 |
| 予期しない変更 | `git checkout -- <file>` で元に戻す |
| 復旧不可能 | rollback を実行 → 障害報告 |

### rollback コマンド

```powershell
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode rollback
```

## 日次ログ提出セット（最小）

障害報告時に必須のファイル:

| ファイル | パス |
|---------|------|
| last_run_summary.json | logs/last_run_summary.json |
| last_run_summary.txt | logs/last_run_summary.txt |
| 直近の step_*.json | logs/steps/step_*.json |

---

# 週次ルーチン

## 目的

週次ルーチンの目的:
1. **ログの肥大化防止**: logs/ ディレクトリの容量監視
2. **状態の健全性確認**: 蓄積された問題の早期発見
3. **運用記録の蓄積**: 週次レポートによる履歴管理

## 実施条件

**いつ実施するか**: 毎週月曜日の業務開始時（推奨）

## チェック項目（10項目以内）

| # | チェック項目 | 確認方法 | 合格基準 |
|---|-------------|---------|---------|
| 1 | logs/ のサイズ | `(Get-ChildItem logs -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB` | 100MB 未満 |
| 2 | step_*.json の件数 | `(Get-ChildItem logs/steps).Count` | 100 件未満 |
| 3 | workspace/artifacts の状態 | `Get-ChildItem workspace/artifacts` | 必要ファイルのみ |
| 4 | git log の異常 | `git log --oneline -10` | CHECKPOINT が週1回以上 |
| 5 | phase_summary.json の確認 | `Get-Content workspace/artifacts/phase_summary.json` | エラーカウント = 0 |
| 6 | config_v0_3.json の変更 | `git diff HEAD~7 config_v0_3.json` | 予期しない変更なし |
| 7 | docs/ の更新有無 | `git log --oneline -10 -- docs/` | 問題なし |
| 8 | 未解決の障害 | 障害報告の確認 | 未解決なし |

## logs/ の肥大化確認手順

```powershell
# logs/ の合計サイズ（MB）
Set-Location 'C:\Users\takag\00_dev\tos'
$size = (Get-ChildItem logs -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "logs/ size: $([math]::Round($size, 2)) MB"

# step_*.json の件数
$count = (Get-ChildItem logs/steps -Filter "step_*.json").Count
Write-Host "step_*.json count: $count"

# 判定
if ($size -gt 100) { Write-Host "WARNING: logs/ が 100MB を超えています" }
if ($count -gt 100) { Write-Host "WARNING: step_*.json が 100 件を超えています" }
```

## workspace/artifacts の状態確認手順

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'
Get-ChildItem workspace/artifacts | Format-Table Name, LastWriteTime, Length
```

期待されるファイル:
- phase_state.json
- phase_summary.json
- job_input.json（存在する場合）
- job_result.json（job_loop_complete 後）
- job_input.example.json

## git log の確認手順

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'
git log --oneline -10
```

確認ポイント:
- CHECKPOINT コミットが週1回以上あるか
- 予期しないコミットがないか
- コミットメッセージが適切か

## 成功判定

以下のすべてを満たせば成功:

| # | 判定項目 | 判定基準 |
|---|---------|---------|
| 1 | logs/ サイズ | 100MB 未満 |
| 2 | step_*.json 件数 | 100 件未満 |
| 3 | 異常ログなし | fatal_error / deny の蓄積なし |
| 4 | checkpoint 存在 | 週1回以上作成されている |

## 失敗時分岐

| 症状 | 対応 |
|------|------|
| logs/ が 100MB 超 | 30日以上前のログを手動削除（月次で対応） |
| step_*.json が 100 件超 | 古いログを手動削除（月次で対応） |
| fatal_error の蓄積 | 原因調査 → 障害報告 |
| checkpoint なし | 即座に checkpoint を作成 |

## 週次報告テンプレ（短文）

```
## 週次運用報告 YYYY-MM-DD

- logs/ サイズ: XX MB
- step_*.json 件数: XX 件
- 週間実行回数: XX 回
- 障害発生: なし / あり（件数）
- 特記事項: なし / あり（内容）
```

## 実施記録の残し方

週次報告は以下のいずれかに記録:
1. チーム共有ドキュメント（推奨）
2. Slack/Teams 等のチャネル
3. ローカルファイル（logs/weekly_reports/）

---

# 月次ルーチン

## 目的

月次ルーチンの目的:
1. **保全**: ログ・成果物の棚卸しと整理
2. **監査**: ドキュメント・設定の整合性確認
3. **棚卸**: 不要ファイルの削除、構成の最適化

## 実施条件

**いつ実施するか**: 毎月1日の業務開始時（推奨）

## 構成一覧の確認（docs/index.md の整合）

docs/index.md に記載されているすべてのドキュメントが存在することを確認:

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'
# 主要ドキュメントの存在確認
$docs = @(
    'docs/s6_stable.md',
    'docs/s6_operations.md',
    'docs/s6_governance.md',
    'docs/s6_environment.md',
    'docs/s6_completion.md',
    'docs/s6_routines.md',
    'docs/s7_proposal.md',
    'docs/runbook.md',
    'docs/glossary.md',
    'docs/failure_report_template.md',
    'docs/release_notes.md',
    'docs/index.md'
)
$docs | ForEach-Object {
    $exists = Test-Path $_
    Write-Host "$_`: $exists"
}
```

## .gitattributes/.editorconfig の方針確認手順

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'

# .gitattributes の確認
Write-Host "=== .gitattributes ==="
Get-Content .gitattributes

# .editorconfig の確認
Write-Host "`n=== .editorconfig ==="
Get-Content .editorconfig
```

確認ポイント:
- `* text=auto` が設定されているか
- `*.md text eol=lf` が設定されているか
- `end_of_line = lf` が設定されているか

## core.autocrlf の推奨方針（再掲）

```powershell
# 現在の設定確認
git config core.autocrlf

# 推奨設定（未設定の場合）
git config core.autocrlf false
```

**推奨値**: `false` または `input`

## 主要ドキュメントのリンク切れ確認手順

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'

# README.md のリンク抽出と存在確認
$readme = Get-Content README.md -Raw
$links = [regex]::Matches($readme, '\[.*?\]\((docs/[^\)]+)\)') | ForEach-Object { $_.Groups[1].Value }
$links | ForEach-Object {
    $exists = Test-Path $_
    if (-not $exists) { Write-Host "BROKEN LINK: $_" }
}
```

## 成功判定

以下のすべてを満たせば成功:

| # | 判定項目 | 判定基準 |
|---|---------|---------|
| 1 | 全ドキュメント存在 | docs/index.md 記載のファイルがすべて存在 |
| 2 | リンク切れなし | README.md からのリンクがすべて有効 |
| 3 | 改行設定正常 | .gitattributes/.editorconfig が正しい |
| 4 | logs/ 整理完了 | 30日以上前のログが削除されている |

## 失敗時分岐

| 症状 | 対応 |
|------|------|
| ドキュメント欠損 | 欠損ファイルを復元または docs/index.md を修正 |
| リンク切れ | リンク先を修正または削除 |
| 改行設定異常 | .gitattributes/.editorconfig を修正 |
| ログ肥大化 | 30日以上前のログを手動削除 |

### ログ手動削除コマンド

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'

# 30日以上前の step_*.json を削除（確認後に実行）
$threshold = (Get-Date).AddDays(-30)
Get-ChildItem logs/steps -Filter "step_*.json" | Where-Object { $_.LastWriteTime -lt $threshold } | Remove-Item -WhatIf

# 実際に削除する場合は -WhatIf を削除
```

## 月次報告テンプレ（短文）

```
## 月次運用報告 YYYY-MM

- ドキュメント整合性: OK / NG（詳細）
- リンク切れ: なし / あり（件数）
- logs/ 整理: 完了 / 未完了
- 削除ファイル数: XX 件
- 障害発生（月間）: なし / あり（件数）
- 特記事項: なし / あり（内容）
```

## 実施記録の残し方

月次報告は以下に記録:
1. チーム共有ドキュメント（推奨）
2. Slack/Teams 等のチャネル
3. git commit メッセージ（月次整理コミット）

---

# 障害対応ルーチン

## 障害の定義

以下のいずれかが発生した場合を「障害」とする:

| # | 障害条件 | 説明 |
|---|---------|------|
| 1 | phase が fatal_error | API 呼び出しまたはシステムエラー |
| 2 | phase が deny で復旧不可 | 設定修正でも解消しない |
| 3 | phase が stopped | 実行が中断された |
| 4 | test モードが失敗 | exit code ≠ 0 |
| 5 | 予期しないデータ破損 | phase_state.json / step_*.json の破損 |
| 6 | 再現性のあるエラー | 同じ操作で同じエラーが発生 |

## 一次対応（30分以内）

障害検知後、30分以内に以下を実施:

| # | 対応項目 | 実施内容 |
|---|---------|---------|
| 1 | 状況確認 | `git status` / `test モード` で現状把握 |
| 2 | ログ収集 | last_run_summary.json/txt, step_*.json を保存 |
| 3 | 影響範囲確認 | 他の処理への影響を確認 |
| 4 | 一次報告 | 障害発生を関係者に通知 |
| 5 | 追加実行の停止 | 原因判明まで run を実行しない |

### 一次対応コマンド

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'

# 1. 状況確認
git status
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode test

# 2. ログ収集
Get-Content logs/last_run_summary.json
Get-Content logs/last_run_summary.txt
Get-ChildItem logs/steps | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { Get-Content $_.FullName }

# 3. commit hash 取得
git rev-parse HEAD
```

## 二次対応（原因調査）

一次対応後、原因を特定するために以下を実施:

| # | 調査項目 | 調査方法 |
|---|---------|---------|
| 1 | エラーメッセージ分析 | step_*.json の error / done_reason を確認 |
| 2 | 直前の変更確認 | `git log --oneline -5` / `git diff HEAD~1` |
| 3 | config 確認 | config_v0_3.json の設定値を確認 |
| 4 | 環境確認 | API キー、ネットワーク、ディスク容量を確認 |
| 5 | 再現確認 | 同じ操作でエラーが再現するか確認 |

## rollback を実行すべき条件

以下のいずれかに該当する場合は **即座に rollback を実行する**:

1. **phase_state.json が破損している**
2. **config_v0_3.json が破損している**
3. **原因不明のエラーが継続している**
4. **設定変更後に正常動作しない**
5. **復旧に30分以上かかる見込み**

### rollback コマンド

```powershell
Set-Location 'C:\Users\takag\00_dev\tos'
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode rollback
```

## 影響範囲報告に必須の項目

障害報告には以下を必ず含める:

| # | 必須項目 | 取得方法 |
|---|---------|---------|
| 1 | 発生日時 | 障害発生時刻 |
| 2 | commit hash | `git rev-parse HEAD` |
| 3 | mode | run / test / cleanrun 等 |
| 4 | phase | done / fatal_error / deny 等 |
| 5 | エラーメッセージ | step_*.json の error フィールド |
| 6 | 影響範囲 | 影響を受けた処理・データ |

## 障害報告テンプレへの導線

詳細な障害報告は **[障害報告テンプレート](failure_report_template.md)** を使用してください。

エスカレーション手順・連絡先は **[エスカレーション](ops_escalation.md)** を参照してください。

テンプレートには以下が含まれています:
- 基本情報フォーマット
- ログ取得コマンド
- 必須項目チェックリスト

## 障害時に「やってはいけないこと」

| # | 禁止事項 | 理由 |
|---|---------|------|
| 1 | 原因不明のまま run を再実行 | 問題が拡大する可能性 |
| 2 | ログを削除する | 原因調査ができなくなる |
| 3 | config を無闘派に変更する | 問題が複雑化する |
| 4 | 報告せずに放置する | 問題が潜在化する |
| 5 | 履歴（git log）を改変する | 追跡不可能になる |

## 再発防止の書き方テンプレ

```
## 再発防止策

### 直接原因
（技術的な原因を記載）

### 根本原因
（なぜその状況が発生したかを記載）

### 再発防止策
1. （短期対策）
2. （中長期対策）

### 確認方法
（再発防止策が機能しているかの確認方法）

### 対応完了日
YYYY-MM-DD
```

## 障害対応完了の判定基準

以下のすべてを満たせば障害対応完了:

| # | 判定項目 | 判定基準 |
|---|---------|---------|
| 1 | 正常動作回復 | test モードが成功（exit code = 0） |
| 2 | 原因特定 | 障害原因が特定されている |
| 3 | 再発防止策策定 | 再発防止策が文書化されている |
| 4 | 報告完了 | 障害報告が関係者に共有されている |
| 5 | 通常運用復帰 | 日次ルーチンが正常に実行可能 |

---

# 正史コンテキスト v1.0 との整合

本ドキュメントは正史コンテキスト v1.0 に準拠しています。

- S-6 stable の定常運用ルーチンを定義
- S-7 は「不要」と確定しているため、拡張は行わない
- S-5 は履歴フェーズであり、参照のみ許可

---

# 更新履歴

- 2025-12-14: 初版作成（S-6 安定運用ルーチン確立）
- 2025-12-14: **最終版確定・封印**（これ以上のルーチン追加なし）
