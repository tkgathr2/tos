"""
NewTOS v1.0 Run0 仕様監査
仕様ファイルの最小チェック
"""

import re
from typing import List, Tuple
from .constants import REQUIRED_SPEC_SECTIONS, SPEC_SECTION_ALIASES


def audit_spec(spec_content: str) -> Tuple[bool, List[str], str]:
    """仕様ファイルを監査

    Args:
        spec_content: 仕様ファイルの内容

    Returns:
        tuple[bool, List[str], str]: (合格したか, 不足セクション, サマリ)
    """
    missing_sections = []

    for section in REQUIRED_SPEC_SECTIONS:
        aliases = SPEC_SECTION_ALIASES.get(section, [section])
        found = False

        for alias in aliases:
            # 見出し形式をチェック (# heading, ## heading, heading:, heading など)
            patterns = [
                rf"^#+\s*{re.escape(alias)}\s*$",  # Markdown heading
                rf"^{re.escape(alias)}\s*[:：]",    # Label with colon
                rf"^\[{re.escape(alias)}\]",        # Bracketed label
                rf"^{re.escape(alias)}\s*$",        # Plain label on its own line
            ]

            for pattern in patterns:
                if re.search(pattern, spec_content, re.MULTILINE | re.IGNORECASE):
                    found = True
                    break

            if found:
                break

        if not found:
            missing_sections.append(section)

    if missing_sections:
        summary = f"Missing required sections: {', '.join(missing_sections)}"
        return False, missing_sections, summary
    else:
        summary = "All required sections found"
        return True, [], summary


def get_required_sections() -> List[str]:
    """必須セクションのリストを取得"""
    return REQUIRED_SPEC_SECTIONS.copy()


def get_section_aliases() -> dict:
    """セクションエイリアスを取得"""
    return SPEC_SECTION_ALIASES.copy()
