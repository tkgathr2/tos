"""
NewTOS v1.0 データモデル
job_status.json の型定義と入出力
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class StopInfo:
    """STOP状態の情報"""
    status: str = "none"  # none, active, resolved
    stop_code: Optional[str] = None
    summary: Optional[str] = None


@dataclass
class Progress:
    """進捗情報"""
    step_name: str = ""
    step_index: int = 0
    total_steps: int = 0


@dataclass
class DecisionTransition:
    """判断遷移記録"""
    decision_summary: str = ""
    decision_by: str = ""  # human, system
    decision_target: str = ""  # stop_code or run name
    outcome: str = ""  # RESUME, FAILED
    timestamp: str = ""


@dataclass
class JobStatus:
    """job_status.json の全体構造"""
    job_id: str
    updated_at: str = ""
    current_run: str = "run0"
    run_goal: str = ""
    run_result: str = "not_started"
    next_run: Optional[str] = None
    progress: Progress = field(default_factory=Progress)
    stop: StopInfo = field(default_factory=StopInfo)
    decision_transitions: List[Dict[str, Any]] = field(default_factory=list)
    spec_path: str = ""
    created_at: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = now
        if not self.created_at:
            self.created_at = now

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = {
            "job_id": self.job_id,
            "updated_at": self.updated_at,
            "created_at": self.created_at,
            "current_run": self.current_run,
            "run_goal": self.run_goal,
            "run_result": self.run_result,
            "next_run": self.next_run,
            "progress": {
                "step_name": self.progress.step_name,
                "step_index": self.progress.step_index,
                "total_steps": self.progress.total_steps
            },
            "stop": {
                "status": self.stop.status,
                "stop_code": self.stop.stop_code,
                "summary": self.stop.summary
            },
            "decision_transitions": self.decision_transitions,
            "spec_path": self.spec_path
        }
        return data

    def update_timestamp(self):
        """updated_at を現在時刻に更新"""
        self.updated_at = datetime.now().isoformat()

    def set_stop(self, stop_code: str, summary: str):
        """STOP状態を設定"""
        self.stop.status = "active"
        self.stop.stop_code = stop_code
        self.stop.summary = summary
        self.run_result = "STOP"
        self.update_timestamp()

    def resolve_stop(self):
        """STOP状態を解決"""
        self.stop.status = "resolved"
        self.update_timestamp()

    def add_decision_transition(self, summary: str, by: str, target: str, outcome: str):
        """判断遷移を追加"""
        transition = {
            "decision_summary": summary,
            "decision_by": by,
            "decision_target": target,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        }
        self.decision_transitions.append(transition)
        self.update_timestamp()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobStatus":
        """辞書からJobStatusを生成"""
        progress_data = data.get("progress", {})
        stop_data = data.get("stop", {})

        progress = Progress(
            step_name=progress_data.get("step_name", ""),
            step_index=progress_data.get("step_index", 0),
            total_steps=progress_data.get("total_steps", 0)
        )

        stop = StopInfo(
            status=stop_data.get("status", "none"),
            stop_code=stop_data.get("stop_code"),
            summary=stop_data.get("summary")
        )

        return cls(
            job_id=data.get("job_id", ""),
            updated_at=data.get("updated_at", ""),
            created_at=data.get("created_at", ""),
            current_run=data.get("current_run", "run0"),
            run_goal=data.get("run_goal", ""),
            run_result=data.get("run_result", "not_started"),
            next_run=data.get("next_run"),
            progress=progress,
            stop=stop,
            decision_transitions=data.get("decision_transitions", []),
            spec_path=data.get("spec_path", "")
        )
