# 报告生成模块
# 生成结构化财务分析报告

"""
财务分析报告生成器

生成格式化的Markdown报告，包含：
1. 封面信息
2. 财务指标总览
3. 风险信号详情
4. 行业对比分析
5. 综合评分
6. 投资建议
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from utils.helpers import setup_logging, format_number, calculate_percentage

logger = setup_logging()


@dataclass
class ReportConfig:
    """报告配置"""
    include_raw_data: bool = True
    include_comparison: bool = True
    include_risk_signals: bool = True
    include_recommendations: bool = True
    output_format: str = "markdown"


class ReportGenerator:
    """
    财务分析报告生成器
    
    将各类分析结果整合为结构化的Markdown报告。
    """
    
    def __init__(self, company_name: str, industry: str):
        """
        初始化报告生成器
        
        Args:
            company_name: 公司名称
            industry: 所属行业
        """
        self.company_name = company_name
        self.industry = industry
        self.report_date = datetime.now().strftime("%Y-%m-%d")
    
    def generate(
        self,
        financial_metrics: Dict[str, Any],
        manipulation_signals: List[Dict],
        industry_comparison: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """
        生成完整报告
        
        Args:
            financial_metrics: 财务指标
            manipulation_signals: 风险信号
            industry_comparison: 行业对比
            risk_assessment: 风险评估
        
        Returns:
            Markdown格式报告
        """
        logger.info("开始生成分析报告...")
        
        report_parts = []
        
        # 1. 报告封面
        report_parts.append(self._generate_header())
        
        # 2. 核心结论
        report_parts.append(self._generate_core_conclusion(risk_assessment))
        
        # 3. 财务指标总览
        report_parts.append(self._generate_metrics_section(financial_metrics))
        
        # 4. 风险信号详情
        report_parts.append(self._generate_risk_signals_section(manipulation_signals))
        
        # 5. 行业对比分析
        report_parts.append(self._generate_industry_comparison_section(industry_comparison))
        
        # 6. 综合评分
        report_parts.append(self._generate_score_section(risk_assessment))
        
        # 7. 投资建议
        report_parts.append(self._generate_recommendations_section(
            risk_assessment, manipulation_signals, financial_metrics
        ))
        
        # 8. 附录
        report_parts.append(self._generate_appendix())
        
        report = "\n\n".join(report_parts)
        
        logger.info("报告生成完成")
        
        return report
    
    def _generate_header(self) -> str:
        """生成报告封面"""
        lines = [
            f"# {self.company_name} - 财务健康分析报告",
            "",
            "---",
            "",
            "| 项目 | 内容 |",
            "|------|------|",
            f"| **公司名称** | {self.company_name} |",
            f"| **所属行业** | {self.industry} |",
            f"| **分析日期** | {self.report_date} |",
            f"| **报告类型** | 年报深度分析 |",
            f"| **分析工具** | FinLens (MiMo-V2.5-Pro驱动) |",
            "",
            "> ⚠️ **免责声明**: 本报告由AI自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。",
            "",
            "---",
        ]
        
        return "\n".join(lines)
    
    def _generate_core_conclusion(self, risk_assessment: Dict[str, Any]) -> str:
        """生成核心结论"""
        risk_level = risk_assessment.get("risk_level", "未知")
        overall_score = risk_assessment.get("overall_score", 0)
        
        # 根据风险等级选择emoji
        risk_emoji = {
            "高风险": "🔴",
            "中风险": "🟡",
            "低风险": "🟢",
            "基本正常": "🟢",
            "未知": "⚪"
        }.get(risk_level, "⚪")
        
        # 生成一句话总结
        summary = risk_assessment.get("summary", "")
        
        lines = [
            "## 📌 核心结论",
            "",
            f"{risk_emoji} **{risk_level}** | 综合评分: **{overall_score}/100**",
            "",
            summary if summary else f"基于财务指标分析、风险信号检测和行业对比，{self.company_name}当前财务状况{risk_level}。",
            "",
        ]
        
        return "\n".join(lines)
    
    def _generate_metrics_section(self, metrics: Dict[str, Any]) -> str:
        """生成财务指标部分"""
        lines = [
            "## 📊 财务指标总览",
            "",
        ]
        
        # 盈利能力
        profitability = {
            "毛利率": metrics.get("gross_margin", 0),
            "净利率": metrics.get("net_margin", 0),
            "营业利润率": metrics.get("operating_margin", 0),
            "ROE": metrics.get("roe", 0),
            "ROA": metrics.get("roa", 0),
        }
        
        if any(v > 0 for v in profitability.values()):
            lines.append("### 盈利能力")
            lines.append("| 指标 | 数值 | 参考值 |")
            lines.append("|------|------|--------|")
            for name, value in profitability.items():
                if value > 0:
                    if "RO" in name:
                        lines.append(f"| {name} | {value:.2f}% | >15% |")
                    else:
                        lines.append(f"| {name} | {value:.2f}% | 行业均值 |")
            lines.append("")
        
        # 偿债能力
        solvency = {
            "资产负债率": metrics.get("debt_ratio", 0),
            "流动比率": metrics.get("current_ratio", 0),
            "速动比率": metrics.get("quick_ratio", 0),
        }
        
        if any(v > 0 for v in solvency.values()):
            lines.append("### 偿债能力")
            lines.append("| 指标 | 数值 | 参考值 |")
            lines.append("|------|------|--------|")
            for name, value in solvency.items():
                if value > 0:
                    if name == "资产负债率":
                        lines.append(f"| {name} | {value:.2f}% | <60% |")
                    else:
                        lines.append(f"| {name} | {value:.2f} | >1 |")
            lines.append("")
        
        # 运营效率
        efficiency = {
            "存货周转率": metrics.get("inventory_turnover", 0),
            "应收账款周转率": metrics.get("receivable_turnover", 0),
            "总资产周转率": metrics.get("total_asset_turnover", 0),
        }
        
        if any(v > 0 for v in efficiency.values()):
            lines.append("### 运营效率")
            lines.append("| 指标 | 数值 |")
            lines.append("|------|------|")
            for name, value in efficiency.items():
                if value > 0:
                    lines.append(f"| {name} | {value:.2f} |")
            lines.append("")
        
        # 现金流
        cash_flow = {
            "经营现金流/净利润": metrics.get("cash_flow_ratio", 0),
        }
        
        if any(v > 0 for v in cash_flow.values()):
            lines.append("### 现金流质量")
            lines.append("| 指标 | 数值 | 参考值 |")
            lines.append("|------|------|--------|")
            for name, value in cash_flow.items():
                if value > 0:
                    lines.append(f"| {name} | {value:.2f} | >1 |")
            lines.append("")
        
        # 成长性
        growth = {
            "营收增长率": metrics.get("revenue_growth", 0),
            "净利润增长率": metrics.get("profit_growth", 0),
        }
        
        if any(v != 0 for v in growth.values()):
            lines.append("### 成长性")
            lines.append("| 指标 | 数值 |")
            lines.append("|------|------|")
            for name, value in growth.items():
                if value != 0:
                    sign = "+" if value > 0 else ""
                    lines.append(f"| {name} | {sign}{value:.2f}% |")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_risk_signals_section(self, signals: List[Dict]) -> str:
        """生成风险信号部分"""
        lines = [
            "## ⚠️ 风险信号检测",
            "",
        ]
        
        if not signals:
            lines.append("✅ **未发现明显风险信号**")
            lines.append("")
            lines.append("基于年报全文分析，未检测到显著的会计操纵风险信号。")
            return "\n".join(lines)
        
        # 按风险等级分类
        high_risk = [s for s in signals if s.get("level") == "高风险"]
        medium_risk = [s for s in signals if s.get("level") == "中风险"]
        low_risk = [s for s in signals if s.get("level") == "低风险"]
        
        # 高风险信号
        if high_risk:
            lines.append("### 🔴 高风险信号")
            lines.append("")
            for i, signal in enumerate(high_risk, 1):
                lines.append(f"**{i}. {signal.get('title', '未命名信号')}**")
                lines.append("")
                lines.append(f"- 描述: {signal.get('description', '无')}")
                if signal.get("evidence"):
                    lines.append(f"- 证据:")
                    for evidence in signal.get("evidence", [])[:3]:
                        lines.append(f"  - {evidence}")
                if signal.get("recommendation"):
                    lines.append(f"- 建议: {signal.get('recommendation')}")
                lines.append("")
        
        # 中风险信号
        if medium_risk:
            lines.append("### 🟡 中风险信号")
            lines.append("")
            for i, signal in enumerate(medium_risk, 1):
                lines.append(f"**{i}. {signal.get('title', '未命名信号')}**")
                lines.append("")
                lines.append(f"- 描述: {signal.get('description', '无')}")
                if signal.get("recommendation"):
                    lines.append(f"- 建议: {signal.get('recommendation')}")
                lines.append("")
        
        # 低风险信号
        if low_risk:
            lines.append("### 🟢 低风险信号")
            lines.append("")
            for i, signal in enumerate(low_risk, 1):
                lines.append(f"- {signal.get('title', '未命名信号')}: {signal.get('description', '')}")
            lines.append("")
        
        # 总结
        lines.append("---")
        lines.append(f"**风险信号统计**: 高风险 {len(high_risk)} 项 | 中风险 {len(medium_risk)} 项 | 低风险 {len(low_risk)} 项")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_industry_comparison_section(self, comparison: Dict[str, Any]) -> str:
        """生成行业对比部分"""
        lines = [
            "## 📈 行业对比分析",
            "",
            f"**所属行业**: {comparison.get('industry', self.industry)}",
            "",
        ]
        
        comparisons = comparison.get("comparisons", [])
        
        if not comparisons:
            lines.append("暂无行业对比数据。")
            return "\n".join(lines)
        
        # 生成表格
        lines.append("| 指标 | 公司值 | 行业均值 | 偏离度 | 状态 |")
        lines.append("|------|--------|---------|--------|------|")
        
        for comp in comparisons:
            indicator = comp.get("indicator", "")
            company_value = comp.get("company_value", 0)
            industry_avg = comp.get("industry_avg", 0)
            deviation = comp.get("deviation", 0)
            level = comp.get("deviation_level", "正常")
            
            # 格式化数值
            if abs(company_value) >= 100:
                company_str = f"{company_value:.0f}"
            elif abs(company_value) >= 1:
                company_str = f"{company_value:.1f}"
            else:
                company_str = f"{company_value:.2f}"
            
            industry_str = f"{industry_avg:.1f}"
            deviation_str = f"{deviation:+.1f}%"
            
            # 状态emoji
            if "显著" in level:
                emoji = "🔴" if comp.get("is_concern") else "🟢"
            elif level == "正常":
                emoji = "🟡"
            else:
                emoji = "🟢" if not comp.get("is_concern") else "🟠"
            
            lines.append(f"| {indicator} | {company_str} | {industry_str} | {deviation_str} | {emoji} {level} |")
        
        lines.append("")
        
        # 优势列表
        advantages = comparison.get("advantages", [])
        if advantages:
            lines.append("### 优势指标")
            for adv in advantages[:5]:
                lines.append(f"- **{adv['indicator']}**: {adv['value']:.2f} ({adv['deviation']})")
            lines.append("")
        
        # 关注事项
        concerns = comparison.get("concerns", [])
        if concerns:
            lines.append("### 需关注事项")
            for con in concerns[:5]:
                lines.append(f"- **{con['indicator']}**: {con['concern_reason']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_score_section(self, assessment: Dict[str, Any]) -> str:
        """生成综合评分部分"""
        overall_score = assessment.get("overall_score", 0)
        risk_level = assessment.get("risk_level", "未知")
        
        # 评分条
        score_bar = self._generate_score_bar(overall_score)
        
        lines = [
            "## 📊 综合评分",
            "",
            f"### {score_bar}",
            "",
            f"**总分**: {overall_score}/100",
            "",
            f"**风险等级**: {risk_level}",
            "",
        ]
        
        # 分数构成
        breakdown = assessment.get("score_breakdown", {})
        if breakdown:
            lines.append("### 评分构成")
            lines.append("")
            lines.append("| 维度 | 得分 |")
            lines.append("|------|------|")
            for dim, score in breakdown.items():
                if isinstance(score, (int, float)):
                    lines.append(f"| {dim} | {score}/100 |")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_score_bar(self, score: int) -> str:
        """生成评分进度条"""
        filled = score // 5
        empty = 20 - filled
        
        bar = "▓" * filled + "░" * empty
        
        # 颜色标注
        if score >= 70:
            color = "🟢"
        elif score >= 40:
            color = "🟡"
        else:
            color = "🔴"
        
        return f"{color} [{bar}] {score}/100"
    
    def _generate_recommendations_section(
        self,
        risk_assessment: Dict[str, Any],
        signals: List[Dict],
        metrics: Dict[str, Any]
    ) -> str:
        """生成投资建议部分"""
        risk_level = risk_assessment.get("risk_level", "未知")
        overall_score = risk_assessment.get("overall_score", 0)
        
        lines = [
            "## 💡 投资建议",
            "",
        ]
        
        # 风险提示
        lines.append("### ⚠️ 风险提示")
        
        if risk_level == "高风险":
            lines.append("🔴 **高风险警示**: 公司存在多项重大财务风险信号，建议谨慎对待，必要时回避。")
        elif risk_level == "中风险":
            lines.append("🟡 **中风险提示**: 公司存在一些需要关注的财务问题，建议深入研究后再做决策。")
        else:
            lines.append("🟢 **风险可控**: 公司财务状况基本正常，可保持常规关注。")
        
        lines.append("")
        
        # 具体建议
        lines.append("### 📋 具体建议")
        
        high_risk = [s for s in signals if s.get("level") == "高风险"]
        
        if high_risk:
            lines.append("**需重点核实事项**:")
            for signal in high_risk[:3]:
                lines.append(f"1. {signal.get('title', '未知问题')}")
            lines.append("")
        
        # 财务健康度评价
        if overall_score >= 80:
            lines.append("**财务健康度**: 优秀，公司财务状况良好，盈利能力强，现金流充裕。")
        elif overall_score >= 60:
            lines.append("**财务健康度**: 良好，公司财务状况正常，但仍需关注部分指标。")
        elif overall_score >= 40:
            lines.append("**财务健康度**: 一般，公司财务存在一些问题，需要谨慎对待。")
        else:
            lines.append("**财务健康度**: 较差，公司财务存在较大问题，建议回避。")
        
        lines.append("")
        
        # 总结
        lines.append("> 📌 **总结**: 建议结合公司基本面、行业前景、估值水平等因素综合判断，不应仅凭财务指标做出投资决策。")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_appendix(self) -> str:
        """生成附录"""
        lines = [
            "---",
            "## 📎 附录",
            "",
            "### 分析方法说明",
            "",
            "本报告采用以下分析方法：",
            "",
            "1. **PDF年报解析**: 自动提取年报中的财务报表和附注信息",
            "2. **财务指标计算**: 计算盈利能力、偿债能力、运营效率等核心指标",
            "3. **会计操纵检测**: 基于100万Token上下文深度分析年报全文，检测潜在风险信号",
            "4. **行业对比**: 与行业平均水平进行横向对比，识别显著偏离的指标",
            "",
            "### 风险信号检测维度",
            "",
            "- 应收账款异常增长",
            "- 存货异常积压",
            "- 经营现金流与净利润背离",
            "- 频繁变更会计政策/估计",
            "- 关联交易占比过高",
            "- 其他应收款异常",
            "- 商誉减值时机可疑",
            "- 研发费用资本化率异常",
            "- 预付款项异常增长",
            "- 非标审计意见",
            "",
            "### 免责声明",
            "",
            "本报告由AI自动生成，仅供参考。报告中的分析结果基于公开披露的年报信息，"
            "不构成任何投资建议。投资者应自主判断，理性投资。",
            "",
            "---",
            "",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "*Powered by FinLens & MiMo-V2.5-Pro*",
        ]
        
        return "\n".join(lines)
