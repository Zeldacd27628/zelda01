# agent模块
# Agent工作流调度和提示词模板

"""
Agent模块包含FinLens的核心工作流调度逻辑和提示词模板。
利用MiMo-V2.5-Pro的100万Token上下文进行深度财务分析。
"""

from .workflow import FinLensWorkflow
from .prompts import (
    SYSTEM_PROMPT,
    ANALYSIS_PROMPT,
    MANIPULATION_DETECTION_PROMPT,
    RISK_ASSESSMENT_PROMPT,
    INDUSTRY_COMPARISON_PROMPT,
    FINAL_REPORT_PROMPT,
    QA_PROMPT
)

__all__ = [
    "FinLensWorkflow",
    "SYSTEM_PROMPT",
    "ANALYSIS_PROMPT", 
    "MANIPULATION_DETECTION_PROMPT",
    "RISK_ASSESSMENT_PROMPT",
    "INDUSTRY_COMPARISON_PROMPT",
    "FINAL_REPORT_PROMPT",
    "QA_PROMPT"
]
