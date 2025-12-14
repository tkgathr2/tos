# S-6 実行環境標準

**S-6 stable 環境標準策定日: 2025-12-14**

本ドキュメントは TOS v0.3 S-6 stable の実行環境標準を定義します。

---

## 1. PowerShell を標準とする

**Windows 実行は PowerShell を標準とします。**

### 理由

1. TOS v0.3 は Windows 環境で開発・テストされている
2. cc_run.ps1 は PowerShell スクリプトである
3. bash での Windows パス操作は失敗しやすい
4. ClaudeCode は PowerShell コマンドを優先すべき

### 禁止: bash での Windows パス cd

以下のコマンドは **失敗する可能性が高い** ため使用禁止：

```bash
# 禁止例（bash）
cd C:\Users\takag\00_dev\tos
cd /d "C:\Users\takag\00_dev\tos"
```

bash は Windows パス形式を正しく解釈できないことがあります。

### 推奨: PowerShell でのディレクトリ移動

```powershell
# 推奨例（PowerShell）
Set-Location 'C:\Users\takag\00_dev\tos'
```

または PowerShell -Command でラップする：

```powershell
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git status"
```

---

## 2. パスはクォート必須

**すべてのパスはクォート（シングルまたはダブル）で囲むこと。**

### 理由

1. スペースを含むパスでエラーを防ぐ
2. 特殊文字のエスケープ問題を回避
3. 一貫性のある記述

### 推奨例

```powershell
# 正しい
Set-Location 'C:\Users\takag\00_dev\tos'
powershell -ExecutionPolicy Bypass -File '.\tools\cc_run.ps1' -Mode run

# 間違い（スペースがあると失敗）
Set-Location C:\Users\takag\00_dev\tos
```

---

## 3. ClaudeCode 出力のコマンドルール

**ClaudeCode が出力するコマンドは PowerShell を優先すること。**

### ルール

1. Windows 環境では PowerShell コマンドを出力する
2. bash コマンドは避ける（特に cd, path 操作）
3. パスは必ずクォートで囲む
4. 複数コマンドは `;` で連結

### 推奨テンプレート

```powershell
# 単一コマンド
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; <command>"

# TOS 実行
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\cc_run.ps1' -Mode <mode>

# Git 操作
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git status"
```

---

## 4. 推奨コマンド例

### 4.1 TOS 実行コマンド

```powershell
# cleanrun
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\cc_run.ps1' -Mode cleanrun

# test
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\cc_run.ps1' -Mode test

# run
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\cc_run.ps1' -Mode run

# checkpoint
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\checkpoint.ps1' -Name 'checkpoint_name'

# rollback
powershell -ExecutionPolicy Bypass -File 'C:\Users\takag\00_dev\tos\tools\cc_run.ps1' -Mode rollback
```

### 4.2 Git 操作コマンド

```powershell
# status
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git status"

# diff
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git diff"

# add
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git add ."

# commit
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git commit -m 'message'"

# push
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; git push"
```

### 4.3 ファイル確認コマンド

```powershell
# ディレクトリ存在確認
powershell -Command "Test-Path 'C:\Users\takag\00_dev\tos'"

# ファイル一覧
powershell -Command "Set-Location 'C:\Users\takag\00_dev\tos'; Get-ChildItem"

# ファイル内容確認
powershell -Command "Get-Content 'C:\Users\takag\00_dev\tos\README.md'"
```

---

## 5. 改行コード方針

### 方針

- **リポジトリ内**: LF を標準とする
- **Windows チェックアウト時**: CRLF に変換される（git の autocrlf 設定による）
- **警告の扱い**: LF/CRLF 警告は無視してよい（.gitattributes で管理）

### git config 確認方法

```powershell
powershell -Command "git config core.autocrlf"
```

### 推奨設定

```powershell
# 推奨: false（変換しない）または input（コミット時のみ LF に変換）
git config core.autocrlf false
```

### 方針に反する場合の是正

1. `.gitattributes` の設定を確認
2. 改行差分のみのコミットは避ける
3. エディタの設定を `.editorconfig` に合わせる

---

## 6. 本ドキュメントの位置づけ

本ドキュメントは S-6 stable の運用ルール内で策定されています。

- 新機能追加ではない（環境標準の明文化）
- 仕様変更ではない（既存動作の文書化）
- S-5 への変更は含まない

### 正史コンテキスト v1.0 との整合

本ドキュメントは正史コンテキスト v1.0 に準拠しています。
