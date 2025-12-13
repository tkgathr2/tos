# ClaudeCode改善案作成のための確認チェックリスト

## 必須（優先度高）

1. **`.claude/CLAUDE.md`** （あれば）
   - 現在のエージェント指示を確認したい

2. **`tools/init.ps1`**
   - 既存の初期化処理を拡張ベースにしたい

3. **`.claude/settings.json`** または **`.claude/settings.local.json`** （あれば）
   - 現在の設定を確認

---

## あると嬉しい（優先度中）

4. **プロジェクトルートのディレクトリ構造**
   - PowerShellで `tree /F .claude` と `tree tools` の出力でOK

5. **「同じBashが繰り返し出る」ときの具体的なログ例**
   - どのコマンドが何回出るか把握したい
   - スクリーンショットかテキストコピーで

---

## 任意（あれば参考に）

6. **orchestrator関連ファイル**（step_state.json的なものがあれば）
   - TOS独自の状態管理があるか確認

---

特に **1, 2, 5** があれば、そのまま使えるCLAUDE.mdテンプレートと改善版init.ps1を作成できます。
