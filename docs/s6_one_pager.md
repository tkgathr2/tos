# TOS v0.3 S-6 運用者向け1枚資料

**S-6 stable 運用クイックリファレンス（完成・封印済み）**

---

## S-6 とは何か

TOS v0.3 の安定運用フェーズ。S-5 で開発・検証した機能を本番環境で継続利用する。
新機能追加・仕様変更は行わない（安定維持優先）。
本リポジトリのドキュメントが唯一の正しい情報源。

**S-6 stable は 2025-12-14 に完成・封印されました。以後は運用のみが許可されます。**

---

## 定常運用リンク

| ルーチン | 参照先 |
|---------|--------|
| 日次ルーチン | [s6_routines.md#日次ルーチン](s6_routines.md#日次ルーチン) |
| 週次ルーチン | [s6_routines.md#週次ルーチン](s6_routines.md#週次ルーチン) |
| 月次ルーチン | [s6_routines.md#月次ルーチン](s6_routines.md#月次ルーチン) |
| 障害対応ルーチン | [s6_routines.md#障害対応ルーチン](s6_routines.md#障害対応ルーチン) |

詳細手順: [Runbook](runbook.md) | 全ドキュメント索引: [index.md](index.md)

---

## 実行の正順

```
cleanrun → test → run
```

1. **cleanrun**: 状態を初期化して実行
2. **test**: 状態を検証
3. **run**: 継続実行（job_loop_complete まで繰り返し）

```powershell
cd C:\Users\takag\00_dev\tos
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode cleanrun
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode test
powershell -ExecutionPolicy Bypass -File .\tools\cc_run.ps1 -Mode run
```

---

## 禁止事項

| 禁止事項 | 理由 |
|---------|------|
| `bash cd` の使用 | PowerShell が標準実行環境 |
| 独自拡張の追加 | 正史コンテキストに違反 |
| 未定義運用の実施 | ドキュメントにない操作は禁止 |
| S-5 ファイルの変更 | 履歴フェーズとして凍結済み |
| S-7 の実施 | 不要と確定済み |
| 勝手に直す | 必ずエスカレーションすること |

---

## 障害時に提出するログセット

障害発生時は以下を収集し、障害報告に添付すること。

### 必須ログ

| ファイル | パス |
|---------|------|
| ステップログ | `logs/steps/step_*.json` |
| フェーズ状態 | `workspace/phase_state.json` |
| 実行サマリー | `logs/last_run_summary.json` |
| 実行サマリー（TXT） | `logs/last_run_summary.txt` |

### 追加情報

| 項目 | 取得方法 |
|------|---------|
| 現在の commit hash | `git rev-parse HEAD` |
| 直近のコミット履歴 | `git log -5 --oneline` |
| 変更差分 | `git status` |

### ログ収集コマンド

```powershell
cd C:\Users\takag\00_dev\tos
git rev-parse HEAD
git log -5 --oneline
git status
Get-Content logs/last_run_summary.txt
Get-Content workspace/phase_state.json
```

---

## 障害報告テンプレート

障害報告は [failure_report_template.md](failure_report_template.md) を使用すること。

---

## 連絡先（運用窓口）

| 役割 | 担当者 | 連絡先 |
|------|--------|--------|
| 一次窓口（運用者） | ________________ | ________________ |
| 二次窓口（開発者） | ________________ | ________________ |
| 緊急連絡先 | ________________ | ________________ |

※ 担当者名と連絡先は運用開始前に記入すること。

---

## エスカレーション基準

| レベル | 条件 | 対応 |
|--------|------|------|
| 軽微 | ログ確認で原因特定可能 | 運用者で完結 |
| 重大 | 原因不明/再現性あり | 開発者へ即連絡 |
| 停止 | 実行継続不可 | 実行停止・rollback判断 |

詳細: [ops_escalation.md](ops_escalation.md)

---

## 関連ドキュメント

- [TOS v0.3 FINAL](tos_v0_3_final.md) - **最終完了宣言**
- [README.md](../README.md) - 概要
- [index.md](index.md) - 全ドキュメント索引
- [runbook.md](runbook.md) - 運用手順ガイド
- [s6_routines.md](s6_routines.md) - 定常運用ルーチン
- [glossary.md](glossary.md) - 用語集
- [ops_escalation.md](ops_escalation.md) - エスカレーション手順
