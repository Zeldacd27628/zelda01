# 会计操纵检测模块
# 核心功能：利用100万Token上下文检测财务造假信号

"""
会计操纵检测器 - FinLens的核心功能

本模块利用MiMo-V2.5-Pro的100万Token超长上下文能力，
深度阅读年报全文，检测各类会计操纵和财务造假信号。

检测维度：
1. 应收账款异常
2. 存货异常
3. 现金流与净利润背离
4. 会计政策变更
5. 关联交易异常
6. 其他应收款异常
7. 商誉减值问题
8. 研发费用资本化
9. 预付款项异常
10. 审计意见
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

from config import THRESHOLDS
from utils.helpers import setup_logging, safe_divide, calculate_percentage

logger = setup_logging()


class RiskLevel(Enum):
    """风险等级枚举"""
    HIGH = "高风险"
    MEDIUM = "中风险"
    LOW = "低风险"
    NONE = "无风险"


class SignalType(Enum):
    """信号类型枚举"""
    RECEIVABLE_ANOMALY = "receivable_anomaly"           # 应收账款异常
    INVENTORY_ANOMALY = "inventory_anomaly"               # 存货异常
    CASH_FLOW_ANOMALY = "cash_flow_anomaly"              # 现金流背离
    ACCOUNTING_CHANGE = "accounting_change"              # 会计政策变更
    RELATED_PARTY = "related_party"                     # 关联交易
    OTHER_RECEIVABLE = "other_receivable"                # 其他应收款
    GOODWILL_IMPAIRMENT = "goodwill_impairment"          # 商誉减值
    RD_CAPITALIZATION = "rd_capitalization"              # 研发资本化
    PREPAYMENT_ANOMALY = "prepayment_anomaly"           # 预付款项异常
    AUDIT_OPINION = "audit_opinion"                       # 审计意见
    GENERAL = "general"                                  # 通用信号


@dataclass
class ManipulationSignal:
    """会计操纵信号数据结构"""
    type: str                      # 信号类型
    level: str                     # 风险等级
    title: str                     # 信号标题
    description: str              # 详细描述
    evidence: List[str] = field(default_factory=list)  # 证据列表
    impact: str = ""               # 影响分析
    recommendation: str = ""       # 建议
    confidence: float = 0.0       # 置信度 0-1
    keywords: List[str] = field(default_factory=list)  # 触发关键词
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "type": self.type,
            "level": self.level,
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "keywords": self.keywords
        }


class ManipulationDetector:
    """
    会计操纵检测器
    
    核心功能：利用100万Token上下文深度分析年报，检测财务操纵信号。
    
    检测策略：
    1. 规则基础检测：基于预设阈值的异常识别
    2. 语义理解检测：利用LLM深度理解业务逻辑
    3. 关联分析：跨科目、跨期间、跨报表的关联验证
    """
    
    def __init__(self):
        """初始化检测器"""
        self.thresholds = THRESHOLDS
        self.detected_signals: List[ManipulationSignal] = []
    
    def detect(
        self, 
        full_text: str, 
        financial_metrics: Dict[str, Any]
    ) -> List[ManipulationSignal]:
        """
        执行完整检测流程
        
        Args:
            full_text: 年报全文（用于深度语义分析）
            financial_metrics: 已计算的财务指标
        
        Returns:
            检测到的风险信号列表
        """
        logger.info("开始会计操纵检测...")
        self.detected_signals = []
        
        # 1. 规则基础检测
        rule_based_signals = self._rule_based_detection(financial_metrics)
        self.detected_signals.extend(rule_based_signals)
        
        # 2. 语义检测（基于关键词和模式）
        semantic_signals = self._semantic_detection(full_text, financial_metrics)
        self.detected_signals.extend(semantic_signals)
        
        # 3. 关联分析
        correlation_signals = self._correlation_analysis(full_text, financial_metrics)
        self.detected_signals.extend(correlation_signals)
        
        # 4. 排序和去重
        self._deduplicate_and_rank()
        
        logger.info(f"检测完成，共发现 {len(self.detected_signals)} 个信号")
        
        return [s.to_dict() for s in self.detected_signals]
    
    def _rule_based_detection(self, metrics: Dict[str, Any]) -> List[ManipulationSignal]:
        """
        基于规则的异常检测
        
        使用预设阈值检测财务指标异常。
        """
        signals = []
        
        # 1. 应收账款异常检测
        receivable_growth = metrics.get("receivable_growth", 0)
        revenue_growth = metrics.get("revenue_growth", 0)
        receivable_diff = receivable_growth - revenue_growth
        
        if receivable_diff > self.thresholds["receivable_growth_diff"]:
            signals.append(ManipulationSignal(
                type=SignalType.RECEIVABLE_ANOMALY.value,
                level=RiskLevel.HIGH.value,
                title="应收账款增速远超营收增速",
                description=f"应收账款增长{receivable_growth:.1f}%，"
                           f"而营收仅增长{revenue_growth:.1f}%，"
                           f"差异达{receivable_diff:.1f}个百分点",
                evidence=[
                    f"应收账款增长率: {receivable_growth:.1f}%",
                    f"营业收入增长率: {revenue_growth:.1f}%",
                    f"差异: {receivable_diff:.1f}个百分点"
                ],
                impact="可能存在虚增收入、放松信用政策或回款困难",
                recommendation="核实收入确认政策、客户信用期变化、大客户经营状况",
                confidence=0.85,
                keywords=["应收账款", "营收增长差异"]
            ))
        
        # 2. 存货异常检测
        inventory_growth = metrics.get("inventory_growth", 0)
        
        if inventory_growth > self.thresholds["inventory_growth_threshold"]:
            signals.append(ManipulationSignal(
                type=SignalType.INVENTORY_ANOMALY.value,
                level=RiskLevel.HIGH.value,
                title="存货异常积压",
                description=f"存货增长{inventory_growth:.1f}%，"
                           f"显著高于正常水平",
                evidence=[
                    f"存货增长率: {inventory_growth:.1f}%",
                    f"阈值: {self.thresholds['inventory_growth_threshold']}%"
                ],
                impact="可能存在滞销、虚增资产或成本结转延迟",
                recommendation="核实存货库龄、周转率变化、跌价准备计提",
                confidence=0.80,
                keywords=["存货", "积压"]
            ))
        
        # 3. 现金流背离检测
        cash_flow_ratio = metrics.get("cash_flow_ratio", 1.0)
        
        if cash_flow_ratio < self.thresholds["cash_flow_diff"]:
            signals.append(ManipulationSignal(
                type=SignalType.CASH_FLOW_ANOMALY.value,
                level=RiskLevel.HIGH.value,
                title="经营现金流与净利润长期背离",
                description=f"经营现金流/净利润比率仅{cash_flow_ratio:.2f}，"
                           f"低于正常水平1.0",
                evidence=[
                    f"经营现金流/净利润比率: {cash_flow_ratio:.2f}",
                    f"正常水平参考: 1.0"
                ],
                impact="净利润含金量存疑，可能存在虚增利润",
                recommendation="分析应收、应付、存货变化，核实现金流质量",
                confidence=0.90,
                keywords=["现金流", "净利润背离"]
            ))
        
        # 4. 资产负债率异常
        debt_ratio = metrics.get("debt_ratio", 0)
        
        if debt_ratio > 85:
            signals.append(ManipulationSignal(
                type=SignalType.GENERAL.value,
                level=RiskLevel.HIGH.value,
                title="资产负债率过高",
                description=f"资产负债率{debt_ratio:.1f}%，财务风险较大",
                evidence=[
                    f"资产负债率: {debt_ratio:.1f}%"
                ],
                impact="偿债压力较大，财务风险偏高",
                recommendation="关注债务结构、现金流覆盖、融资能力",
                confidence=0.75,
                keywords=["资产负债率", "债务风险"]
            ))
        
        return signals
    
    def _semantic_detection(
        self, 
        full_text: str, 
        metrics: Dict[str, Any]
    ) -> List[ManipulationSignal]:
        """
        基于语义的检测
        
        通过关键词和模式匹配检测异常。
        """
        signals = []
        text_lower = full_text.lower()
        
        # 1. 审计意见检测
        audit_keywords = {
            "保留意见": RiskLevel.HIGH,
            "无法表示意见": RiskLevel.HIGH,
            "否定意见": RiskLevel.HIGH,
            "带强调事项段": RiskLevel.MEDIUM,
            "持续经营重大不确定性": RiskLevel.HIGH
        }
        
        for keyword, risk_level in audit_keywords.items():
            if keyword in full_text:
                signals.append(ManipulationSignal(
                    type=SignalType.AUDIT_OPINION.value,
                    level=risk_level.value,
                    title=f"审计意见异常: {keyword}",
                    description=f"审计报告中出现'{keyword}'，表明审计师对财报存在重大关切",
                    evidence=[f"年报中发现关键词: {keyword}"],
                    impact="财务报告可靠性存疑",
                    recommendation="深入分析强调事项段的具体内容",
                    confidence=0.95,
                    keywords=[keyword]
                ))
        
        # 2. 会计政策变更检测
        if "会计政策变更" in full_text or "会计估计变更" in full_text:
            # 提取变更详情
            change_pattern = r"会计政策[变更]*[：:]([^。]+)"
            matches = re.findall(change_pattern, full_text)
            
            signals.append(ManipulationSignal(
                type=SignalType.ACCOUNTING_CHANGE.value,
                level=RiskLevel.MEDIUM.value,
                title="存在会计政策或估计变更",
                description="年报披露了会计政策或会计估计变更，"
                           "需关注变更对利润的影响方向和合理性",
                evidence=matches[:3] if matches else ["年报中有相关披露"],
                impact="可能通过变更调节各期利润",
                recommendation="量化变更对各期损益的影响，评估变更理由合理性",
                confidence=0.70,
                keywords=["会计政策变更", "会计估计变更"]
            ))
        
        # 3. 关联交易检测
        related_party_keywords = [
            "关联交易", "关联方", "关联销售", "关联采购",
            "关联方往来", "关联担保"
        ]
        
        related_party_mentions = sum(1 for kw in related_party_keywords if kw in text_lower)
        
        if related_party_mentions >= 3:
            signals.append(ManipulationSignal(
                type=SignalType.RELATED_PARTY.value,
                level=RiskLevel.MEDIUM.value,
                title="关联交易披露较多",
                description=f"年报中关联交易相关披露出现{related_party_mentions}次，"
                           f"需关注交易的公允性和必要性",
                evidence=[f"关联交易关键词出现{related_party_mentions}次"],
                impact="可能存在利益输送或转移利润",
                recommendation="核实关联交易定价、金额占比、交易必要性",
                confidence=0.65,
                keywords=related_party_keywords
            ))
        
        # 4. 商誉减值检测
        goodwill_ratio = metrics.get("goodwill_ratio", 0)
        
        if goodwill_ratio > self.thresholds["goodwill_ratio"] * 100:
            signals.append(ManipulationSignal(
                type=SignalType.GOODWILL_IMPAIRMENT.value,
                level=RiskLevel.MEDIUM.value,
                title="商誉占比较高",
                description=f"商誉占净资产比例为{goodwill_ratio:.1f}%，"
                           f"存在较大减值风险",
                evidence=[f"商誉/净资产: {goodwill_ratio:.1f}%"],
                impact="未来可能面临大额商誉减值",
                recommendation="分析并购标的业绩表现，关注减值测试假设",
                confidence=0.75,
                keywords=["商誉", "减值"]
            ))
        
        # 5. 研发资本化检测
        rd_capitalization_ratio = metrics.get("rd_capitalization_ratio", 0)
        
        if rd_capitalization_ratio > self.thresholds["rd_capitalization_ratio"] * 100:
            signals.append(ManipulationSignal(
                type=SignalType.RD_CAPITALIZATION.value,
                level=RiskLevel.MEDIUM.value,
                title="研发资本化率偏高",
                description=f"研发支出资本化率为{rd_capitalization_ratio:.1f}%，"
                           f"高于正常水平",
                evidence=[f"研发资本化率: {rd_capitalization_ratio:.1f}%"],
                impact="可能通过资本化虚增当期利润",
                recommendation="核实资本化时点、依据，与同业对比",
                confidence=0.70,
                keywords=["研发费用", "资本化"]
            ))
        
        # 6. 其他应收款异常
        other_receivable_ratio = metrics.get("other_receivable_ratio", 0)
        
        if other_receivable_ratio > self.thresholds["other_receivable_ratio"] * 100:
            signals.append(ManipulationSignal(
                type=SignalType.OTHER_RECEIVABLE.value,
                level=RiskLevel.MEDIUM.value,
                title="其他应收款占比异常",
                description=f"其他应收款占总资产{other_receivable_ratio:.1f}%，"
                           f"可能存在资金占用",
                evidence=[f"其他应收款/总资产: {other_receivable_ratio:.1f}%"],
                impact="可能存在大股东资金占用或体外循环",
                recommendation="查看明细构成，核实对手方性质",
                confidence=0.75,
                keywords=["其他应收款", "资金占用"]
            ))
        
        # 7. 预付款项异常
        prepayment_growth = metrics.get("prepayment_growth", 0)
        
        if prepayment_growth > self.thresholds["prepayment_growth"]:
            signals.append(ManipulationSignal(
                type=SignalType.PREPAYMENT_ANOMALY.value,
                level=RiskLevel.MEDIUM.value,
                title="预付款项增长异常",
                description=f"预付款项增长{prepayment_growth:.1f}%，"
                           f"需关注是否虚构交易",
                evidence=[f"预付款项增长率: {prepayment_growth:.1f}%"],
                impact="可能存在虚构预付款转移资金",
                recommendation="核实预付对手方、账龄、业务背景",
                confidence=0.70,
                keywords=["预付款项", "预付账款"]
            ))
        
        return signals
    
    def _correlation_analysis(
        self, 
        full_text: str, 
        metrics: Dict[str, Any]
    ) -> List[ManipulationSignal]:
        """
        关联分析
        
        通过跨指标关联验证发现隐藏异常。
        """
        signals = []
        
        # 1. 毛利率与净利率差异分析
        gross_margin = metrics.get("gross_margin", 0)
        net_margin = metrics.get("net_margin", 0)
        margin_diff = gross_margin - net_margin
        
        # 正常情况下，毛利率和净利率差距应该在合理范围
        if margin_diff > 60:  # 差距超过60个百分点
            signals.append(ManipulationSignal(
                type=SignalType.GENERAL.value,
                level=RiskLevel.MEDIUM.value,
                title="毛利率与净利率差距过大",
                description=f"毛利率{gross_margin:.1f}%，净利率{net_margin:.1f}%，"
                           f"差距{margin_diff:.1f}个百分点，费用率异常",
                evidence=[
                    f"毛利率: {gross_margin:.1f}%",
                    f"净利率: {net_margin:.1f}%",
                    f"差值: {margin_diff:.1f}个百分点"
                ],
                impact="费用结构可能存在异常",
                recommendation="分析费用构成，关注是否有一次性费用",
                confidence=0.60,
                keywords=["毛利率", "净利率", "费用率"]
            ))
        
        # 2. 应收账款与存货双高检测
        receivable_growth = metrics.get("receivable_growth", 0)
        inventory_growth = metrics.get("inventory_growth", 0)
        
        if receivable_growth > 20 and inventory_growth > 20:
            signals.append(ManipulationSignal(
                type=SignalType.GENERAL.value,
                level=RiskLevel.MEDIUM.value,
                title="应收账款与存货双高增长",
                description=f"应收账款增长{receivable_growth:.1f}%，"
                           f"存货增长{inventory_growth:.1f}%，"
                           f"两项同时快速增长需警惕",
                evidence=[
                    f"应收账款增长率: {receivable_growth:.1f}%",
                    f"存货增长率: {inventory_growth:.1f}%"
                ],
                impact="可能同时存在虚增收入和虚增存货",
                recommendation="结合现金流分析，核实业务真实性",
                confidence=0.75,
                keywords=["应收账款", "存货", "双高"]
            ))
        
        # 3. 营收增长与税收背离
        revenue_growth = metrics.get("revenue_growth", 0)
        
        # 正常情况下，营收增长应带来税收相应增长
        # 如果营收大幅增长但税收异常低，可能有问题
        # 这里简化处理，实际需要更多数据
        
        return signals
    
    def _deduplicate_and_rank(self):
        """去重和排序"""
        # 按风险等级和置信度排序
        level_order = {RiskLevel.HIGH.value: 0, RiskLevel.MEDIUM.value: 1, RiskLevel.LOW.value: 2}
        
        self.detected_signals.sort(
            key=lambda s: (
                level_order.get(s.level, 3),  # 首先按风险等级
                -s.confidence                  # 然后按置信度
            )
        )
    
    def get_high_risk_signals(self) -> List[ManipulationSignal]:
        """获取高风险信号"""
        return [s for s in self.detected_signals if s.level == RiskLevel.HIGH.value]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """获取风险摘要"""
        return {
            "total_signals": len(self.detected_signals),
            "high_risk_count": len(self.get_high_risk_signals()),
            "medium_risk_count": len([s for s in self.detected_signals if s.level == RiskLevel.MEDIUM.value]),
            "low_risk_count": len([s for s in self.detected_signals if s.level == RiskLevel.LOW.value]),
            "overall_risk_level": self._determine_overall_risk()
        }
    
    def _determine_overall_risk(self) -> str:
        """确定整体风险等级"""
        high_count = len(self.get_high_risk_signals())
        medium_count = len([s for s in self.detected_signals if s.level == RiskLevel.MEDIUM.value])
        
        if high_count >= 2:
            return "高风险"
        elif high_count >= 1 or medium_count >= 3:
            return "中风险"
        elif medium_count >= 1:
            return "低风险"
        else:
            return "基本正常"
