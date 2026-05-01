# 行业对比模块
# 同行业财务指标横向对比

"""
行业对比分析器

将目标公司的财务指标与行业平均水平进行对比，
识别显著偏离的指标，标记异常值。
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from config import INDUSTRY_BENCHMARKS
from utils.helpers import setup_logging, safe_divide, calculate_percentage

logger = setup_logging()


class DeviationLevel(Enum):
    """偏离等级"""
    SIGNIFICANT_HIGH = "显著偏高"     # 显著高于行业均值
    HIGH = "偏高"                      # 高于行业均值
    NORMAL = "正常"                    # 在正常范围内
    LOW = "偏低"                       # 低于行业均值
    SIGNIFICANT_LOW = "显著偏低"        # 显著低于行业均值


@dataclass
class ComparisonResult:
    """对比结果数据结构"""
    indicator: str                    # 指标名称
    company_value: float              # 公司值
    industry_avg: float               # 行业均值
    industry_median: Optional[float] = None  # 行业中位数
    deviation: float = 0.0            # 偏离度（百分比）
    deviation_level: str = "正常"     # 偏离等级
    is_concern: bool = False          # 是否需要关注
    concern_reason: str = ""          # 关注原因
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "indicator": self.indicator,
            "company_value": self.company_value,
            "industry_avg": self.industry_avg,
            "industry_median": self.industry_median,
            "deviation": self.deviation,
            "deviation_level": self.deviation_level,
            "is_concern": self.is_concern,
            "concern_reason": self.concern_reason
        }


class IndustryComparator:
    """
    行业对比分析器
    
    功能：
    1. 与行业均值/中位数对比
    2. 识别显著偏离的指标
    3. 区分"优势"和"风险"
    4. 生成对比报告
    """
    
    def __init__(self, industry: str):
        """
        初始化对比器
        
        Args:
            industry: 所属行业名称
        """
        self.industry = industry
        self.benchmarks = self._get_industry_benchmarks(industry)
        self.comparisons: List[ComparisonResult] = []
    
    def _get_industry_benchmarks(self, industry: str) -> Dict[str, float]:
        """
        获取行业基准数据
        
        Args:
            industry: 行业名称
        
        Returns:
            行业基准指标字典
        """
        # 直接使用配置中的基准
        if industry in INDUSTRY_BENCHMARKS:
            return INDUSTRY_BENCHMARKS[industry]
        
        # 尝试模糊匹配
        for ind, benchmark in INDUSTRY_BENCHMARKS.items():
            if industry in ind or ind in industry:
                logger.info(f"使用行业基准: {ind} (与 {industry} 匹配)")
                return benchmark
        
        # 返回默认基准
        logger.warning(f"未找到行业 {industry} 的基准，使用默认基准")
        return INDUSTRY_BENCHMARKS.get("default", INDUSTRY_BENCHMARKS["制造业"])
    
    def compare(self, financial_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行行业对比
        
        Args:
            financial_metrics: 公司财务指标
        
        Returns:
            对比结果字典
        """
        logger.info(f"开始行业对比: {self.industry}")
        self.comparisons = []
        
        # 盈利能力对比
        self._compare_profitability(financial_metrics)
        
        # 偿债能力对比
        self._compare_solvency(financial_metrics)
        
        # 运营效率对比
        self._compare_efficiency(financial_metrics)
        
        # 现金流对比
        self._compare_cash_flow(financial_metrics)
        
        # 生成对比摘要
        summary = self._generate_summary()
        
        return {
            "industry": self.industry,
            "benchmarks": self.benchmarks,
            "comparisons": [c.to_dict() for c in self.comparisons],
            "concerns": [c.to_dict() for c in self.comparisons if c.is_concern],
            "advantages": self._identify_advantages(),
            "summary": summary
        }
    
    def _compare_profitability(self, metrics: Dict[str, Any]):
        """对比盈利能力指标"""
        # 毛利率
        gross_margin = metrics.get("gross_margin", 0)
        if gross_margin > 0 and "gross_margin" in self.benchmarks:
            self._add_comparison(
                "毛利率",
                gross_margin,
                self.benchmarks["gross_margin"],
                metrics_type="profitability"
            )
        
        # 净利率
        net_margin = metrics.get("net_margin", 0)
        if net_margin > 0 and "net_margin" in self.benchmarks:
            self._add_comparison(
                "净利率",
                net_margin,
                self.benchmarks["net_margin"],
                metrics_type="profitability"
            )
        
        # ROE
        roe = metrics.get("roe", 0)
        if roe > 0 and "roe" in self.benchmarks:
            self._add_comparison(
                "净资产收益率(ROE)",
                roe,
                self.benchmarks["roe"],
                metrics_type="profitability"
            )
    
    def _compare_solvency(self, metrics: Dict[str, Any]):
        """对比偿债能力指标"""
        # 资产负债率
        debt_ratio = metrics.get("debt_ratio", 0)
        if debt_ratio > 0 and "debt_ratio" in self.benchmarks:
            # 资产负债率是越低越好（风险角度看）
            self._add_comparison(
                "资产负债率",
                debt_ratio,
                self.benchmarks["debt_ratio"],
                metrics_type="solvency",
                inverse=True  # 反向指标
            )
        
        # 流动比率
        current_ratio = metrics.get("current_ratio", 0)
        if current_ratio > 0 and "current_ratio" in self.benchmarks:
            self._add_comparison(
                "流动比率",
                current_ratio,
                self.benchmarks["current_ratio"],
                metrics_type="solvency"
            )
    
    def _compare_efficiency(self, metrics: Dict[str, Any]):
        """对比运营效率指标"""
        # 应收账款周转率
        receivable_turnover = metrics.get("receivable_turnover", 0)
        if receivable_turnover > 0 and "receivable_turnover" in self.benchmarks:
            self._add_comparison(
                "应收账款周转率",
                receivable_turnover,
                self.benchmarks["receivable_turnover"],
                metrics_type="efficiency"
            )
        
        # 存货周转率
        inventory_turnover = metrics.get("inventory_turnover", 0)
        if inventory_turnover > 0 and "inventory_turnover" in self.benchmarks:
            self._add_comparison(
                "存货周转率",
                inventory_turnover,
                self.benchmarks.get("inventory_turnover", 5.0),
                metrics_type="efficiency"
            )
    
    def _compare_cash_flow(self, metrics: Dict[str, Any]):
        """对比现金流指标"""
        # 经营现金流/净利润
        cash_flow_ratio = metrics.get("cash_flow_ratio", 0)
        if cash_flow_ratio > 0:
            self._add_comparison(
                "经营现金流/净利润",
                cash_flow_ratio,
                1.0,  # 正常水平为1
                metrics_type="cash_flow",
                threshold=0.3  # 偏离超过30%需要关注
            )
    
    def _add_comparison(
        self,
        indicator: str,
        company_value: float,
        industry_avg: float,
        metrics_type: str = "general",
        inverse: bool = False,
        threshold: float = 0.3
    ):
        """
        添加对比结果
        
        Args:
            indicator: 指标名称
            company_value: 公司值
            industry_avg: 行业均值
            metrics_type: 指标类型
            inverse: 是否反向指标（越低越好）
            threshold: 关注阈值
        """
        # 计算偏离度
        if industry_avg != 0:
            deviation = (company_value - industry_avg) / industry_avg * 100
        else:
            deviation = 0
        
        # 确定偏离等级
        abs_deviation = abs(deviation)
        
        if inverse:
            # 反向指标（越低越好，如资产负债率）
            if deviation < -threshold * 100:
                deviation_level = DeviationLevel.SIGNIFICANT_LOW.value
                is_advantage = True
                concern = False
                reason = "显著低于行业均值，财务更稳健"
            elif deviation < 0:
                deviation_level = DeviationLevel.LOW.value
                is_advantage = True
                concern = False
                reason = "低于行业均值"
            elif deviation > threshold * 100:
                deviation_level = DeviationLevel.SIGNIFICANT_HIGH.value
                is_advantage = False
                concern = True
                reason = "显著高于行业均值，财务风险较大"
            else:
                deviation_level = DeviationLevel.NORMAL.value
                is_advantage = False
                concern = False
                reason = "在正常范围内"
        else:
            # 正向指标（越高越好，如毛利率）
            if deviation > threshold * 100:
                deviation_level = DeviationLevel.SIGNIFICANT_HIGH.value
                is_advantage = True
                concern = False
                reason = "显著高于行业均值，竞争力强"
            elif deviation > 0:
                deviation_level = DeviationLevel.HIGH.value
                is_advantage = True
                concern = False
                reason = "高于行业均值"
            elif deviation < -threshold * 100:
                deviation_level = DeviationLevel.SIGNIFICANT_LOW.value
                is_advantage = False
                concern = True
                reason = "显著低于行业均值，竞争力弱"
            else:
                deviation_level = DeviationLevel.NORMAL.value
                is_advantage = False
                concern = False
                reason = "在正常范围内"
        
        comparison = ComparisonResult(
            indicator=indicator,
            company_value=company_value,
            industry_avg=industry_avg,
            deviation=deviation,
            deviation_level=deviation_level,
            is_concern=concern,
            concern_reason=reason
        )
        
        self.comparisons.append(comparison)
    
    def _identify_advantages(self) -> List[Dict]:
        """识别公司优势"""
        advantages = []
        
        for comp in self.comparisons:
            if comp.deviation_level in [DeviationLevel.SIGNIFICANT_HIGH.value, DeviationLevel.HIGH.value]:
                if not comp.is_concern:  # 确保不是反向指标的高值
                    advantages.append({
                        "indicator": comp.indicator,
                        "value": comp.company_value,
                        "industry_avg": comp.industry_avg,
                        "deviation": f"+{comp.deviation:.1f}%"
                    })
        
        return advantages
    
    def _generate_summary(self) -> str:
        """生成对比摘要"""
        concerns = [c for c in self.comparisons if c.is_concern]
        advantages = self._identify_advantages()
        
        summary_parts = []
        
        if concerns:
            summary_parts.append(f"需关注: {len(concerns)}项指标偏离行业")
        
        if advantages:
            summary_parts.append(f"优势: {len(advantages)}项指标优于行业")
        
        if not concerns and not advantages:
            summary_parts.append("各项指标与行业平均水平基本一致")
        
        return "; ".join(summary_parts)
    
    def format_comparison_table(self) -> str:
        """
        格式化对比表格（Markdown格式）
        
        Returns:
            Markdown表格字符串
        """
        if not self.comparisons:
            return "暂无对比数据"
        
        lines = []
        lines.append("| 指标 | 公司值 | 行业均值 | 偏离度 | 状态 |")
        lines.append("|------|--------|---------|--------|------|")
        
        for comp in self.comparisons:
            # 格式化数值
            if abs(comp.company_value) >= 100:
                company_str = f"{comp.company_value:.0f}"
            elif abs(comp.company_value) >= 1:
                company_str = f"{comp.company_value:.1f}"
            else:
                company_str = f"{comp.company_value:.2f}"
            
            industry_str = f"{comp.industry_avg:.1f}"
            deviation_str = f"{comp.deviation:+.1f}%"
            
            # 状态emoji
            if "显著" in comp.deviation_level:
                if comp.is_concern:
                    level_emoji = "🔴"
                else:
                    level_emoji = "🟢"
            elif comp.deviation_level == "正常":
                level_emoji = "🟡"
            else:
                if comp.is_concern:
                    level_emoji = "🟠"
                else:
                    level_emoji = "🟢"
            
            lines.append(
                f"| {comp.indicator} | {company_str} | {industry_str} | "
                f"{deviation_str} | {level_emoji} {comp.deviation_level} |"
            )
        
        return "\n".join(lines)
    
    def get_comparison_report(self) -> str:
        """
        生成完整的对比报告
        
        Returns:
            Markdown格式报告
        """
        report = []
        
        report.append("## 行业对比分析")
        report.append("")
        report.append(f"**所属行业**: {self.industry}")
        report.append("")
        report.append(self.format_comparison_table())
        report.append("")
        
        # 优势列表
        advantages = self._identify_advantages()
        if advantages:
            report.append("### 优势指标")
            for adv in advantages:
                report.append(
                    f"- **{adv['indicator']}**: {adv['value']:.2f} "
                    f"(行业均值: {adv['industry_avg']:.1f}, {adv['deviation']})"
                )
            report.append("")
        
        # 关注列表
        concerns = [c for c in self.comparisons if c.is_concern]
        if concerns:
            report.append("### 需关注指标")
            for con in concerns:
                report.append(
                    f"- **{con['indicator']}**: {con.company_value:.2f} "
                    f"(行业均值: {con.industry_avg:.1f})"
                )
                report.append(f"  - {con.concern_reason}")
            report.append("")
        
        return "\n".join(report)
