# TOS v0.3 S-6 運用者研修（30分コース）

**S-6 stable 運用者向け最短研修（最終版）**

**本研修は最終版です。追加研修コースの作成は予定されていません。**

---

## 研修概要

| 項目 | 内容 |
|------|------|
| 対象者 | TOS v0.3 運用担当者 |
| 所要時間 | 30分（10分 × 3セクション） |
| 前提知識 | PowerShell 基本操作 |
| 到達目標 | 日次運用を単独で実行できる |

---

## カリキュラム

| セクション | 内容 | 時間 |
|-----------|------|------|
| 1 | TOS の目的と正史の考え方 | 10分 |
| 2 | runbook の読み方と実行前/後チェック | 10分 |
| 3 | 失敗時の報告（failure_report_template） | 10分 |

---

## セクション1: TOS の目的と正史の考え方（10分）

### 1.1 TOS とは何か

TOS（Takagi Orchestration System）は AI を活用したタスクオーケストレーターです。

**目的**: 複数ジョブを順次実行し、結果を記録・管理する

### 1.2 フェーズの歴史

| フェーズ | 状態 | 説明 |
|---------|------|------|
| S-4 | 履歴 | 基本機能実装 |
| S-5 | 履歴（凍結） | experimental フェーズ |
| S-6 | **現行（完成）** | stable フェーズ |
| S-7 | 不要（確定） | 2025-12-14 に「やらない」と確定 |

### 1.3 正史コンテキストとは

**正史コンテキスト v1.0** = TOS の開発・運用における唯一の正しい文脈

- 本リポジトリのドキュメントが唯一の正しい情報源
- ドキュメントに記載のない操作は禁止
- 独自拡張・未定義運用は禁止

### 1.4 S-6 stable の原則

- 新機能追加・仕様変更は行わない
- 安定維持を最優先
- 問題があればエスカレーション（勝手に直さない）

### セクション1 確認テスト

- [ ] S-6 が現行フェーズであることを説明できる
- [ ] S-5 が履歴フェーズで触れないことを説明できる
- [ ] S-7 が不要と確定していることを説明できる
- [ ] 正史コンテキストの意味を説明できる

---

## セクション2: runbook の読み方と実行前/後チェック（10分）

### 2.1 runbook の構成

[runbook.md](runbook.md) には以下が記載されています：

1. 基本的なコマンド（run/test/cleanrun/checkpoint/rollback）
2. 設定ファイル（config_v0_3.json）の説明
3. ログファイルの場所と読み方
4. トラブルシューティング

### 2.2 実行の正順

```
cleanrun → test → run
```

この順序を守ること。逆順（run → test → cleanrun）は禁止。

### 2.3 ハンズオン: 基本コマンド

```powershell
# 作業ディレクトリへ移動
cd C:\Users\takag\00_dev\tos

# 現在の状態を確認
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test

# 正常時のみ継続実行
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
```

### 2.4 実行前チェックリスト

実行前に必ず確認：

- [ ] 作業ディレクトリが `C:\Users\takag\00_dev\tos` である
- [ ] 環境変数 OPENAI_API_KEY / ANTHROPIC_API_KEY が設定されている
- [ ] 前回の実行が正常終了している（logs/last_run_summary.txt を確認）

### 2.5 実行後チェックリスト

実行後に必ず確認：

- [ ] logs/last_run_summary.txt の内容を確認
- [ ] phase が done または job_loop_complete である
- [ ] エラーがあれば障害報告を作成

### 2.6 ハンズオン: ログ確認

```powershell
# 最新の実行サマリーを確認
Get-Content logs/last_run_summary.txt

# フェーズ状態を確認
Get-Content workspace/phase_state.json

# ステップログを確認（最新）
Get-ChildItem logs/steps/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

### セクション2 確認テスト

- [ ] 正順（cleanrun → test → run）を説明できる
- [ ] test モードの目的を説明できる
- [ ] 実行前チェックリストを実行できる
- [ ] logs/last_run_summary.txt の場所を知っている

---

## セクション3: 失敗時の報告（10分）

### 3.1 障害報告テンプレート

[failure_report_template.md](failure_report_template.md) を使用して報告する。

### 3.2 報告に必要な情報

| 項目 | 取得方法 |
|------|---------|
| 発生日時 | 手動記録 |
| commit hash | `git rev-parse HEAD` |
| 実行したコマンド | 手動記録 |
| エラーメッセージ | ログから転記 |
| 再現手順 | 手動記録 |

### 3.3 ハンズオン: ログ収集

```powershell
cd C:\Users\takag\00_dev\tos

# commit hash を取得
git rev-parse HEAD

# 直近のコミット履歴
git log -5 --oneline

# 変更差分を確認
git status

# 実行サマリーを確認
Get-Content logs/last_run_summary.txt

# フェーズ状態を確認
Get-Content workspace/phase_state.json
```

### 3.4 障害報告の流れ

1. **検知**: エラー発生を確認
2. **収集**: ログセットを収集
3. **記録**: テンプレートに記入
4. **報告**: 運用窓口へ連絡
5. **待機**: 指示を待つ（勝手に直さない）

### 3.5 勝手に直さない理由

- 原因特定前の修正は問題を複雑化させる
- ログが上書きされると調査が困難になる
- 正史コンテキストに違反する可能性がある

### セクション3 確認テスト

- [ ] 障害報告テンプレートの場所を知っている
- [ ] commit hash の取得方法を知っている
- [ ] 「勝手に直さない」理由を説明できる
- [ ] 障害報告の流れを説明できる

---

## よくあるミス3つと回避策

### ミス1: 正順を守らない

**症状**: unexpected phase エラー

**原因**: run を cleanrun なしで実行

**回避策**: 必ず cleanrun → test → run の順序を守る

### ミス2: ログを確認しない

**症状**: 障害が長時間放置される

**原因**: 実行後のログ確認を怠る

**回避策**: 実行後は必ず logs/last_run_summary.txt を確認

### ミス3: 勝手に直す

**症状**: 問題が複雑化、ログが失われる

**原因**: エスカレーション前に独自対応

**回避策**: 障害時は必ず報告してから指示を待つ

---

## 禁止事項（再掲）

| 禁止事項 | 理由 |
|---------|------|
| bash cd の使用 | PowerShell が標準実行環境 |
| 独自拡張の追加 | 正史コンテキストに違反 |
| 未定義運用の実施 | ドキュメントにない操作は禁止 |
| S-5 ファイルの変更 | 履歴フェーズとして凍結済み |
| S-7 の実施 | 不要と確定済み |
| 勝手に直す | 必ずエスカレーションすること |

---

## 研修後に配布するリンク一覧

研修終了後、以下のリンクをブックマークしてください。

| ドキュメント | 用途 | リンク |
|-------------|------|--------|
| 1枚資料 | クイックリファレンス | [s6_one_pager.md](s6_one_pager.md) |
| runbook | 運用手順詳細 | [runbook.md](runbook.md) |
| 定常ルーチン | 日次/週次/月次/障害対応 | [s6_routines.md](s6_routines.md) |
| 障害報告テンプレート | 障害発生時 | [failure_report_template.md](failure_report_template.md) |
| 用語集 | 用語確認 | [glossary.md](glossary.md) |
| 全ドキュメント索引 | 目次 | [index.md](index.md) |
| エスカレーション | 連絡先・判断基準 | [ops_escalation.md](ops_escalation.md) |

---

## 研修の合格条件

以下のすべてを満たすこと：

### 知識確認

- [ ] S-6 stable の目的を説明できる
- [ ] 正史コンテキストの意味を説明できる
- [ ] 正順（cleanrun → test → run）を説明できる
- [ ] 禁止事項を3つ以上列挙できる

### 実技確認

- [ ] test モードを実行できる
- [ ] logs/last_run_summary.txt を確認できる
- [ ] commit hash を取得できる
- [ ] 障害報告テンプレートの場所を知っている

### 態度確認

- [ ] 「勝手に直さない」ことに同意
- [ ] 不明点は質問することに同意
- [ ] 正史コンテキストに従うことに同意

---

## 研修記録

### 受講記録テンプレート

| 項目 | 内容 |
|------|------|
| 受講者名 | ________________ |
| 受講日 | ____年____月____日 |
| 講師名 | ________________ |
| 合否 | □ 合格 / □ 再受講 |
| 備考 | ________________ |

### 受講者一覧

| No. | 受講者名 | 受講日 | 合否 | 講師 |
|-----|---------|--------|------|------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 関連ドキュメント

- [s6_one_pager.md](s6_one_pager.md) - 1枚資料
- [runbook.md](runbook.md) - 運用手順ガイド
- [s6_routines.md](s6_routines.md) - 定常運用ルーチン
- [failure_report_template.md](failure_report_template.md) - 障害報告テンプレート
- [glossary.md](glossary.md) - 用語集
- [ops_escalation.md](ops_escalation.md) - エスカレーション手順
