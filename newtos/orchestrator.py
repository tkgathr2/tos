"""
NewTOS v1.0 オーケストレーター
中核ロジック
"""

import os
import logging
from typing import Optional, Tuple

from .models import JobStatus
from .constants import (
    RUN_0, RUN_1, RUN_GOALS, RUN_RESULT_GO, RUN_RESULT_STOP,
    STOP_CODE_SPEC_MISSING, STOP_CODE_ACCEPTANCE_AMBIGUOUS,
    STOP_STATUS_ACTIVE, STOP_STATUS_RESOLVED, STOP_STATUS_NONE,
    DECISION_YES, DECISION_NO, DECISION_1, DECISION_2,
    DECISION_RESUME, DECISION_FAILED
)
from .storage import (
    save_job_status, load_job_status, read_spec_file,
    read_human_decision, ensure_job_dir, write_stop_report
)
from .slack import send_stop_notification, send_resume_notification
from .run0_audit import audit_spec

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("newtos")


class Orchestrator:
    """NewTOS オーケストレーター"""

    def __init__(self, job_dir: str, spec_path: str):
        self.job_dir = os.path.abspath(job_dir)
        self.spec_path = os.path.abspath(spec_path)
        self.status: Optional[JobStatus] = None

    def initialize(self) -> JobStatus:
        """ジョブを初期化"""
        ensure_job_dir(self.job_dir)

        # 既存のステータスがあれば読み込む
        existing = load_job_status(self.job_dir)
        if existing:
            logger.info(f"Loaded existing job status: {existing.job_id}")
            self.status = existing
            return self.status

        # 新規作成
        job_id = os.path.basename(self.job_dir)
        self.status = JobStatus(
            job_id=job_id,
            current_run=RUN_0,
            run_goal=RUN_GOALS.get(RUN_0, ""),
            spec_path=self.spec_path
        )

        save_job_status(self.job_dir, self.status)
        logger.info(f"Created new job: {job_id}")

        return self.status

    def run(self) -> JobStatus:
        """メイン実行ループ"""
        if not self.status:
            self.initialize()

        # STOP状態の場合、human_decision を確認
        if self.status.stop.status == STOP_STATUS_ACTIVE:
            logger.info("Job is in STOP state, checking for human decision")
            decision = read_human_decision(self.job_dir)

            if decision:
                self._process_human_decision(decision)
            else:
                logger.info("No human decision found, remaining in STOP state")
                return self.status

        # STOP状態が解決されていない場合は終了
        if self.status.stop.status == STOP_STATUS_ACTIVE:
            return self.status

        # Run を実行
        if self.status.current_run == RUN_0:
            self._execute_run0()

        save_job_status(self.job_dir, self.status)
        return self.status

    def _execute_run0(self):
        """Run0 仕様監査を実行"""
        logger.info("Executing Run0: Spec Audit")
        self.status.progress.step_name = "spec_audit"
        self.status.run_goal = RUN_GOALS.get(RUN_0, "spec_audit")

        try:
            spec_content = read_spec_file(self.spec_path)
        except FileNotFoundError as e:
            self._set_stop(STOP_CODE_SPEC_MISSING, str(e))
            return

        # 仕様監査
        passed, missing, summary = audit_spec(spec_content)

        if not passed:
            self._set_stop(STOP_CODE_SPEC_MISSING, summary)
            return

        # Go
        logger.info(f"Run0 passed: {summary}")
        self.status.run_result = RUN_RESULT_GO
        self.status.next_run = RUN_1
        self.status.progress.step_name = "completed"

        # 次の Run はこのフェーズではスタブ
        logger.info("Run0 completed, next run would be run1 (not implemented in this phase)")

    def _set_stop(self, stop_code: str, summary: str):
        """STOP状態を設定し通知"""
        logger.info(f"STOP: {stop_code} - {summary}")
        self.status.set_stop(stop_code, summary)

        save_job_status(self.job_dir, self.status)

        # Slack通知
        success, message = send_stop_notification(self.status)
        logger.info(message)

    def _process_human_decision(self, decision: str):
        """human_decision を処理"""
        decision = decision.strip().upper()

        # 正規化
        if decision in [DECISION_YES.upper(), DECISION_1]:
            self._resume()
        elif decision in [DECISION_NO.upper(), DECISION_2]:
            self._fail()
        else:
            # 不正な値
            logger.info(f"Invalid human decision value: {decision}")
            self.status.set_stop(
                STOP_CODE_ACCEPTANCE_AMBIGUOUS,
                f"Invalid decision value: {decision}. Expected Yes/No or 1/2"
            )
            save_job_status(self.job_dir, self.status)

    def _resume(self):
        """RESUME処理"""
        logger.info("Human decision: RESUME")

        self.status.add_decision_transition(
            summary="Human approved to continue",
            by="human",
            target=self.status.stop.stop_code or "unknown",
            outcome=DECISION_RESUME
        )
        self.status.resolve_stop()
        self.status.run_result = RUN_RESULT_GO

        save_job_status(self.job_dir, self.status)

        success, message = send_resume_notification(self.status)
        logger.info(message)

    def _fail(self):
        """失敗終端処理"""
        logger.info("Human decision: FAILED (rejected)")

        self.status.add_decision_transition(
            summary="Human rejected, marking as failed",
            by="human",
            target=self.status.stop.stop_code or "unknown",
            outcome=DECISION_FAILED
        )

        self.status.run_result = "FAILED"
        self.status.stop.status = "terminal"

        save_job_status(self.job_dir, self.status)

        # 停止レポート出力
        report_path = write_stop_report(self.job_dir, self.status)
        logger.info(f"Stop report written: {report_path}")


def run_job(job_dir: str, spec_path: str) -> JobStatus:
    """ジョブを実行するエントリポイント"""
    orchestrator = Orchestrator(job_dir, spec_path)
    orchestrator.initialize()
    return orchestrator.run()
