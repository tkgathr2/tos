"""
NewTOS v1.0 ストレージ
ファイル保存と読み込み
"""

import json
import os
from typing import Optional
from .models import JobStatus
from .constants import JOB_STATUS_FILE, HUMAN_DECISION_FILE


def save_job_status(job_dir: str, status: JobStatus) -> str:
    """job_status.json を保存"""
    status.update_timestamp()
    file_path = os.path.join(job_dir, JOB_STATUS_FILE)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(status.to_dict(), f, ensure_ascii=False, indent=2)

    return file_path


def load_job_status(job_dir: str) -> Optional[JobStatus]:
    """job_status.json を読み込み"""
    file_path = os.path.join(job_dir, JOB_STATUS_FILE)

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return JobStatus.from_dict(data)


def read_spec_file(spec_path: str) -> str:
    """仕様ファイルを読み込み"""
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Spec file not found: {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        return f.read()


def read_human_decision(job_dir: str) -> Optional[str]:
    """human_decision.txt を読み込み"""
    file_path = os.path.join(job_dir, HUMAN_DECISION_FILE)

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    return content if content else None


def ensure_job_dir(job_dir: str) -> bool:
    """ジョブディレクトリが存在することを確認"""
    if not os.path.exists(job_dir):
        os.makedirs(job_dir, exist_ok=True)
        return True
    return os.path.isdir(job_dir)


def write_stop_report(job_dir: str, status: JobStatus) -> str:
    """停止レポートを出力"""
    report_path = os.path.join(job_dir, "stop_report.txt")

    lines = [
        "NewTOS Stop Report",
        "=" * 40,
        f"Job ID: {status.job_id}",
        f"Updated: {status.updated_at}",
        f"Current Run: {status.current_run}",
        f"Run Goal: {status.run_goal}",
        f"Run Result: {status.run_result}",
        "",
        "Stop Information",
        "-" * 40,
        f"Status: {status.stop.status}",
        f"Stop Code: {status.stop.stop_code}",
        f"Summary: {status.stop.summary}",
        "",
        "Decision Transitions",
        "-" * 40
    ]

    for dt in status.decision_transitions:
        lines.append(f"  - {dt.get('timestamp', '')}: {dt.get('decision_summary', '')}")
        lines.append(f"    By: {dt.get('decision_by', '')}, Outcome: {dt.get('outcome', '')}")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path
