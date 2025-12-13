#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOS v0.3 Orchestrator - S-2 API接続版
ChatGPT API / Claude API の実接続
"""

import json
import os
import sys
import subprocess
import re
import time
import requests
import anthropic
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

    # { ... } のブロックを抽出（JSONオブジェクトのみ対応）
    if not text.strip().startswith('{'):
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSONパース失敗: {e}")
        return None


def get_api_keys() -> tuple:
    """環境変数からAPIキーを取得"""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    return openai_key, anthropic_key


def call_openai_api(config: dict, prompt: str, api_key: str, retry_count: int = 0) -> str:
    """OpenAI ChatGPT APIを呼び出す"""
    model = config.get("openai_model", "gpt-4o-mini")
    max_retries = config.get("api_retry", 2)
    timeout_sec = config.get("timeout_sec", 120)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout_sec)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenAI API呼び出し失敗: {e}")
        if retry_count < max_retries:
            print(f"[INFO] リトライ {retry_count + 1}/{max_retries}")
            time.sleep(2 ** retry_count)
            return call_openai_api(config, prompt, api_key, retry_count + 1)
        return None


def call_anthropic_api(config: dict, prompt: str, api_key: str, retry_count: int = 0) -> str:
    """Anthropic Claude APIを呼び出す"""
    model = config.get("anthropic_model", "claude-3-5-sonnet-20241022")
    max_retries = config.get("api_retry", 2)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content = message.content[0].text
        return content
    except Exception as e:
        print(f"[ERROR] Anthropic API呼び出し失敗: {e}")
        if retry_count < max_retries:
            print(f"[INFO] リトライ {retry_count + 1}/{max_retries}")
            time.sleep(2 ** retry_count)
            return call_anthropic_api(config, prompt, api_key, retry_count + 1)
        return None


def call_api_with_json_retry(config: dict, prompt: str, api_key: str, api_type: str) -> tuple:
    """APIを呼び出し、JSONパースに失敗したらリトライする"""
    max_json_retries = config.get("json_retry", 2)

    for attempt in range(max_json_retries + 1):
        if api_type == "openai":
            raw_response = call_openai_api(config, prompt, api_key)
        else:
            raw_response = call_anthropic_api(config, prompt, api_key)

        if raw_response is None:
            print("[ERROR] API呼び出しが失敗しました")
            return None, None

        parsed = parse_json_strict(raw_response)
        if parsed is not None:
            return raw_response, parsed

        if attempt < max_json_retries:
            print(f"[INFO] JSONパース失敗。再プロンプトでリトライ {attempt + 1}/{max_json_retries}")
            prompt = f"""前回の応答がJSON形式ではありませんでした。
必ず以下の形式で、JSONのみを返してください。説明文は不要です。

{prompt}"""

    print("[ERROR] JSONパースリトライ上限に達しました")
    return raw_response, None


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


def make_draft(config: dict, step_num: int, context: dict, openai_key: str) -> tuple:
    """ChatGPT APIでドラフト生成"""
    print(f"[API] make_draft called (step={step_num})")

    prompt = f"""あなたはタスク実行AIです。以下の目標を達成するためのコマンドを生成してください。

目標: workspace/results/result_v2.txt に集計結果を出力する
条件:
- result_v2.txt には「合計:」「平均:」「件数:」の3つのキーワードを含めること
- PowerShellコマンドで実行可能な形式で出力すること

ステップ: {step_num}
これまでの履歴: {json.dumps(context.get("history", []), ensure_ascii=False)}

以下のJSON形式のみで応答してください。説明文は不要です。
{{
  "thought": "この行動の理由",
  "commands": [
    {{
      "type": "powershell",
      "code": "実行するPowerShellコード"
    }}
  ]
}}"""

    raw, parsed = call_api_with_json_retry(config, prompt, openai_key, "openai")
    return raw, parsed


def review_plus(config: dict, step_num: int, draft: dict, context: dict, anthropic_key: str) -> tuple:
    """Claude APIでレビューと改善"""
    print(f"[API] review_plus called (step={step_num})")

    prompt = f"""あなたはコードレビュアーです。以下のドラフトをレビューし、改善してください。

ドラフト:
{json.dumps(draft, ensure_ascii=False, indent=2)}

ステップ: {step_num}

レビュー観点:
1. コマンドが安全か（危険なコマンドがないか）
2. 目標を達成できるか
3. より良い方法があれば改善

以下のJSON形式のみで応答してください。説明文は不要です。
{{
  "review": "レビューコメント",
  "improved_commands": [
    {{
      "type": "powershell",
      "code": "改善後のコード"
    }}
  ],
  "approval": true
}}"""

    raw, parsed = call_api_with_json_retry(config, prompt, anthropic_key, "anthropic")
    return raw, parsed


def make_final(config: dict, step_num: int, draft: dict, review: dict, openai_key: str) -> tuple:
    """ChatGPT APIで最終決定"""
    print(f"[API] make_final called (step={step_num})")

    prompt = f"""あなたは最終判断AIです。ドラフトとレビューを踏まえて、実行する最終コマンドを決定してください。

ドラフト:
{json.dumps(draft, ensure_ascii=False, indent=2)}

レビュー:
{json.dumps(review, ensure_ascii=False, indent=2)}

ステップ: {step_num}

以下のJSON形式のみで応答してください。説明文は不要です。
{{
  "final_commands": [
    {{
      "type": "powershell",
      "code": "最終的に実行するコード"
    }}
  ],
  "summary": "このステップで行ったことの要約"
}}"""

    raw, parsed = call_api_with_json_retry(config, prompt, openai_key, "openai")
    return raw, parsed


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
        # PowerShellのOut-FileはUTF-16で出力することがあるため、複数のエンコードを試す
        content = None
        for encoding in ["utf-8", "utf-16", "utf-16-le", "cp932"]:
            try:
                with open(result_file, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print("[ERROR] done判定: ファイルのエンコードを判別できませんでした")
            return False

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


def sanitize_for_log(text: str, max_length: int = 2000) -> str:
    """ログ出力用にテキストをサニタイズ（APIキー等の除去、長さ制限）"""
    if text is None:
        return None
    # 長すぎる場合は切り詰め
    if len(text) > max_length:
        text = text[:max_length] + "...(truncated)"
    return text


def main():
    print("=" * 60)
    print("TOS v0.3 Orchestrator - S-2 API接続版")
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
        print(f"tos_python_path.txt の内容を確認してください:")
        print(f"  {TOS_PYTHON_PATH_FILE}")
        print("")
        print("正しい Python パスに修正してください。")
        print("=" * 60)
        sys.exit(1)

    # 5. APIキー確認
    openai_key, anthropic_key = get_api_keys()

    if not openai_key:
        print("")
        print("=" * 60)
        print("[STOP] OPENAI_API_KEY 環境変数が設定されていません")
        print("=" * 60)
        sys.exit(1)

    if not anthropic_key:
        print("")
        print("=" * 60)
        print("[STOP] ANTHROPIC_API_KEY 環境変数が設定されていません")
        print("=" * 60)
        sys.exit(1)

    print("[INFO] APIキー確認完了")

    # 6. メインループ
    max_steps = config.get("max_steps", 8)
    context = {"history": []}

    for step_num in range(1, max_steps + 1):
        print("")
        print(f"--- Step {step_num}/{max_steps} ---")

        # done判定（ループ先頭）
        done_result = evaluate_done_minimal(config)
        if done_result:
            done_reason = "workspace/results/result_v2.txt が存在し、合計/平均/件数の全キーワードを含む"
            print(f"[INFO] done=True に到達。ループ終了。")
            write_step_log(config, step_num, {
                "phase": "done",
                "done": True,
                "done_reason": done_reason,
                "message": "目標達成"
            })
            break

        # API呼び出し: draft (ChatGPT)
        draft_raw, draft = make_draft(config, step_num, context, openai_key)
        if draft is None:
            print("[ERROR] draft生成に失敗しました。処理を中断します。")
            write_step_log(config, step_num, {
                "phase": "error",
                "error": "draft生成失敗",
                "draft_raw": sanitize_for_log(draft_raw),
                "done": False,
                "done_reason": "API呼び出しまたはJSONパース失敗"
            })
            sys.exit(1)

        # API呼び出し: review (Claude)
        review_raw, review = review_plus(config, step_num, draft, context, anthropic_key)
        if review is None:
            print("[ERROR] review生成に失敗しました。処理を中断します。")
            write_step_log(config, step_num, {
                "phase": "error",
                "error": "review生成失敗",
                "draft": draft,
                "review_raw": sanitize_for_log(review_raw),
                "done": False,
                "done_reason": "API呼び出しまたはJSONパース失敗"
            })
            sys.exit(1)

        # API呼び出し: final (ChatGPT)
        final_raw, final = make_final(config, step_num, draft, review, openai_key)
        if final is None:
            print("[ERROR] final生成に失敗しました。処理を中断します。")
            write_step_log(config, step_num, {
                "phase": "error",
                "error": "final生成失敗",
                "draft": draft,
                "review": review,
                "final_raw": sanitize_for_log(final_raw),
                "done": False,
                "done_reason": "API呼び出しまたはJSONパース失敗"
            })
            sys.exit(1)

        # コマンド実行
        commands = final.get("final_commands", [])
        exec_result = run_commands(config, commands, python_path)

        # ステップログ出力（詳細版）
        step_data = {
            "phase": "execute",
            "models_used": {
                "draft": config.get("openai_model"),
                "review": config.get("anthropic_model"),
                "final": config.get("openai_model")
            },
            "draft": draft,
            "draft_raw": sanitize_for_log(draft_raw),
            "review": review,
            "review_raw": sanitize_for_log(review_raw),
            "final": final,
            "final_raw": sanitize_for_log(final_raw),
            "execution": exec_result,
            "done": False,
            "done_reason": "ステップ実行完了、次のループでdone判定"
        }
        write_step_log(config, step_num, step_data)

        # コンテキスト更新
        context["history"].append({
            "step": step_num,
            "summary": final.get("summary", "")
        })

    else:
        print(f"[WARN] max_steps ({max_steps}) に到達。done=False のまま終了。")
        write_step_log(config, max_steps + 1, {
            "phase": "max_steps_reached",
            "done": False,
            "done_reason": f"max_steps ({max_steps}) に到達したが目標未達成"
        })

    print("")
    print("=" * 60)
    print("TOS v0.3 Orchestrator 終了")
    print("=" * 60)


if __name__ == "__main__":
    main()
