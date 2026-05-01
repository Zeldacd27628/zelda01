# PDF解析模块
# 年报PDF文本和表格提取

"""
PDF年报解析器，支持从A股年报PDF中提取：
1. 完整文本内容（用于LLM深度分析）
2. 结构化财务报表数据（资产负债表、利润表、现金流量表）
3. 关键附注信息
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field

# PDF解析库
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("警告: PyMuPDF未安装，部分功能可能受限")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("警告: pdfplumber未安装，表格提取可能受限")

from utils.helpers import setup_logging, clean_text, parse_financial_number

logger = setup_logging()


@dataclass
class FinancialTable:
    """财务报表数据结构"""
    table_type: str  # 'balance_sheet', 'income_statement', 'cash_flow', 'other'
    year: str
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PDFParseResult:
    """PDF解析结果"""
    full_text: str
    financial_tables: Dict[str, List[FinancialTable]]
    metadata: Dict[str, Any]
    page_count: int
    extraction_stats: Dict[str, int]


class PDFParser:
    """
    PDF年报解析器
    
    功能：
    1. 提取完整文本（用于LLM分析）
    2. 提取财务报表表格
    3. 识别关键章节和附注
    """
    
    def __init__(self):
        """初始化解析器"""
        self.text_encoding = "utf-8"
        
        # 财务报表表头模式（识别不同格式）
        self.balance_sheet_patterns = [
            r"资产负债表",
            r"合并资产负债表",
            r"公司资产负债表",
            r"BALANCE\s*SHEET",
        ]
        
        self.income_statement_patterns = [
            r"利润表",
            r"合并利润表",
            r"公司利润表",
            r"损益表",
            r"INCOME\s*STATEMENT",
            r"PROFIT\s*AND\s*LOSS",
        ]
        
        self.cash_flow_patterns = [
            r"现金流量表",
            r"合并现金流量表",
            r"公司现金流量表",
            r"CASH\s*FLOW",
        ]
        
        # 财务指标正则模式
        self.financial_item_patterns = {
            # 资产负债表项目
            "total_assets": [r"资产总计", r"总资产"],
            "current_assets": [r"流动资产合计"],
            "fixed_assets": [r"固定资产合计"],
            "intangible_assets": [r"无形资产", r"无形资产及长期待摊费用"],
            "goodwill": [r"商誉"],
            "accounts_receivable": [r"应收账款"],
            "other_receivables": [r"其他应收款"],
            "inventory": [r"存货"],
            "prepaid_expenses": [r"预付款项", r"预付账款"],
            "total_liabilities": [r"负债合计", r"总负债"],
            "current_liabilities": [r"流动负债合计"],
            "long_term_liabilities": [r"非流动负债合计", r"长期负债"],
            "accounts_payable": [r"应付账款"],
            "other_payables": [r"其他应付款"],
            "total_equity": [r"所有者权益合计", r"股东权益合计", r"归属母公司股东权益"],
            
            # 利润表项目
            "revenue": [r"营业收入", r"营业总收入"],
            "operating_cost": [r"营业成本"],
            "gross_profit": [r"毛利", r"毛利润"],
            "operating_expense": [r"营业费用", r"销售费用", r"管理费用", r"财务费用"],
            "operating_profit": [r"营业利润", r"营业利润"],
            "total_profit": [r"利润总额"],
            "net_profit": [r"净利润", r"归属于母公司所有者的净利润"],
            "rd_expense": [r"研发费用"],
            
            # 现金流量表项目
            "operating_cash_flow": [r"经营活动产生的现金流量净额", r"经营活动现金净流量"],
            "investing_cash_flow": [r"投资活动产生的现金流量净额", r"投资活动现金净流量"],
            "financing_cash_flow": [r"筹资活动产生的现金流量净额", r"筹资活动现金净流量"],
            "cash_equivalents": [r"期末现金及现金等价物余额", r"现金及现金等价物净增加额"],
            
            # 附注项目
            "related_party_transaction": [r"关联交易", r"关联方交易"],
            "accounting_policy_change": [r"会计政策变更", r"会计估计变更"],
            "audit_opinion": [r"审计意见", r"审计报告"],
        }
    
    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            包含full_text和financial_tables的字典
        """
        path = Path(pdf_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        logger.info(f"开始解析PDF: {pdf_path}")
        
        # 使用PyMuPDF提取文本
        if PYMUPDF_AVAILABLE:
            full_text = self._extract_text_pymupdf(pdf_path)
        else:
            full_text = self._extract_text_basic(pdf_path)
        
        # 使用pdfplumber提取表格
        if PDFPLUMBER_AVAILABLE:
            financial_tables = self._extract_tables_pdfplumber(pdf_path)
        else:
            financial_tables = self._extract_tables_from_text(full_text)
        
        # 合并表格数据
        merged_tables = self._merge_financial_tables(financial_tables)
        
        # 提取元数据
        metadata = self._extract_metadata(full_text)
        
        logger.info(f"PDF解析完成: {len(full_text)} 字符, {len(merged_tables)} 个表格")
        
        return {
            "full_text": full_text,
            "financial_tables": merged_tables,
            "metadata": metadata,
            "page_count": metadata.get("page_count", 0),
            "extraction_stats": {
                "text_length": len(full_text),
                "table_count": len(merged_tables),
                "page_count": metadata.get("page_count", 0)
            }
        }
    
    def _extract_text_pymupdf(self, pdf_path: str) -> str:
        """使用PyMuPDF提取文本"""
        text_parts = []
        
        try:
            with fitz.open(pdf_path) as doc:
                page_count = len(doc)
                logger.info(f"PDF共 {page_count} 页")
                
                for page_num, page in enumerate(doc):
                    # 提取页面文本
                    text = page.get_text("text")
                    
                    # 清理文本
                    text = clean_text(text)
                    
                    # 添加页码标记（便于追踪）
                    text_parts.append(f"\n\n=== 第 {page_num + 1} 页 ===\n\n")
                    text_parts.append(text)
                    
                    # 进度显示
                    if (page_num + 1) % 20 == 0:
                        logger.info(f"已处理 {page_num + 1}/{page_count} 页")
                
                full_text = "\n".join(text_parts)
                
        except Exception as e:
            logger.error(f"PyMuPDF解析失败: {e}")
            raise
        
        return full_text
    
    def _extract_text_basic(self, pdf_path: str) -> str:
        """基础文本提取（当PyMuPDF不可用时）"""
        logger.warning("使用基础文本提取，可能丢失部分格式信息")
        
        try:
            import subprocess
            
            # 尝试使用pdftotext
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return clean_text(result.stdout)
            else:
                raise Exception("pdftotext不可用")
                
        except Exception as e:
            logger.error(f"基础文本提取失败: {e}")
            raise
    
    def _extract_tables_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """使用pdfplumber提取表格"""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # 提取表格
                    page_tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            # 确定表格类型
                            table_type = self._identify_table_type(table)
                            
                            if table_type:
                                tables.append({
                                    "page": page_num + 1,
                                    "index": table_idx,
                                    "type": table_type,
                                    "data": table
                                })
        except Exception as e:
            logger.error(f"pdfplumber表格提取失败: {e}")
        
        return tables
    
    def _extract_tables_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从纯文本中提取表格数据"""
        tables = []
        
        # 简单的表格识别逻辑
        lines = text.split("\n")
        
        for i, line in enumerate(lines):
            # 检查是否是表格标题行
            if any(pattern in line for pattern in 
                   self.balance_sheet_patterns + self.income_statement_patterns + self.cash_flow_patterns):
                # 尝试提取后续的表格内容
                table_data = []
                for j in range(i+1, min(i+50, len(lines))):
                    line = lines[j].strip()
                    if line and self._looks_like_table_row(line):
                        cells = self._parse_table_row(line)
                        if cells:
                            table_data.append(cells)
                
                if table_data:
                    table_type = self._identify_table_type_from_text(table_data)
                    tables.append({
                        "page": 0,
                        "index": len(tables),
                        "type": table_type,
                        "data": table_data
                    })
        
        return tables
    
    def _identify_table_type(self, table: List[List[str]]) -> Optional[str]:
        """识别表格类型"""
        if not table or len(table) < 2:
            return None
        
        # 检查表头
        header = " ".join(str(cell).lower() for cell in table[0] if cell)
        
        for pattern in self.balance_sheet_patterns:
            if re.search(pattern, header, re.IGNORECASE):
                return "balance_sheet"
        
        for pattern in self.income_statement_patterns:
            if re.search(pattern, header, re.IGNORECASE):
                return "income_statement"
        
        for pattern in self.cash_flow_patterns:
            if re.search(pattern, header, re.IGNORECASE):
                return "cash_flow"
        
        # 检查内容行关键词
        for row in table[:5]:
            row_text = " ".join(str(cell).lower() for cell in row if cell)
            
            if any(kw in row_text for kw in ["货币资金", "应收账款", "存货", "资产总计"]):
                return "balance_sheet"
            if any(kw in row_text for kw in ["营业收入", "净利润", "利润总额"]):
                return "income_statement"
            if any(kw in row_text for kw in ["经营活动", "投资活动", "筹资活动", "现金"]):
                return "cash_flow"
        
        return None
    
    def _identify_table_type_from_text(self, table_data: List[List[str]]) -> Optional[str]:
        """从文本数据识别表格类型"""
        if not table_data:
            return None
        
        all_text = " ".join(" ".join(row) for row in table_data).lower()
        
        for pattern in self.balance_sheet_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                return "balance_sheet"
        
        for pattern in self.income_statement_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                return "income_statement"
        
        for pattern in self.cash_flow_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                return "cash_flow"
        
        return "other"
    
    def _looks_like_table_row(self, line: str) -> bool:
        """判断行是否像表格行"""
        # 表格行通常包含数字和分隔符
        return bool(re.search(r"\d+[,\.\d]*", line)) and len(line) > 10
    
    def _parse_table_row(self, line: str) -> Optional[List[str]]:
        """解析表格行"""
        # 尝试多种分隔符
        for sep in ["\t", "  ", " | ", "|"]:
            if sep in line:
                cells = [cell.strip() for cell in line.split(sep)]
                if len(cells) >= 2:
                    return cells
        
        # 尝试按固定宽度分割
        return None
    
    def _merge_financial_tables(self, tables: List[Dict[str, Any]]) -> Dict[str, List]:
        """合并同类表格"""
        result = {
            "balance_sheet": [],
            "income_statement": [],
            "cash_flow": [],
            "other": []
        }
        
        for table in tables:
            table_type = table.get("type", "other")
            if table_type in result:
                result[table_type].append(table)
            else:
                result["other"].append(table)
        
        return result
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """提取PDF元数据"""
        metadata = {
            "page_count": text.count("=== 第") if "=== 第" in text else 0
        }
        
        # 提取公司名称
        company_match = re.search(r"^(.+?)(?:股份有限公司|有限公司)", text[:500])
        if company_match:
            metadata["company_name"] = company_match.group(1).strip()
        
        # 提取报告期
        year_match = re.search(r"20\d{2}年度?", text[:1000])
        if year_match:
            metadata["report_year"] = year_match.group(0)
        
        # 提取报告类型
        if "年度报告" in text[:1000]:
            metadata["report_type"] = "年度报告"
        elif "中期报告" in text[:1000]:
            metadata["report_type"] = "中期报告"
        
        return metadata
    
    def extract_financial_data(self, tables: Dict[str, List]) -> Dict[str, Any]:
        """
        从表格中提取结构化财务数据
        
        用于后续的财务指标计算
        """
        financial_data = {}
        
        # 处理资产负债表
        for table in tables.get("balance_sheet", []):
            data = table.get("data", [])
            if data:
                parsed = self._parse_financial_table(data)
                financial_data.update(parsed)
        
        # 处理利润表
        for table in tables.get("income_statement", []):
            data = table.get("data", [])
            if data:
                parsed = self._parse_financial_table(data)
                financial_data.update(parsed)
        
        # 处理现金流量表
        for table in tables.get("cash_flow", []):
            data = table.get("data", [])
            if data:
                parsed = self._parse_financial_table(data)
                financial_data.update(parsed)
        
        return financial_data
    
    def _parse_financial_table(self, table_data: List[List[str]]) -> Dict[str, Any]:
        """解析财务表格，提取关键数据"""
        result = {}
        
        for row in table_data:
            if not row or len(row) < 2:
                continue
            
            # 第一列通常是科目名称
            item_name = str(row[0]).strip()
            
            # 查找对应的英文键名
            for key, patterns in self.financial_item_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, item_name, re.IGNORECASE):
                        # 后续列通常是数值
                        for col_idx in range(1, len(row)):
                            value_str = str(row[col_idx]).strip()
                            value = parse_financial_number(value_str)
                            
                            if value is not None:
                                col_key = f"{key}_{col_idx}" if col_idx > 1 else key
                                result[col_key] = value
                        
                        break
        
        return result
    
    def get_full_text(self, pdf_path: str) -> str:
        """
        获取PDF完整文本（便捷方法）
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            完整文本内容
        """
        result = self.parse(pdf_path)
        return result["full_text"]
    
    def get_financial_summary(self, pdf_path: str) -> Dict[str, Any]:
        """
        获取财务数据摘要（便捷方法）
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            包含主要财务数据的字典
        """
        result = self.parse(pdf_path)
        financial_data = self.extract_financial_data(result["financial_tables"])
        
        return {
            "metadata": result["metadata"],
            "financial_data": financial_data,
            "table_count": len(result["financial_tables"])
        }
