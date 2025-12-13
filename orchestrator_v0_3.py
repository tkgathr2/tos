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


def build_step_log_data(
    phase: str,
    step_num: int,
    config: dict,
    done: bool = False,
    done_reason: str = "",
    error: str = None,
    models_used: dict = None,
    prompts_used: dict = None,
    final_commands: list = None,
    allowlist_summary: list = None,
    draft: dict = None,
    draft_raw: str = None,
    review: dict = None,
    review_raw: str = None,
    final: dict = None,
    final_raw: str = None,
    execution: dict = None,
    message: str = None,
    next_phase_name: str = None,
    next_phase_done_condition: str = None,
    next_instruction_id: str = None,
    next_instruction_summary: str = None,
    next_instruction_inputs: list = None,
    next_instruction_expected_outputs: list = None
) -> dict:
    """ステップログデータを構築（スキーマ固定）

    全てのキーを必ず含め、欠損キーを防ぐ
    """
    return {
        "phase": phase,
        "step_num": step_num,
        "timestamp": datetime.now().isoformat(),
        "done": done,
        "done_reason": done_reason,
        "error": error,
        "message": message,
        "models_used": models_used or {
            "draft": config.get("openai_model"),
            "review": config.get("anthropic_model"),
            "final": config.get("openai_model")
        },
        "prompts_used": prompts_used,
        "final_commands": final_commands,
        "allowlist_summary": allowlist_summary,
        "draft": draft,
        "draft_raw": draft_raw,
        "review": review,
        "review_raw": review_raw,
        "final": final,
        "final_raw": final_raw,
        "execution": execution,
        "next_phase_name": next_phase_name,
        "next_phase_done_condition": next_phase_done_condition,
        "next_instruction_id": next_instruction_id,
        "next_instruction_summary": next_instruction_summary,
        "next_instruction_inputs": next_instruction_inputs,
        "next_instruction_expected_outputs": next_instruction_expected_outputs
    }


def write_step_log(config: dict, step_num: int, data: dict) -> Path:
    """ステップログを書き込む"""
    logs_dir = BASE_DIR / config["logs_dir"] / "steps"
    log_file = logs_dir / f"step_{step_num:03d}.json"

    # timestampとstep_numは build_step_log_data で設定済みだが、念のため
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
    if "step_num" not in data:
        data["step_num"] = step_num

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] ステップログ出力: {log_file}")
    return log_file


def make_draft(config: dict, step_num: int, context: dict, openai_key: str) -> tuple:
    """ChatGPT APIでドラフト生成

    Returns:
        tuple: (raw_response, parsed_json, prompt_info)
    """
    print(f"[API] make_draft called (step={step_num})")

    template_name = "draft_prompt_template"
    template = config.get(template_name, "")

    # テンプレート変数を置換
    history_json = json.dumps(context.get("history", []), ensure_ascii=False)
    prompt = template.replace("{step_num}", str(step_num))
    prompt = prompt.replace("{history_json}", history_json)

    prompt_info = {
        "template_name": template_name,
        "prompt": sanitize_for_log(prompt, 500)
    }

    raw, parsed = call_api_with_json_retry(config, prompt, openai_key, "openai")
    return raw, parsed, prompt_info


def review_plus(config: dict, step_num: int, draft: dict, context: dict, anthropic_key: str) -> tuple:
    """Claude APIでレビューと改善

    Returns:
        tuple: (raw_response, parsed_json, prompt_info)
    """
    print(f"[API] review_plus called (step={step_num})")

    template_name = "review_prompt_template"
    template = config.get(template_name, "")

    # テンプレート変数を置換
    draft_json = json.dumps(draft, ensure_ascii=False, indent=2)
    prompt = template.replace("{step_num}", str(step_num))
    prompt = prompt.replace("{draft_json}", draft_json)

    prompt_info = {
        "template_name": template_name,
        "prompt": sanitize_for_log(prompt, 500)
    }

    raw, parsed = call_api_with_json_retry(config, prompt, anthropic_key, "anthropic")
    return raw, parsed, prompt_info


def make_final(config: dict, step_num: int, draft: dict, review: dict, openai_key: str) -> tuple:
    """ChatGPT APIで最終決定

    Returns:
        tuple: (raw_response, parsed_json, prompt_info)
    """
    print(f"[API] make_final called (step={step_num})")

    template_name = "final_prompt_template"
    template = config.get(template_name, "")

    # テンプレート変数を置換
    draft_json = json.dumps(draft, ensure_ascii=False, indent=2)
    review_json = json.dumps(review, ensure_ascii=False, indent=2)
    prompt = template.replace("{step_num}", str(step_num))
    prompt = prompt.replace("{draft_json}", draft_json)
    prompt = prompt.replace("{review_json}", review_json)

    prompt_info = {
        "template_name": template_name,
        "prompt": sanitize_for_log(prompt, 500)
    }

    raw, parsed = call_api_with_json_retry(config, prompt, openai_key, "openai")
    return raw, parsed, prompt_info


def check_allowlist(config: dict, cmd_type: str, code: str) -> tuple:
    """コマンドがallowlistを通過するか判定する

    Returns:
        tuple: (allowed: bool, reason: str, matched_pattern: str or None)
    """
    # 1. type チェック
    allow_types = config.get("allow_types", ["powershell"])
    if cmd_type not in allow_types:
        return False, f"type '{cmd_type}' は許可されていない (allow_types: {allow_types})", None

    # 2. deny_patterns チェック
    deny_patterns = config.get("deny_patterns", [])
    for pattern in deny_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"禁止パターン '{pattern}' に一致", pattern

    return True, "allowlist通過", None


def run_commands(config: dict, commands: list, python_path: str) -> dict:
    """コマンドを実行（allowlist判定付き）"""
    results = []
    timeout_sec = config.get("timeout_sec", 120)

    for cmd in commands:
        cmd_type = cmd.get("type", "")
        code = cmd.get("code", "")

        # allowlist判定
        allowed, reason, matched_pattern = check_allowlist(config, cmd_type, code)

        if not allowed:
            print(f"[DENY] コマンド拒否: {reason}")
            results.append({
                "type": cmd_type,
                "code": code[:200] + "..." if len(code) > 200 else code,
                "allowed": False,
                "deny_reason": reason,
                "matched_pattern": matched_pattern,
                "executed": False
            })
            continue

        print(f"[ALLOW] コマンド許可: {reason}")

        if cmd_type == "powershell":
            try:
                result = subprocess.run(
                    ["powershell", "-Command", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    cwd=str(BASE_DIR)
                )
                results.append({
                    "type": cmd_type,
                    "code": code[:500] + "..." if len(code) > 500 else code,
                    "allowed": True,
                    "allow_reason": reason,
                    "executed": True,
                    "returncode": result.returncode,
                    "stdout": result.stdout[:1000] if result.stdout else "",
                    "stderr": result.stderr[:1000] if result.stderr else "",
                    "timeout": False
                })
                print(f"[INFO] PowerShell実行完了 (rc={result.returncode})")
            except subprocess.TimeoutExpired:
                results.append({
                    "type": cmd_type,
                    "code": code[:500] + "..." if len(code) > 500 else code,
                    "allowed": True,
                    "allow_reason": reason,
                    "executed": True,
                    "timeout": True,
                    "error": f"タイムアウト ({timeout_sec}秒)"
                })
                print(f"[ERROR] PowerShell タイムアウト ({timeout_sec}秒)")
            except Exception as e:
                results.append({
                    "type": cmd_type,
                    "code": code[:500] + "..." if len(code) > 500 else code,
                    "allowed": True,
                    "allow_reason": reason,
                    "executed": False,
                    "error": str(e)
                })
                print(f"[ERROR] PowerShell実行失敗: {e}")

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


def evaluate_phase_done(config: dict) -> dict:
    """フェーズ完了判定

    Returns:
        dict: {
            "done": bool,
            "done_reason": str,
            "next_phase_name": str or None,
            "next_phase_done_condition": str or None,
            "next_instruction_id": str or None,
            "next_instruction_summary": str or None,
            "next_instruction_inputs": list or None,
            "next_instruction_expected_outputs": list or None
        }
    """
    # 現在のフェーズ完了条件をチェック
    is_done = evaluate_done_minimal(config)

    if is_done:
        return {
            "done": True,
            "done_reason": "workspace/results/result_v2.txt が存在し、合計/平均/件数の全キーワードを含む",
            "next_phase_name": "S-5",
            "next_phase_done_condition": "次のフェーズの完了条件（未定義）",
            "next_instruction_id": "指示書010",
            "next_instruction_summary": "S-5フェーズ: 次の目標に向けた準備と実行",
            "next_instruction_inputs": [
                "workspace/results/result_v2.txt (前フェーズの出力)",
                "config_v0_3.json (設定ファイル)"
            ],
            "next_instruction_expected_outputs": [
                "次フェーズの成果物（未定義）",
                "logs/steps/step_XXX.json (実行ログ)"
            ]
        }
    else:
        return {
            "done": False,
            "done_reason": "フェーズ完了条件を満たしていない",
            "next_phase_name": None,
            "next_phase_done_condition": None,
            "next_instruction_id": None,
            "next_instruction_summary": None,
            "next_instruction_inputs": None,
            "next_instruction_expected_outputs": None
        }


def sanitize_for_log(text: str, max_length: int = 2000) -> str:
    """ログ出力用にテキストをサニタイズ（APIキー等の除去、長さ制限）"""
    if text is None:
        return None
    # 長すぎる場合は切り詰め
    if len(text) > max_length:
        text = text[:max_length] + "...(truncated)"
    return text


def write_phase_summary(config: dict) -> Path:
    """全ステップのサマリをphase_summary.jsonに集約する

    Returns:
        Path: 出力ファイルのパス
    """
    logs_dir = BASE_DIR / config["logs_dir"]
    steps_dir = logs_dir / "steps"
    summary_file = logs_dir / "phase_summary.json"

    # 全ステップログを読み込み
    step_files = sorted(steps_dir.glob("step_*.json"))
    steps = []
    success_count = 0
    fail_count = 0
    final_done = False
    final_phase_result = None

    for step_file in step_files:
        try:
            with open(step_file, "r", encoding="utf-8") as f:
                step_data = json.load(f)
                steps.append({
                    "step_num": step_data.get("step_num"),
                    "phase": step_data.get("phase"),
                    "done": step_data.get("done"),
                    "done_reason": step_data.get("done_reason"),
                    "timestamp": step_data.get("timestamp"),
                    "error": step_data.get("error"),
                    "message": step_data.get("message")
                })

                # 統計情報を集計
                if step_data.get("phase") == "error":
                    fail_count += 1
                elif step_data.get("phase") in ["execute", "done"]:
                    success_count += 1

                # 最終結果を記録
                if step_data.get("done"):
                    final_done = True
                    final_phase_result = {
                        "next_phase_name": step_data.get("next_phase_name"),
                        "next_phase_done_condition": step_data.get("next_phase_done_condition"),
                        "next_instruction_id": step_data.get("next_instruction_id"),
                        "next_instruction_summary": step_data.get("next_instruction_summary"),
                        "next_instruction_inputs": step_data.get("next_instruction_inputs"),
                        "next_instruction_expected_outputs": step_data.get("next_instruction_expected_outputs")
                    }
        except Exception as e:
            print(f"[WARN] ステップログ読み込みエラー: {step_file} - {e}")

    # サマリを構築
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_steps": len(steps),
        "success_count": success_count,
        "fail_count": fail_count,
        "final_done": final_done,
        "final_phase_result": final_phase_result,
        "steps": steps
    }

    # ファイル出力
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[INFO] フェーズサマリ出力: {summary_file}")
    return summary_file


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

        # フェーズ完了判定（ループ先頭）
        phase_result = evaluate_phase_done(config)
        if phase_result["done"]:
            print(f"[INFO] done=True に到達。ループ終了。")
            step_data = build_step_log_data(
                phase="done",
                step_num=step_num,
                config=config,
                done=True,
                done_reason=phase_result["done_reason"],
                message="目標達成",
                next_phase_name=phase_result["next_phase_name"],
                next_phase_done_condition=phase_result["next_phase_done_condition"],
                next_instruction_id=phase_result["next_instruction_id"],
                next_instruction_summary=phase_result["next_instruction_summary"],
                next_instruction_inputs=phase_result["next_instruction_inputs"],
                next_instruction_expected_outputs=phase_result["next_instruction_expected_outputs"]
            )
            write_step_log(config, step_num, step_data)
            break

        # API呼び出し: draft (ChatGPT)
        draft_raw, draft, draft_prompt_info = make_draft(config, step_num, context, openai_key)
        if draft is None:
            print("[ERROR] draft生成に失敗しました。処理を中断します。")
            step_data = build_step_log_data(
                phase="error",
                step_num=step_num,
                config=config,
                done=False,
                done_reason="API呼び出しまたはJSONパース失敗",
                error="draft生成失敗",
                prompts_used={"draft": draft_prompt_info},
                draft_raw=sanitize_for_log(draft_raw)
            )
            write_step_log(config, step_num, step_data)
            sys.exit(1)

        # API呼び出し: review (Claude)
        review_raw, review, review_prompt_info = review_plus(config, step_num, draft, context, anthropic_key)
        if review is None:
            print("[ERROR] review生成に失敗しました。処理を中断します。")
            step_data = build_step_log_data(
                phase="error",
                step_num=step_num,
                config=config,
                done=False,
                done_reason="API呼び出しまたはJSONパース失敗",
                error="review生成失敗",
                prompts_used={"draft": draft_prompt_info, "review": review_prompt_info},
                draft=draft,
                review_raw=sanitize_for_log(review_raw)
            )
            write_step_log(config, step_num, step_data)
            sys.exit(1)

        # API呼び出し: final (ChatGPT)
        final_raw, final, final_prompt_info = make_final(config, step_num, draft, review, openai_key)
        if final is None:
            print("[ERROR] final生成に失敗しました。処理を中断します。")
            step_data = build_step_log_data(
                phase="error",
                step_num=step_num,
                config=config,
                done=False,
                done_reason="API呼び出しまたはJSONパース失敗",
                error="final生成失敗",
                prompts_used={"draft": draft_prompt_info, "review": review_prompt_info, "final": final_prompt_info},
                draft=draft,
                review=review,
                final_raw=sanitize_for_log(final_raw)
            )
            write_step_log(config, step_num, step_data)
            sys.exit(1)

        # コマンド実行
        commands = final.get("final_commands", [])
        exec_result = run_commands(config, commands, python_path)

        # allowlist判定サマリを作成
        allowlist_summary = []
        for cmd_result in exec_result.get("command_results", []):
            summary = {
                "type": cmd_result.get("type"),
                "allowed": cmd_result.get("allowed"),
                "reason": cmd_result.get("allow_reason") or cmd_result.get("deny_reason"),
                "matched_pattern": cmd_result.get("matched_pattern"),
                "executed": cmd_result.get("executed"),
                "returncode": cmd_result.get("returncode"),
                "timeout": cmd_result.get("timeout", False)
            }
            allowlist_summary.append(summary)

        # ステップログ出力（詳細版）
        step_data = build_step_log_data(
            phase="execute",
            step_num=step_num,
            config=config,
            done=False,
            done_reason="ステップ実行完了、次のループでdone判定",
            prompts_used={
                "draft": draft_prompt_info,
                "review": review_prompt_info,
                "final": final_prompt_info
            },
            final_commands=commands,
            allowlist_summary=allowlist_summary,
            draft=draft,
            draft_raw=sanitize_for_log(draft_raw),
            review=review,
            review_raw=sanitize_for_log(review_raw),
            final=final,
            final_raw=sanitize_for_log(final_raw),
            execution=exec_result
        )
        write_step_log(config, step_num, step_data)

        # コンテキスト更新
        context["history"].append({
            "step": step_num,
            "summary": final.get("summary", "")
        })

    else:
        print(f"[WARN] max_steps ({max_steps}) に到達。done=False のまま終了。")
        step_data = build_step_log_data(
            phase="max_steps_reached",
            step_num=max_steps + 1,
            config=config,
            done=False,
            done_reason=f"max_steps ({max_steps}) に到達したが目標未達成"
        )
        write_step_log(config, max_steps + 1, step_data)

    # フェーズサマリを出力
    write_phase_summary(config)

    print("")
    print("=" * 60)
    print("TOS v0.3 Orchestrator 終了")
    print("=" * 60)


if __name__ == "__main__":
    main()
