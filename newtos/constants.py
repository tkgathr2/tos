"""
NewTOS v1.0 定数定義
"""

# Stop codes
STOP_CODE_SPEC_MISSING = "SPEC_MISSING"
STOP_CODE_ACCEPTANCE_AMBIGUOUS = "ACCEPTANCE_AMBIGUOUS"
STOP_CODE_HUMAN_DECISION_REQUIRED = "HUMAN_DECISION_REQUIRED"
STOP_CODE_REJECTION = "REJECTION"

# Stop status
STOP_STATUS_ACTIVE = "active"
STOP_STATUS_RESOLVED = "resolved"
STOP_STATUS_NONE = "none"

# Run names
RUN_0 = "run0"
RUN_1 = "run1"
RUN_2 = "run2"
RUN_3 = "run3"

# Run goals
RUN_GOALS = {
    RUN_0: "spec_audit",
    RUN_1: "prototype",
    RUN_2: "full_build",
    RUN_3: "hardening"
}

# Run results
RUN_RESULT_GO = "Go"
RUN_RESULT_STOP = "STOP"
RUN_RESULT_PENDING = "pending"
RUN_RESULT_NOT_STARTED = "not_started"

# Decision values
DECISION_YES = "Yes"
DECISION_NO = "No"
DECISION_1 = "1"
DECISION_2 = "2"

# Decision outcomes
DECISION_RESUME = "RESUME"
DECISION_FAILED = "FAILED"

# Required spec sections
REQUIRED_SPEC_SECTIONS = [
    "purpose",
    "input",
    "output",
    "rules",
    "environment",
    "completion_criteria",
    "prohibited"
]

# Spec section aliases (Japanese and English)
SPEC_SECTION_ALIASES = {
    "purpose": ["purpose", "目的"],
    "input": ["input", "入力"],
    "output": ["output", "出力"],
    "rules": ["rules", "ルール"],
    "environment": ["environment", "環境"],
    "completion_criteria": ["completion_criteria", "完成条件"],
    "prohibited": ["prohibited", "禁止"]
}

# Job status file name
JOB_STATUS_FILE = "job_status.json"
HUMAN_DECISION_FILE = "human_decision.txt"
