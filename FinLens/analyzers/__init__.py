# analyzers模块
# 财务分析器

"""
财务分析模块包含：
1. financial.py - 财务指标计算
2. detection.py - 会计操纵检测
3. comparison.py - 行业对比
"""

from .financial import FinancialAnalyzer
from .detection import ManipulationDetector
from .comparison import IndustryComparator

__all__ = [
    "FinancialAnalyzer",
    "ManipulationDetector",
    "IndustryComparator"
]
