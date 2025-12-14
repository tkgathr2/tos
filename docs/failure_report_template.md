# 障害報告テンプレート

**S-6 stable 障害報告標準**

本テンプレートを使用して障害を報告してください。

---

## 障害報告フォーマット

```
## 基本情報

報告日時: YYYY-MM-DD HH:MM
報告者:
commit hash:
mode: (run / test / cleanrun / checkpoint / rollback)
job_index:
job_name:

## 症状

(発生した問題を簡潔に記載)

## 再現手順

1.
2.
3.

## エラーメッセージ

(エラーメッセージをコピー)

## 添付ログ

### last_run_summary.json

```json
(logs/last_run_summary.json の内容をコピー)
```

### last_run_summary.txt

```
(logs/last_run_summary.txt の内容をコピー)
```

### step_*.json（直近）

```json
(logs/steps/step_*.json の内容をコピー)
```

## 環境情報

- OS: Windows XX
- PowerShell: X.X
- Python: X.XX
- git: X.XX

## 対処済みの内容

(試した対処があれば記載)

## 備考

(その他の情報)
```

---

## 必須項目チェックリスト

障害報告時に以下の項目がすべて含まれていることを確認してください：

- [ ] commit hash（`git rev-parse HEAD` で取得）
- [ ] mode（run / test / cleanrun / checkpoint / rollback）
- [ ] job_index（job_loop 使用時）
- [ ] job_name（job_loop 使用時）
- [ ] last_run_summary.json
- [ ] last_run_summary.txt
- [ ] 直近の step_*.json

---

## ログ取得コマンド

### commit hash

```powershell
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git rev-parse HEAD"
```

### last_run_summary.json

```powershell
powershell -Command "Get-Content 'C:\Users\takag\00_dev\tos\logs\last_run_summary.json'"
```

### last_run_summary.txt

```powershell
powershell -Command "Get-Content 'C:\Users\takag\00_dev\tos\logs\last_run_summary.txt'"
```

### 直近の step_*.json

```powershell
powershell -Command "Get-ChildItem 'C:\Users\takag\00_dev\tos\logs\steps' | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { Get-Content $_.FullName }"
```

### phase_summary.json

```powershell
powershell -Command "Get-Content 'C:\Users\takag\00_dev\tos\workspace\artifacts\phase_summary.json'"
```

---

## 異常時のログ提出セット

障害報告時に提出すべきログ一覧：

| ファイル | パス | 必須/任意 |
|---------|------|----------|
| last_run_summary.json | logs/last_run_summary.json | 必須 |
| last_run_summary.txt | logs/last_run_summary.txt | 必須 |
| step_*.json（直近） | logs/steps/step_*.json | 必須 |
| phase_summary.json | workspace/artifacts/phase_summary.json | 必須 |
| job_result.json | workspace/artifacts/job_result.json | 任意（存在時） |
| エラースクリーンショット | - | 推奨 |

---

## 再現に必要な情報

障害を再現するために必要な情報：

1. **commit hash**: 実行時のリポジトリ状態
2. **config_v0_3.json の設定**: 特にカスタマイズした箇所
3. **job_input.json の内容**: job_loop 使用時
4. **実行コマンド**: 実際に実行したコマンド
5. **実行順序**: cleanrun → test → run など

---

## 正史コンテキスト v1.0 との整合

本テンプレートは正史コンテキスト v1.0 に準拠しています。

障害報告は S-6 stable の運用ルール内で処理されます。
