# FinLens Agent工作流
# 核心调度逻辑

"""
FinLens的核心工作流调度器，负责串联所有分析模块，
利用MiMo-V2.5-Pro进行深度财务分析。
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from parsers.pdf_parser import PDFParser
from analyzers.financial import FinancialAnalyzer
from analyzers.detection import ManipulationDetector
from analyzers.comparison import IndustryComparator
from generators.report import ReportGenerator
from agent.prompts import (
    SYSTEM_PROMPT,
    ANALYSIS_PROMPT,
    MANIPULATION_DETECTION_PROMPT,
    RISK_ASSESSMENT_PROMPT,
    INDUSTRY_COMPARISON_PROMPT,
    FINAL_REPORT_PROMPT,
    QA_PROMPT
)
from config import (
    MIMO_BASE_URL,
    MIMO_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    API_TIMEOUT,
    MAX_RETRIES,
    AGENT_CONFIG
)
from utils.helpers import setup_logging, format_number, calculate_percentage

logger = setup_logging()


class FinLensWorkflow:
    """
    FinLens工作流调度器
    
    核心流程:
    1. PDF解析 -> 2. 财务指标计算 -> 3. 会计操纵检测 -> 
    4. 行业对比 -> 5. 报告生成 -> 6. 交互问答
    """
    
    def __init__(
        self, 
        api_key: str, 
        company_name: str, 
        industry: str,
        output_dir: str = "./output"
    ):
        """
        初始化FinLens工作流
        
        Args:
            api_key: MiMo API密钥
            company_name: 公司名称
            industry: 所属行业
            output_dir: 输出目录
        """
        self.api_key = api_key
        self.company_name = company_name
        self.industry = industry
        self.output_dir = Path(output_dir)
        
        # 初始化OpenAI兼容客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=MIMO_BASE_URL,
            timeout=API_TIMEOUT
        )
        
        # 初始化各模块
        self.pdf_parser = PDFParser()
        self.financial_analyzer = FinancialAnalyzer()
        self.manipulation_detector = ManipulationDetector()
        self.industry_comparator = IndustryComparator(industry)
        self.report_generator = ReportGenerator(company_name, industry)
        
        # 存储分析结果
        self.analysis_context = {
            "company_name": company_name,
            "industry": industry,
            "pdf_text": "",
            "financial_data": {},
            "financial_metrics": {},
            "manipulation_signals": [],
            "industry_comparison": {},
            "risk_assessment": {},
            "analysis_history": [],
            "conversation_history": []
        }
        
        logger.info(f"FinLens工作流初始化完成: {company_name} ({industry})")
    
    def _call_llm(
        self, 
        messages: List[Dict], 
        system_prompt: Optional[str] = None,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        调用MiMo LLM API
        
        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词（可选）
            temperature: 温度参数
            max_tokens: 最大输出Token数
        
        Returns:
            LLM响应文本
        """
        # 如果提供了系统提示词，在消息列表开头插入
        if system_prompt:
            full_messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            full_messages = messages
        
        # 重试机制
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=MIMO_MODEL,
                    messages=full_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise
        
        return ""
    
    def _build_context_summary(self) -> str:
        """构建上下文摘要，用于提示词"""
        return f"""
当前分析公司: {self.company_name}
所属行业: {self.industry}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

已完成的分析:
{json.dumps(self.analysis_context['financial_metrics'], ensure_ascii=False, indent=2)}

风险信号检测结果:
{json.dumps(self.analysis_context['manipulation_signals'], ensure_ascii=False, indent=2)}

行业对比结果:
{json.dumps(self.analysis_context['industry_comparison'], ensure_ascii=False, indent=2)}
"""
    
    def run(self, pdf_path: str) -> Dict[str, Any]:
        """
        执行完整的财务分析流程
        
        Args:
            pdf_path: PDF年报文件路径
        
        Returns:
            包含完整分析结果的字典
        """
        logger.info(f"开始分析: {pdf_path}")
        start_time = datetime.now()
        
        # 步骤1: PDF解析
        logger.info("[1/5] 正在解析PDF年报...")
        pdf_data = self.pdf_parser.parse(pdf_path)
        self.analysis_context["pdf_text"] = pdf_data["full_text"]
        self.analysis_context["financial_data"] = pdf_data["financial_tables"]
        logger.info(f"PDF解析完成，提取文字 {len(pdf_data['full_text'])} 字符")
        
        # 步骤2: 财务指标计算
        logger.info("[2/5] 正在计算财务指标...")
        financial_metrics = self.financial_analyzer.analyze(pdf_data["financial_tables"])
        self.analysis_context["financial_metrics"] = financial_metrics
        logger.info(f"计算完成，共 {len(financial_metrics)} 项指标")
        
        # 步骤3: 会计操纵检测（核心步骤，使用完整PDF上下文）
        logger.info("[3/5] 正在进行会计操纵检测（100万Token上下文深度分析）...")
        manipulation_signals = self._detect_manipulation(pdf_data["full_text"], financial_metrics)
        self.analysis_context["manipulation_signals"] = manipulation_signals
        logger.info(f"检测完成，发现 {len(manipulation_signals)} 个风险信号")
        
        # 步骤4: 行业对比
        logger.info("[4/5] 正在进行行业对比分析...")
        industry_comparison = self.industry_comparator.compare(financial_metrics)
        self.analysis_context["industry_comparison"] = industry_comparison
        logger.info("行业对比完成")
        
        # 步骤5: 风险评估与报告生成
        logger.info("[5/5] 正在生成分析报告...")
        risk_assessment = self._assess_risk(manipulation_signals, financial_metrics)
        self.analysis_context["risk_assessment"] = risk_assessment
        
        report = self.report_generator.generate(
            financial_metrics=financial_metrics,
            manipulation_signals=manipulation_signals,
            industry_comparison=industry_comparison,
            risk_assessment=risk_assessment
        )
        
        # 计算总耗时
        duration = datetime.now() - start_time
        logger.info(f"分析完成，总耗时: {duration}")
        
        return {
            "report": report,
            "financial_metrics": financial_metrics,
            "manipulation_signals": manipulation_signals,
            "industry_comparison": industry_comparison,
            "risk_assessment": risk_assessment,
            "overall_score": risk_assessment.get("overall_score", 0),
            "risk_level": risk_assessment.get("risk_level", "未知"),
            "duration": str(duration)
        }
    
    def _detect_manipulation(self, full_text: str, financial_metrics: Dict) -> List[Dict]:
        """
        使用100万Token上下文进行会计操纵检测
        
        这是FinLens的核心功能，利用MiMo-V2.5的完整上下文能力
        深度理解年报全文，发现跨章节的关联异常。
        """
        # 构建检测提示词
        prompt = MANIPULATION_DETECTION_PROMPT.format(
            company_name=self.company_name,
            industry=self.industry,
            financial_metrics=json.dumps(financial_metrics, ensure_ascii=False, indent=2),
            pdf_text=full_text[:500000]  # 限制字数但仍保留大量上下文
        )
        
        # 调用LLM进行深度分析
        response = self._call_llm(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3
        )
        
        # 解析响应
        try:
            # 尝试提取JSON部分
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end]
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end]
            
            signals = json.loads(response)
            
            # 确保返回的是列表
            if isinstance(signals, dict) and "signals" in signals:
                return signals["signals"]
            return signals
            
        except json.JSONDecodeError:
            logger.warning("LLM响应JSON解析失败，使用备用解析")
            return self._parse_manipulation_fallback(response, financial_metrics)
    
    def _parse_manipulation_fallback(self, response: str, financial_metrics: Dict) -> List[Dict]:
        """备用解析方法，当LLM响应不是标准JSON时使用"""
        signals = []
        
        # 简单的关键词检测
        high_risk_keywords = [
            "非标", "保留意见", "无法表示", "否定意见",
            "应收账款异常", "存货积压", "现金流背离"
        ]
        medium_risk_keywords = [
            "变更会计政策", "关联交易", "商誉减值",
            "其他应收款", "预付款项"
        ]
        
        response_lower = response.lower()
        
        for keyword in high_risk_keywords:
            if keyword in response_lower:
                signals.append({
                    "type": self._classify_signal_type(keyword),
                    "level": "高风险",
                    "description": f"检测到风险信号: {keyword}",
                    "evidence": "LLM深度分析发现",
                    "recommendation": "建议深入核实"
                })
        
        for keyword in medium_risk_keywords:
            if keyword in response_lower:
                signals.append({
                    "type": self._classify_signal_type(keyword),
                    "level": "中风险",
                    "description": f"存在疑点: {keyword}",
                    "evidence": "LLM深度分析发现",
                    "recommendation": "建议保持关注"
                })
        
        return signals if signals else [{"type": "general", "level": "低风险", "description": "未发现明显异常信号", "evidence": "", "recommendation": "财务状况基本正常"}]
    
    def _classify_signal_type(self, keyword: str) -> str:
        """将关键词映射到信号类型"""
        mapping = {
            "非标": "audit_opinion",
            "保留意见": "audit_opinion",
            "无法表示": "audit_opinion",
            "否定意见": "audit_opinion",
            "应收账款异常": "receivable_anomaly",
            "存货积压": "inventory_anomaly",
            "现金流背离": "cash_flow_anomaly",
            "变更会计政策": "accounting_change",
            "关联交易": "related_party",
            "商誉减值": "goodwill_impairment",
            "其他应收款": "other_receivable",
            "预付款项": "prepayment_anomaly"
        }
        return mapping.get(keyword, "general")
    
    def _assess_risk(self, manipulation_signals: List[Dict], financial_metrics: Dict) -> Dict:
        """
        综合评估风险等级
        
        Args:
            manipulation_signals: 风险信号列表
            financial_metrics: 财务指标
        
        Returns:
            风险评估结果
        """
        # 构建评估提示词
        prompt = RISK_ASSESSMENT_PROMPT.format(
            company_name=self.company_name,
            financial_metrics=json.dumps(financial_metrics, ensure_ascii=False, indent=2),
            manipulation_signals=json.dumps(manipulation_signals, ensure_ascii=False, indent=2)
        )
        
        # 调用LLM评估
        response = self._call_llm(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2
        )
        
        # 解析响应
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end]
            
            assessment = json.loads(response)
            return assessment
            
        except json.JSONDecodeError:
            # 备用计算
            return self._calculate_risk_score(manipulation_signals, financial_metrics)
    
    def _calculate_risk_score(self, manipulation_signals: List[Dict], financial_metrics: Dict) -> Dict:
        """计算风险分数的备用方法"""
        score = 100  # 起始分数
        
        for signal in manipulation_signals:
            level = signal.get("level", "")
            if level == "高风险":
                score -= 25
            elif level == "中风险":
                score -= 10
            elif level == "低风险":
                score -= 5
        
        # 根据财务指标调整
        roe = financial_metrics.get("roe", 0)
        if roe < 0:
            score -= 20
        elif roe < 5:
            score -= 10
        
        debt_ratio = financial_metrics.get("debt_ratio", 0)
        if debt_ratio > 80:
            score -= 15
        elif debt_ratio > 70:
            score -= 10
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        # 确定风险等级
        if score >= 70:
            risk_level = "低风险"
        elif score >= 40:
            risk_level = "中风险"
        else:
            risk_level = "高风险"
        
        return {
            "overall_score": score,
            "risk_level": risk_level,
            "score_factors": {
                "signal_deduction": len(manipulation_signals) * 5,
                "financial_health": score
            },
            "summary": f"基于{len(manipulation_signals)}个风险信号和财务指标综合评估"
        }
    
    def run_interactive(self, pdf_path: str) -> Dict[str, Any]:
        """
        运行交互式分析模式
        
        先执行完整分析，然后进入问答环节
        """
        logger.info("启动交互式分析模式...")
        
        # 先执行完整分析
        result = self.run(pdf_path)
        
        print("\n" + "=" * 60)
        print("📊 初步分析完成，现在可以提问关于年报的问题")
        print("=" * 60)
        print("提示: 输入 'quit' 或 'exit' 退出交互模式\n")
        
        # 进入问答循环
        while True:
            try:
                question = input("\n❓ 您的问题: ").strip()
                
                if question.lower() in ["quit", "exit", "q", "退出"]:
                    print("\n感谢使用FinLens，再见！")
                    break
                
                if not question:
                    continue
                
                # 回答问题
                answer = self.answer_question(question, pdf_path)
                print("\n📝 回答:")
                print("-" * 40)
                print(answer)
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n\n已退出交互模式")
                break
        
        return result
    
    def answer_question(self, question: str, pdf_path: str) -> str:
        """
        回答关于年报的问题
        
        Args:
            question: 用户问题
            pdf_path: PDF文件路径（用于补充上下文）
        
        Returns:
            回答文本
        """
        # 获取PDF文本（如果还没有）
        if not self.analysis_context.get("pdf_text"):
            pdf_data = self.pdf_parser.parse(pdf_path)
            self.analysis_context["pdf_text"] = pdf_data["full_text"]
        
        # 构建问答提示词
        context_summary = self._build_context_summary()
        prompt = QA_PROMPT.format(
            company_name=self.company_name,
            question=question,
            context_summary=context_summary,
            pdf_text=self.analysis_context["pdf_text"][:500000]
        )
        
        # 调用LLM回答
        response = self._call_llm(
            messages=[
                {"role": "user", "content": prompt}
            ],
            system_prompt=SYSTEM_PROMPT,
            temperature=0.4
        )
        
        # 记录对话历史
        self.analysis_context["conversation_history"].append({
            "question": question,
            "answer": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
