#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOS v0.3 Orchestrator - S-1 骨格実装
ダミーAPI（固定JSON）で動作確認用
"""

import json
import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path

# グローバル定数
BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config_v0_3.json"
TOS_PYTHON_PATH_FILE = BASE_DIR / "tos_python_path.txt"


def load_config() -> dict:
    """設定ファイルを読み込む"""
    if not CONFIG_FILE.exists():
        print(f"[ERROR] 設定ファイルが見つかりません: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    print(f"[INFO] 設定ファイル読み込み完了: {CONFIG_FILE}")
    return config


def ensure_dirs(config: dict) -> None:
    """必要なディレクトリを作成"""
    workspace_dir = BASE_DIR / config["workspace_dir"]
    logs_dir = BASE_DIR / config["logs_dir"]

    dirs = [
        workspace_dir / "generated",
        workspace_dir / "results",
        workspace_dir / "artifacts",
        logs_dir / "steps",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] ディレクトリ確認完了")


def load_tos_python_path() -> str:
    """tos_python_path.txt から Python パスを読み込む"""
    if not TOS_PYTHON_PATH_FILE.exists():
        return None

    with open(TOS_PYTHON_PATH_FILE, "r", encoding="utf-8") as f:
        path = f.read().strip()

    return path if path else None


def verify_python(python_path: str) -> bool:
    """Python実行可能性を検証"""
    if not python_path:
        return False

    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"[INFO] Python検証OK: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"[WARN] Python検証失敗: {e}")

    return False


def parse_json_strict(text: str) -> dict:
    """JSON文字列を厳密にパース"""
    # ```json ... ``` のブロックを抽出
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSONパース失敗: {e}")
        return None


def write_step_log(config: dict, step_num: int, data: dict) -> Path:
    """ステップログを書き込む"""
    logs_dir = BASE_DIR / config["logs_dir"] / "steps"
    log_file = logs_dir / f"step_{step_num:03d}.json"

    data["timestamp"] = datetime.now().isoformat()
    data["step_num"] = step_num

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] ステップログ出力: {log_file}")
    return log_file


def dummy_make_draft(step_num: int, context: dict) -> dict:
    """ダミー: ドラフト生成（固定JSON返却）"""
    print(f"[DUMMY] make_draft called (step={step_num})")

    # step_001 では result_v2.txt を作成するコマンドを返す
    if step_num == 1:
        return {
            "thought": "初回なので result_v2.txt を作成して done 判定に到達させる",
            "commands": [
                {
                    "type": "powershell",
                    "code": """
$content = @"
=== 集計結果 ===
合計: 12345
平均: 123.45
件数: 100
================
"@
Set-Content -Path "workspace/results/result_v2.txt" -Value $content -Encoding UTF8
"""
                }
            ]
        }

    return {
        "thought": f"ステップ {step_num} の処理",
        "commands": []
    }


def dummy_review_plus(step_num: int, draft: dict, context: dict) -> dict:
    """ダミー: レビュー＋改善（固定JSON返却）"""
    print(f"[DUMMY] review_plus called (step={step_num})")

    return {
        "review": "ダミーレビュー: 問題なし",
        "improved_commands": draft.get("commands", []),
        "approval": True
    }


def dummy_make_final(step_num: int, draft: dict, review: dict) -> dict:
    """ダミー: 最終決定（固定JSON返却）"""
    print(f"[DUMMY] make_final called (step={step_num})")

    return {
        "final_commands": review.get("improved_commands", []),
        "summary": f"ステップ {step_num} 完了"
    }


def run_commands(config: dict, commands: list, python_path: str) -> dict:
    """コマンドを実行"""
    results = []
    workspace_dir = BASE_DIR / config["workspace_dir"]

    for cmd in commands:
        cmd_type = cmd.get("type", "")
        code = cmd.get("code", "")

        if cmd_type == "powershell":
            try:
                result = subprocess.run(
                    ["powershell", "-Command", code],
                    capture_output=True,
                    text=True,
                    timeout=config.get("timeout_sec", 120),
                    cwd=str(BASE_DIR)
                )
                results.append({
                    "type": cmd_type,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                print(f"[INFO] PowerShell実行完了 (rc={result.returncode})")
            except Exception as e:
                results.append({
                    "type": cmd_type,
                    "error": str(e)
                })
                print(f"[ERROR] PowerShell実行失敗: {e}")

        elif cmd_type == "python":
            try:
                result = subprocess.run(
                    [python_path, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=config.get("timeout_sec", 120),
                    cwd=str(workspace_dir)
                )
                results.append({
                    "type": cmd_type,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                print(f"[INFO] Python実行完了 (rc={result.returncode})")
            except Exception as e:
                results.append({
                    "type": cmd_type,
                    "error": str(e)
                })
                print(f"[ERROR] Python実行失敗: {e}")

    return {"command_results": results}


def evaluate_done_minimal(config: dict) -> bool:
    """done判定（最小版）

    条件:
    - workspace/results/result_v2.txt が存在
    - 「合計:」「平均:」「件数:」を全て含む
    """
    result_file = BASE_DIR / config["workspace_dir"] / "results" / "result_v2.txt"

    if not result_file.exists():
        print(f"[INFO] done判定: result_v2.txt が存在しない -> False")
        return False

    try:
        with open(result_file, "r", encoding="utf-8") as f:
            content = f.read()

        required = ["合計:", "平均:", "件数:"]
        missing = [r for r in required if r not in content]

        if missing:
            print(f"[INFO] done判定: 必須キーワード不足 {missing} -> False")
            return False

        print(f"[INFO] done判定: 全条件クリア -> True")
        return True

    except Exception as e:
        print(f"[ERROR] done判定エラー: {e}")
        return False


def main():
    print("=" * 60)
    print("TOS v0.3 Orchestrator - S-1 骨格版")
    print("=" * 60)

    # 1. 設定読み込み
    config = load_config()

    # 2. ディレクトリ確認
    ensure_dirs(config)

    # 3. Python パス確認（tos_python_path.txt）
    python_path = load_tos_python_path()

    if python_path is None:
        print("")
        print("=" * 60)
        print("[STOP] tos_python_path.txt が見つかりません")
        print("=" * 60)
        print("")
        print("【次の一手】")
        print("以下のファイルを作成してください:")
        print(f"  {TOS_PYTHON_PATH_FILE}")
        print("")
        print("内容: Python実行ファイルのフルパスを1行で記載")
        print("例: C:\\Python311\\python.exe")
        print("")
        print("Pythonのパスが分からない場合は、コマンドプロンプトで")
        print("  where python")
        print("を実行して確認してください。")
        print("=" * 60)
        sys.exit(1)

    # 4. Python 検証
    if not verify_python(python_path):
        print("")
        print("=" * 60)
        print(f"[STOP] Python実行ファイルが無効です: {python_path}")
        print("=" * 60)
        print("")
        print("【次の一手】")
        print(f"tos_python_path.txt の内容を確認してください:")
        print(f"  {TOS_PYTHON_PATH_FILE}")
        print("")
        print("正しい Python パスに修正してください。")
        print("=" * 60)
        sys.exit(1)

    # 5. メインループ
    max_steps = config.get("max_steps", 8)
    context = {"history": []}

    for step_num in range(1, max_steps + 1):
        print("")
        print(f"--- Step {step_num}/{max_steps} ---")

        # done判定（ループ先頭）
        if evaluate_done_minimal(config):
            print(f"[INFO] done=True に到達。ループ終了。")
            write_step_log(config, step_num, {
                "phase": "done",
                "done": True,
                "message": "目標達成"
            })
            break

        # ダミーAPI呼び出し
        draft = dummy_make_draft(step_num, context)
        review = dummy_review_plus(step_num, draft, context)
        final = dummy_make_final(step_num, draft, review)

        # コマンド実行
        commands = final.get("final_commands", [])
        exec_result = run_commands(config, commands, python_path)

        # ステップログ出力
        step_data = {
            "phase": "execute",
            "draft": draft,
            "review": review,
            "final": final,
            "execution": exec_result,
            "done": False
        }
        write_step_log(config, step_num, step_data)

        # コンテキスト更新
        context["history"].append({
            "step": step_num,
            "summary": final.get("summary", "")
        })

    else:
        print(f"[WARN] max_steps ({max_steps}) に到達。done=False のまま終了。")

    print("")
    print("=" * 60)
    print("TOS v0.3 Orchestrator 終了")
    print("=" * 60)


if __name__ == "__main__":
    main()
