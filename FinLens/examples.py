# FinLens 使用示例
# 示例代码展示如何使用FinLens进行财务分析

"""
本文件展示FinLens的多种使用方式：
1. 基础分析模式
2. 交互式问答模式
3. 自定义分析配置
4. 直接调用各模块
"""

# ============================================
# 示例1：基础分析模式
# ============================================

def example_basic_analysis():
    """
    基础分析模式 - 对单个年报进行完整分析
    """
    from agent.workflow import FinLensWorkflow
    from config import MIMO_API_KEY
    
    # 初始化工作流
    workflow = FinLensWorkflow(
        api_key=MIMO_API_KEY,
        company_name="贵州茅台",
        industry="白酒"
    )
    
    # 执行分析
    result = workflow.run("./data/annual_report.pdf")
    
    # 输出结果
    print("=" * 60)
    print("分析完成!")
    print(f"风险等级: {result['risk_level']}")
    print(f"综合评分: {result['overall_score']}")
    print("=" * 60)
    
    # 保存报告
    with open("./output/report.md", "w", encoding="utf-8") as f:
        f.write(result["report"])
    
    return result


# ============================================
# 示例2：交互式问答模式
# ============================================

def example_interactive_mode():
    """
    交互式问答模式 - 分析后可提问关于年报的问题
    """
    from agent.workflow import FinLensWorkflow
    
    workflow = FinLensWorkflow(
        api_key="your-api-key",
        company_name="五粮液",
        industry="白酒"
    )
    
    # 启动交互模式
    # 用户可以在命令行提问，系统会基于年报内容回答
    workflow.run_interactive("./data/wuliangye_annual_report.pdf")
    
    # 示例问题：
    # - "公司是否存在财务造假风险？"
    # - "应收账款增长是否异常？"
    # - "现金流状况如何？"
    # - "与行业平均水平相比表现如何？"


# ============================================
# 示例3：单独使用各模块
# ============================================

def example_modular_usage():
    """
    单独使用各分析模块
    """
    from parsers.pdf_parser import PDFParser
    from analyzers.financial import FinancialAnalyzer
    from analyzers.detection import ManipulationDetector
    from analyzers.comparison import IndustryComparator
    from generators.report import ReportGenerator
    
    # 1. PDF解析
    parser = PDFParser()
    pdf_data = parser.parse("./data/annual_report.pdf")
    full_text = pdf_data["full_text"]
    financial_tables = pdf_data["financial_tables"]
    
    # 2. 财务指标计算
    financial_analyzer = FinancialAnalyzer()
    metrics = financial_analyzer.analyze(financial_tables)
    
    # 3. 会计操纵检测
    detector = ManipulationDetector()
    signals = detector.detect(full_text, metrics)
    
    # 4. 行业对比
    comparator = IndustryComparator("白酒")
    comparison = comparator.compare(metrics)
    
    # 5. 生成报告
    report_gen = ReportGenerator("贵州茅台", "白酒")
    report = report_gen.generate(metrics, signals, comparison, {
        "risk_level": "低风险",
        "overall_score": 85,
        "summary": "财务状况良好"
    })
    
    print(report)


# ============================================
# 示例4：批量分析多家公司
# ============================================

def example_batch_analysis():
    """
    批量分析多家公司
    """
    from agent.workflow import FinLensWorkflow
    from pathlib import Path
    from datetime import datetime
    
    # 公司列表
    companies = [
        {"name": "贵州茅台", "industry": "白酒", "pdf": "maotai.pdf"},
        {"name": "五粮液", "industry": "白酒", "pdf": "wuliangye.pdf"},
        {"name": "泸州老窖", "industry": "白酒", "pdf": "luzhou.pdf"},
    ]
    
    results = []
    
    for company in companies:
        try:
            print(f"\n正在分析: {company['name']}...")
            
            workflow = FinLensWorkflow(
                api_key="your-api-key",
                company_name=company["name"],
                industry=company["industry"]
            )
            
            result = workflow.run(f"./data/{company['pdf']}")
            
            results.append({
                "company": company["name"],
                "risk_level": result["risk_level"],
                "score": result["overall_score"]
            })
            
            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            Path(f"./output/{company['name']}_{timestamp}.md").write_text(
                result["report"], encoding="utf-8"
            )
            
        except Exception as e:
            print(f"分析失败: {company['name']} - {e}")
            results.append({
                "company": company["name"],
                "error": str(e)
            })
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("批量分析汇总")
    print("=" * 60)
    for r in results:
        if "error" in r:
            print(f"{r['company']}: 分析失败")
        else:
            print(f"{r['company']}: {r['risk_level']} ({r['score']}分)")


# ============================================
# 示例5：使用示例数据进行测试
# ============================================

def example_with_sample_data():
    """
    使用示例数据进行测试（无需真实PDF）
    """
    from analyzers.financial import FinancialAnalyzer
    from analyzers.detection import ManipulationDetector
    from analyzers.comparison import IndustryComparator
    from generators.report import ReportGenerator
    from data.sample_data import SAMPLE_FINANCIAL_DATA, SAMPLE_INDUSTRY_BENCHMARKS
    
    # 提取数据
    financial_data = {
        "balance_sheet": [{"data": []}],
        "income_statement": [{"data": []}],
        "cash_flow": [{"data": []}]
    }
    
    bs = SAMPLE_FINANCIAL_DATA["balance_sheet"]
    is_ = SAMPLE_FINANCIAL_DATA["income_statement"]
    cf = SAMPLE_FINANCIAL_DATA["cash_flow"]
    prior = SAMPLE_FINANCIAL_DATA["prior_year"]
    
    # 计算增长率
    revenue_growth = ((is_["revenue"] - prior["revenue"]) / prior["revenue"]) * 100
    receivable_growth = ((bs["accounts_receivable"] - prior["accounts_receivable"]) / prior["accounts_receivable"]) * 100
    
    # 构建财务指标
    metrics = {
        # 盈利能力
        "gross_margin": ((is_["revenue"] - is_["operating_cost"]) / is_["revenue"]) * 100,
        "net_margin": (is_["net_profit"] / is_["revenue"]) * 100,
        "roe": (is_["net_profit"] / bs["total_equity"]) * 100,
        "roa": (is_["net_profit"] / bs["total_assets"]) * 100,
        
        # 偿债能力
        "debt_ratio": (bs["total_liabilities"] / bs["total_assets"]) * 100,
        "current_ratio": bs["current_assets"] / bs["current_liabilities"],
        
        # 运营效率
        "inventory_turnover": is_["operating_cost"] / bs["inventory"],
        "receivable_turnover": is_["revenue"] / bs["accounts_receivable"],
        
        # 现金流
        "cash_flow_ratio": cf["operating_cash_flow"] / is_["net_profit"],
        
        # 成长性
        "revenue_growth": revenue_growth,
        "profit_growth": ((is_["net_profit"] - prior["net_profit"]) / prior["net_profit"]) * 100,
        "receivable_growth": receivable_growth,
        "inventory_growth": ((bs["inventory"] - prior["inventory"]) / prior["inventory"]) * 100,
        
        # 占比指标
        "goodwill_ratio": (bs["goodwill"] / bs["total_assets"]) * 100,
        "other_receivable_ratio": (bs["other_receivables"] / bs["total_assets"]) * 100,
    }
    
    # 检测操纵信号
    detector = ManipulationDetector()
    signals = detector.detect("", metrics)  # 空文本，仅用规则检测
    
    # 行业对比
    comparator = IndustryComparator("白酒")
    comparison = comparator.compare(metrics)
    
    # 风险评估
    high_risk_count = len([s for s in signals if s.get("level") == "高风险"])
    medium_risk_count = len([s for s in signals if s.get("level") == "中风险"])
    
    if high_risk_count >= 2:
        risk_level = "高风险"
        score = max(30, 100 - high_risk_count * 25 - medium_risk_count * 10)
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        risk_level = "中风险"
        score = max(40, 70 - medium_risk_count * 10)
    else:
        risk_level = "低风险"
        score = 80 + (5 if high_risk_count == 0 else 0)
    
    risk_assessment = {
        "risk_level": risk_level,
        "overall_score": score,
        "summary": f"基于{high_risk_count}个高风险信号和{medium_risk_count}个中风险信号的综合评估"
    }
    
    # 生成报告
    report_gen = ReportGenerator("贵州茅台", "白酒")
    report = report_gen.generate(metrics, signals, comparison, risk_assessment)
    
    print(report)
    
    return {
        "metrics": metrics,
        "signals": signals,
        "comparison": comparison,
        "risk_assessment": risk_assessment,
        "report": report
    }


# ============================================
# 主函数
# ============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("请选择运行模式:")
        print("1. 基础分析 (需要真实PDF)")
        print("2. 交互模式 (需要真实PDF)")
        print("3. 模块演示")
        print("4. 批量分析 (需要真实PDF)")
        print("5. 示例数据测试")
        print("\n输入数字选择，或直接运行示例数据测试...")
        mode = input("选择: ").strip() or "5"
    
    if mode == "1":
        example_basic_analysis()
    elif mode == "2":
        example_interactive_mode()
    elif mode == "3":
        example_modular_usage()
    elif mode == "4":
        example_batch_analysis()
    else:
        print("运行示例数据测试...")
        example_with_sample_data()
