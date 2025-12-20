"""
NewTOS v1.0 CLI
コマンドライン入口
"""

import argparse
import sys
import os
import json

from .orchestrator import run_job


def main():
    """CLI エントリポイント"""
    parser = argparse.ArgumentParser(
        prog="newtos",
        description="NewTOS v1.0 - Task Orchestration System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # run コマンド
    run_parser = subparsers.add_parser("run", help="Run a job")
    run_parser.add_argument(
        "--job",
        required=True,
        help="Path to job directory"
    )
    run_parser.add_argument(
        "--spec",
        required=True,
        help="Path to spec file (Spec A)"
    )
    run_parser.add_argument(
        "--run",
        default="run0",
        help="Starting run (default: run0)"
    )

    # status コマンド
    status_parser = subparsers.add_parser("status", help="Show job status")
    status_parser.add_argument(
        "--job",
        required=True,
        help="Path to job directory"
    )

    args = parser.parse_args()

    if args.command == "run":
        execute_run(args)
    elif args.command == "status":
        show_status(args)
    else:
        parser.print_help()
        sys.exit(1)


def execute_run(args):
    """run コマンドを実行"""
    job_dir = os.path.abspath(args.job)
    spec_path = os.path.abspath(args.spec)

    # 仕様ファイル存在確認
    if not os.path.exists(spec_path):
        print(f"Error: Spec file not found: {spec_path}")
        sys.exit(1)

    print(f"Starting NewTOS job")
    print(f"  Job directory: {job_dir}")
    print(f"  Spec file: {spec_path}")
    print()

    try:
        status = run_job(job_dir, spec_path)

        print()
        print("Job execution completed")
        print(f"  Job ID: {status.job_id}")
        print(f"  Current Run: {status.current_run}")
        print(f"  Run Result: {status.run_result}")
        print(f"  Stop Status: {status.stop.status}")

        if status.stop.stop_code:
            print(f"  Stop Code: {status.stop.stop_code}")
            print(f"  Stop Summary: {status.stop.summary}")

        if status.next_run:
            print(f"  Next Run: {status.next_run}")

        status_file = os.path.join(job_dir, "job_status.json")
        print(f"  Status file: {status_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def show_status(args):
    """status コマンドを実行"""
    job_dir = os.path.abspath(args.job)
    status_file = os.path.join(job_dir, "job_status.json")

    if not os.path.exists(status_file):
        print(f"Error: No job_status.json found in {job_dir}")
        sys.exit(1)

    with open(status_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
