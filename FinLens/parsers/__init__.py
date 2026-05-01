# parsers模块
# PDF年报解析

"""
PDF解析模块负责从年报PDF中提取文本和表格数据。
支持多种PDF格式，自动识别财务报表。
"""

from .pdf_parser import PDFParser

__all__ = ["PDFParser"]
