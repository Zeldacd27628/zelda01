# 财务指标计算模块
# 盈利能力、偿债能力、运营效率、成长性、现金流分析

"""
财务指标计算器，从财务报表数据中计算各类财务指标。
支持A股上市公司年报的标准化分析。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from utils.helpers import setup_logging, safe_divide, parse_financial_number

logger = setup_logging()


@dataclass
class FinancialMetrics:
    """财务指标数据结构"""
    # 盈利能力
    gross_margin: float = 0.0           # 毛利率
    net_margin: float = 0.0            # 净利率
    roe: float = 0.0                   # 净资产收益率
    roa: float = 0.0                   # 总资产收益率
    eps: float = 0.0                   # 每股收益
    
    # 偿债能力
    debt_ratio: float = 0.0            # 资产负债率
    current_ratio: float = 0.0         # 流动比率
    quick_ratio: float = 0.0           # 速动比率
    
    # 运营效率
    inventory_turnover: float = 0.0    # 存货周转率
    receivable_turnover: float = 0.0   # 应收账款周转率
    total_asset_turnover: float = 0.0  # 总资产周转率
    
    # 成长性
    revenue_growth: float = 0.0        # 营收增长率
    profit_growth: float = 0.0         # 利润增长率
    asset_growth: float = 0.0          # 资产增长率
    
    # 现金流
    cash_flow_ratio: float = 0.0       # 经营现金流/净利润
    cash_coverage: float = 0.0         # 现金流利息保障倍数
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "gross_margin": self.gross_margin,
            "net_margin": self.net_margin,
            "roe": self.roe,
            "roa": self.roa,
            "eps": self.eps,
            "debt_ratio": self.debt_ratio,
            "current_ratio": self.current_ratio,
            "quick_ratio": self.quick_ratio,
            "inventory_turnover": self.inventory_turnover,
            "receivable_turnover": self.receivable_turnover,
            "total_asset_turnover": self.total_asset_turnover,
            "revenue_growth": self.revenue_growth,
            "profit_growth": self.profit_growth,
            "asset_growth": self.asset_growth,
            "cash_flow_ratio": self.cash_flow_ratio,
            "cash_coverage": self.cash_coverage,
        }


class FinancialAnalyzer:
    """
    财务指标计算器
    
    计算A股上市公司年报中的各类财务指标。
    """
    
    def __init__(self):
        """初始化分析器"""
        self.metrics = FinancialMetrics()
    
    def analyze(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析财务数据，计算所有指标
        
        Args:
            financial_data: 从PDF提取的结构化财务数据
        
        Returns:
            包含所有财务指标的字典
        """
        logger.info("开始计算财务指标...")
        
        # 提取关键财务数据
        balance_sheet = financial_data.get("balance_sheet", [{}])[0].get("data", []) if financial_data.get("balance_sheet") else []
        income_statement = financial_data.get("income_statement", [{}])[0].get("data", []) if financial_data.get("income_statement") else []
        cash_flow = financial_data.get("cash_flow", [{}])[0].get("data", []) if financial_data.get("cash_flow") else []
        
        # 解析财务数据
        bs = self._parse_balance_sheet(balance_sheet)
        is_ = self._parse_income_statement(income_statement)
        cf = self._parse_cash_flow(cash_flow)
        
        # 计算各类指标
        profitability = self._calculate_profitability(is_)
        solvency = self._calculate_solvency(bs)
        efficiency = self._calculate_efficiency(bs, is_)
        growth = self._calculate_growth(bs, is_)
        cash_flow_metrics = self._calculate_cash_flow_metrics(is_, cf)
        
        # 合并结果
        result = {
            "profitability": profitability,
            "solvency": solvency,
            "efficiency": efficiency,
            "growth": growth,
            "cash_flow": cash_flow_metrics,
            **profitability,
            **solvency,
            **efficiency,
            **growth,
            **cash_flow_metrics
        }
        
        logger.info(f"财务指标计算完成: {len(result)} 项指标")
        
        return result
    
    def _parse_balance_sheet(self, data: List[List[str]]) -> Dict[str, float]:
        """解析资产负债表"""
        parsed = {}
        
        for row in data:
            if not row or len(row) < 2:
                continue
            
            item = str(row[0]).strip().lower()
            value = self._extract_value(row[1] if len(row) > 1 else "")
            
            # 资产类
            if any(kw in item for kw in ["总资产", "资产总计"]):
                parsed["total_assets"] = value
            elif "流动资产" in item:
                parsed["current_assets"] = value
            elif "固定资产" in item:
                parsed["fixed_assets"] = value
            elif "应收账款" in item and "其他" not in item:
                parsed["accounts_receivable"] = value
            elif "其他应收款" in item:
                parsed["other_receivables"] = value
            elif "存货" in item:
                parsed["inventory"] = value
            elif "预付款项" in item:
                parsed["prepaid_expenses"] = value
            elif "商誉" in item:
                parsed["goodwill"] = value
            elif "无形资产" in item:
                parsed["intangible_assets"] = value
            
            # 负债类
            if any(kw in item for kw in ["总负债", "负债合计"]):
                parsed["total_liabilities"] = value
            elif "流动负债" in item:
                parsed["current_liabilities"] = value
            elif "应付账款" in item and "其他" not in item:
                parsed["accounts_payable"] = value
            elif "其他应付款" in item:
                parsed["other_payables"] = value
            elif "短期借款" in item:
                parsed["short_term_borrowings"] = value
            elif "长期借款" in item:
                parsed["long_term_borrowings"] = value
            
            # 权益类
            if any(kw in item for kw in ["所有者权益", "股东权益", "归属母公司"]):
                parsed["total_equity"] = value
            elif "股本" in item:
                parsed["share_capital"] = value
        
        return parsed
    
    def _parse_income_statement(self, data: List[List[str]]) -> Dict[str, float]:
        """解析利润表"""
        parsed = {}
        
        for row in data:
            if not row or len(row) < 2:
                continue
            
            item = str(row[0]).strip().lower()
            value = self._extract_value(row[1] if len(row) > 1 else "")
            
            if any(kw in item for kw in ["营业收入", "营业总收入", "营业总收入"]):
                parsed["revenue"] = value
            elif any(kw in item for kw in ["营业成本", "营业总成本"]):
                parsed["operating_cost"] = value
            elif "毛利" in item:
                parsed["gross_profit"] = value
            elif "销售费用" in item:
                parsed["selling_expense"] = value
            elif "管理费用" in item:
                parsed["admin_expense"] = value
            elif "财务费用" in item:
                parsed["finance_expense"] = value
            elif "研发费用" in item:
                parsed["rd_expense"] = value
            elif "营业利润" in item:
                parsed["operating_profit"] = value
            elif "利润总额" in item:
                parsed["total_profit"] = value
            elif any(kw in item for kw in ["净利润", "归属于母公司"]):
                if "parent" not in parsed and "母公司" in item:
                    parsed["net_profit_parent"] = value
                elif "parent" not in parsed:
                    parsed["net_profit"] = value
        
        return parsed
    
    def _parse_cash_flow(self, data: List[List[str]]) -> Dict[str, float]:
        """解析现金流量表"""
        parsed = {}
        
        for row in data:
            if not row or len(row) < 2:
                continue
            
            item = str(row[0]).strip().lower()
            value = self._extract_value(row[1] if len(row) > 1 else "")
            
            if "经营活动" in item and "现金流量净额" in item:
                parsed["operating_cash_flow"] = value
            elif "投资活动" in item and "现金流量净额" in item:
                parsed["investing_cash_flow"] = value
            elif "筹资活动" in item and "现金流量净额" in item:
                parsed["financing_cash_flow"] = value
            elif "现金及现金等价物" in item and "增加" in item:
                parsed["cash_increase"] = value
            elif "现金及现金等价物" in item and "期末" in item:
                parsed["ending_cash"] = value
        
        return parsed
    
    def _extract_value(self, cell: str) -> Optional[float]:
        """从单元格提取数值"""
        if not cell:
            return None
        
        return parse_financial_number(str(cell))
    
    def _calculate_profitability(self, is_data: Dict[str, float]) -> Dict[str, float]:
        """计算盈利能力指标"""
        result = {}
        
        revenue = is_data.get("revenue", 0)
        operating_cost = is_data.get("operating_cost", 0)
        gross_profit = is_data.get("gross_profit", 0)
        net_profit = is_data.get("net_profit", is_data.get("net_profit_parent", 0))
        operating_profit = is_data.get("operating_profit", 0)
        
        total_profit = is_data.get("total_profit", 0)
        
        # 毛利率 = (营收 - 营业成本) / 营收
        if revenue > 0:
            result["gross_margin"] = safe_divide(revenue - operating_cost, revenue) * 100
            result["net_margin"] = safe_divide(net_profit, revenue) * 100
        
        # 营业利润率
        if revenue > 0:
            result["operating_margin"] = safe_divide(operating_profit, revenue) * 100
        
        return result
    
    def _calculate_solvency(self, bs_data: Dict[str, float]) -> Dict[str, float]:
        """计算偿债能力指标"""
        result = {}
        
        total_assets = bs_data.get("total_assets", 0)
        total_liabilities = bs_data.get("total_liabilities", 0)
        current_assets = bs_data.get("current_assets", 0)
        current_liabilities = bs_data.get("current_liabilities", 0)
        
        # 资产负债率
        if total_assets > 0:
            result["debt_ratio"] = safe_divide(total_liabilities, total_assets) * 100
        
        # 流动比率
        if current_liabilities > 0:
            result["current_ratio"] = safe_divide(current_assets, current_liabilities)
        
        # 速动比率 (流动资产 - 存货) / 流动负债
        inventory = bs_data.get("inventory", 0)
        if current_liabilities > 0:
            quick_assets = current_assets - inventory
            result["quick_ratio"] = safe_divide(quick_assets, current_liabilities)
        
        return result
    
    def _calculate_efficiency(self, bs_data: Dict[str, float], is_data: Dict[str, float]) -> Dict[str, float]:
        """计算运营效率指标"""
        result = {}
        
        revenue = is_data.get("revenue", 0)
        operating_cost = is_data.get("operating_cost", 0)
        
        inventory = bs_data.get("inventory", 0)
        accounts_receivable = bs_data.get("accounts_receivable", 0)
        total_assets = bs_data.get("total_assets", 0)
        
        # 存货周转率 = 营业成本 / 平均存货
        if inventory > 0:
            result["inventory_turnover"] = safe_divide(operating_cost, inventory)
            result["inventory_days"] = safe_divide(365, result["inventory_turnover"])
        
        # 应收账款周转率 = 营收 / 平均应收账款
        if accounts_receivable > 0:
            result["receivable_turnover"] = safe_divide(revenue, accounts_receivable)
            result["receivable_days"] = safe_divide(365, result["receivable_turnover"])
        
        # 总资产周转率 = 营收 / 总资产
        if total_assets > 0:
            result["total_asset_turnover"] = safe_divide(revenue, total_assets)
        
        return result
    
    def _calculate_growth(self, bs_data: Dict[str, float], is_data: Dict[str, float]) -> Dict[str, float]:
        """计算成长性指标"""
        result = {}
        
        # 注意：这里需要两期数据对比计算增长率
        # 简化版本：假设传入的数据已经包含上期数据
        
        return result
    
    def _calculate_cash_flow_metrics(self, is_data: Dict[str, float], cf_data: Dict[str, float]) -> Dict[str, float]:
        """计算现金流指标"""
        result = {}
        
        net_profit = is_data.get("net_profit", is_data.get("net_profit_parent", 0))
        operating_cash_flow = cf_data.get("operating_cash_flow", 0)
        
        # 经营现金流/净利润
        if net_profit != 0:
            result["cash_flow_ratio"] = safe_divide(operating_cash_flow, net_profit)
        
        return result
    
    def calculate_comprehensive_metrics(
        self, 
        current_data: Dict[str, float],
        prior_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        计算综合财务指标（需要当期和上期数据）
        
        Args:
            current_data: 当期财务数据
            prior_data: 上期财务数据（可选）
        
        Returns:
            完整财务指标字典
        """
        metrics = {}
        
        # 基本指标计算
        revenue = current_data.get("revenue", 0)
        net_profit = current_data.get("net_profit", 0)
        total_assets = current_data.get("total_assets", 0)
        total_equity = current_data.get("total_equity", 0)
        
        # ROE = 净利润 / 净资产
        if total_equity > 0:
            metrics["roe"] = (net_profit / total_equity) * 100
        
        # ROA = 净利润 / 总资产
        if total_assets > 0:
            metrics["roa"] = (net_profit / total_assets) * 100
        
        # EPS = 净利润 / 股本（简化计算）
        share_capital = current_data.get("share_capital", 0)
        if share_capital > 0:
            metrics["eps"] = net_profit / share_capital
        
        # 成长性指标（需要上期数据）
        if prior_data:
            prior_revenue = prior_data.get("revenue", 0)
            prior_net_profit = prior_data.get("net_profit", 0)
            prior_total_assets = prior_data.get("total_assets", 0)
            
            if prior_revenue > 0:
                metrics["revenue_growth"] = ((revenue - prior_revenue) / prior_revenue) * 100
            
            if prior_net_profit > 0:
                metrics["profit_growth"] = ((net_profit - prior_net_profit) / prior_net_profit) * 100
            
            if prior_total_assets > 0:
                metrics["asset_growth"] = ((total_assets - prior_total_assets) / prior_total_assets) * 100
        
        return metrics
    
    def format_metrics_for_display(self, metrics: Dict[str, float]) -> str:
        """
        格式化指标用于显示
        
        Args:
            metrics: 财务指标字典
        
        Returns:
            格式化的字符串
        """
        lines = []
        
        lines.append("## 财务指标总览\n")
        
        # 盈利能力
        lines.append("### 盈利能力")
        lines.append(f"- 毛利率: {metrics.get('gross_margin', 0):.2f}%")
        lines.append(f"- 净利率: {metrics.get('net_margin', 0):.2f}%")
        lines.append(f"- ROE: {metrics.get('roe', 0):.2f}%")
        lines.append(f"- ROA: {metrics.get('roa', 0):.2f}%")
        lines.append("")
        
        # 偿债能力
        lines.append("### 偿债能力")
        lines.append(f"- 资产负债率: {metrics.get('debt_ratio', 0):.2f}%")
        lines.append(f"- 流动比率: {metrics.get('current_ratio', 0):.2f}")
        lines.append(f"- 速动比率: {metrics.get('quick_ratio', 0):.2f}")
        lines.append("")
        
        # 运营效率
        lines.append("### 运营效率")
        lines.append(f"- 存货周转率: {metrics.get('inventory_turnover', 0):.2f}")
        lines.append(f"- 应收账款周转率: {metrics.get('receivable_turnover', 0):.2f}")
        lines.append(f"- 总资产周转率: {metrics.get('total_asset_turnover', 0):.2f}")
        lines.append("")
        
        # 现金流
        lines.append("### 现金流")
        lines.append(f"- 经营现金流/净利润: {metrics.get('cash_flow_ratio', 0):.2f}")
        
        return "\n".join(lines)
