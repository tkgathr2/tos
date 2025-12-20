"""
NewTOS v1.0 Slack通知
Webhook による通知送信
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional
from .models import JobStatus


def get_webhook_url() -> Optional[str]:
    """Slack Webhook URL を取得"""
    # 環境変数から取得
    url = os.environ.get("NEWTOS_SLACK_WEBHOOK_URL")
    if url:
        return url

    # 設定ファイルから取得を試みる
    config_paths = [
        os.path.join(os.path.dirname(__file__), "..", "config_v0_3.json"),
        os.path.join(os.path.dirname(__file__), "..", "newtos_config.json")
    ]

    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    url = config.get("slack_webhook_url") or config.get("slack", {}).get("webhook_url")
                    if url:
                        return url
            except (json.JSONDecodeError, IOError):
                continue

    return None


def send_stop_notification(status: JobStatus) -> tuple[bool, str]:
    """STOP通知をSlackに送信

    Returns:
        tuple[bool, str]: (成功したか, メッセージ)
    """
    webhook_url = get_webhook_url()

    if not webhook_url:
        return False, "Slack Webhook URL is not configured, skipping notification"

    message = build_stop_message(status)

    try:
        data = json.dumps({"text": message}).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Slack notification sent successfully"
            else:
                return False, f"Slack notification failed with status {response.status}"

    except urllib.error.URLError as e:
        return False, f"Slack notification failed: {str(e)}"
    except Exception as e:
        return False, f"Slack notification error: {str(e)}"


def build_stop_message(status: JobStatus) -> str:
    """STOP通知メッセージを構築"""
    lines = [
        "NewTOS STOP Notification",
        "",
        f"Job ID: {status.job_id}",
        f"Current Run: {status.current_run}",
        f"Stop Code: {status.stop.stop_code}",
        f"Summary: {status.stop.summary}",
        "",
        "Please respond with Yes/No or 1/2"
    ]

    return "\n".join(lines)


def send_resume_notification(status: JobStatus) -> tuple[bool, str]:
    """RESUME通知をSlackに送信"""
    webhook_url = get_webhook_url()

    if not webhook_url:
        return False, "Slack Webhook URL is not configured, skipping notification"

    message = f"NewTOS RESUME\n\nJob ID: {status.job_id}\nRun: {status.current_run}\nStatus: Resumed by human decision"

    try:
        data = json.dumps({"text": message}).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Resume notification sent"
            else:
                return False, f"Notification failed with status {response.status}"

    except Exception as e:
        return False, f"Notification error: {str(e)}"
