# TOS v0.3 ドキュメント索引

**S-6 stable 完成版・封印済み**

**TOS v0.3 は 2025-12-14 に完結・封印されました。本索引は最終版です。**

本ページは TOS v0.3 の全ドキュメントへの入口です。

---

## クイックスタート

初めて TOS を使う方：

1. [README.md](../README.md) - 概要と Quick Start
2. [Runbook](runbook.md) - 運用手順ガイド

---

## TOS v0.3 FINAL

**最終完了宣言: [TOS v0.3 FINAL](tos_v0_3_final.md)** - 完成・封印・運用のみ

---

## S-6 Stable（現行フェーズ・完成・封印）

### 封印宣言

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| [S-6 最終封印宣言](s6_sealed.md) | TOS v0.3 完結・封印宣言 | 全員 |

### 運用ドキュメント

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| [S-6 Stable](s6_stable.md) | フェーズ定義・運用ルール | 全員 |
| [S-6 Operations](s6_operations.md) | 安定運用ガイド（フロー・ログ・組織） | 運用担当者 |
| [S-6 Governance](s6_governance.md) | ガバナンス・判断基準・拡張ルール | 承認者・管理者 |
| [S-6 Environment](s6_environment.md) | 実行環境標準（PowerShell・改行） | 開発者・運用者 |
| [S-6 Completion](s6_completion.md) | S-6 完成宣言 | 全員 |

### 運用ツール

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| [Runbook](runbook.md) | 運用手順ガイド | 運用担当者 |
| [S-6 Routines](s6_routines.md) | 日次/週次/月次/障害対応ルーチン | 運用担当者 |
| [S-6 Stable Checklist](s6_stable_checklist.md) | 運用チェックリスト | 運用担当者 |
| [Failure Report Template](failure_report_template.md) | 障害報告テンプレート | 運用担当者 |
| [Glossary](glossary.md) | 用語集 | 全員 |

### 運用移行・周知

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| [S-6 1枚資料](s6_one_pager.md) | 運用者向けクイックリファレンス | 運用担当者 |
| [周知メッセージ雛形](ops_announcement_slack.md) | Slack/Teams 等での周知テンプレート | 管理者 |
| [30分研修](s6_training_30min.md) | 運用者向け最短研修コース | 運用担当者 |
| [エスカレーション](ops_escalation.md) | 障害レベル・連絡先・判断基準 | 全員 |

### 変更履歴

| ドキュメント | 内容 |
|-------------|------|
| [Release Notes](release_notes.md) | 変更履歴 |

### 監査記録

| ドキュメント | 内容 |
|-------------|------|
| [S-6 ドキュメント監査](s6_docs_audit.md) | 整合性監査報告（2025-12-14） |
| [S-6 封印後検証](s6_seal_verification.md) | 封印実効性検証報告（2025-12-14） |

---

## S-7（検討完了・不要と確定）

**S-7 は 2025-12-14 に「不要」と確定しました。実施しません。**

| ドキュメント | 内容 |
|-------------|------|
| [S-7 検討結果](s7_proposal.md) | 検討経緯・結論・再検討条件 |

---

## S-5（履歴フェーズ・凍結）

**S-5 は履歴フェーズです。変更は禁止されています。**

| ドキュメント | 内容 |
|-------------|------|
| [S-5 Closeout](s5_closeout.md) | S-5 closeout 宣言 |
| [S-5 Definition](s5_definition.md) | S-5 フェーズ定義 |
| [S-5 Closeout Checklist](s5_closeout_checklist.md) | closeout チェックリスト |

---

## 引き継ぎ時の推奨読み順

1. **README.md** - 概要把握
2. **docs/s6_stable.md** - S-6 運用ルールの確認
3. **docs/s6_operations.md** - 安定運用ガイド
4. **docs/s6_governance.md** - ガバナンス・判断基準
5. **docs/s6_environment.md** - 実行環境標準
6. **docs/runbook.md** - 運用手順の確認
7. **docs/glossary.md** - 用語の確認
8. **docs/s6_stable_checklist.md** - 運用チェックリスト

---

## 正史コンテキスト v1.0

本リポジトリは正史コンテキスト v1.0 に準拠しています。

- TOS v0.3 は S-6 stable フェーズで完成・運用中
- S-5 は履歴フェーズとして凍結済み
- 新機能追加・仕様変更は行わない（安定維持優先）
- 本リポジトリのドキュメントが唯一の正しい情報源
