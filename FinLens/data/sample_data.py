# FinLens 示例数据
# 本目录用于存放测试数据

"""
目录用途：
- annual_reports/: 存放年报PDF文件
- output/: 存放分析报告输出
- cache/: 存放缓存数据
"""

# 示例：贵州茅台2023年简化财务数据
SAMPLE_FINANCIAL_DATA = {
    "company_name": "贵州茅台",
    "industry": "白酒",
    "report_year": 2023,
    
    # 资产负债表数据（单位：亿元）
    "balance_sheet": {
        "total_assets": 2544.52,
        "current_assets": 1646.32,
        "fixed_assets": 254.12,
        "intangible_assets": 12.45,
        "goodwill": 0,
        "accounts_receivable": 1.23,
        "other_receivables": 2.34,
        "inventory": 388.54,
        "prepaid_expenses": 5.67,
        "total_liabilities": 245.67,
        "current_liabilities": 234.56,
        "long_term_liabilities": 11.11,
        "accounts_payable": 23.45,
        "other_payables": 45.67,
        "total_equity": 2298.85
    },
    
    # 利润表数据（单位：亿元）
    "income_statement": {
        "revenue": 1476.19,
        "operating_cost": 121.54,
        "gross_profit": 1354.65,
        "selling_expense": 25.47,
        "admin_expense": 85.23,
        "finance_expense": -8.92,
        "rd_expense": 0,
        "operating_profit": 1036.60,
        "total_profit": 1038.84,
        "net_profit": 747.53,
        "net_profit_parent": 747.53
    },
    
    # 现金流量表数据（单位：亿元）
    "cash_flow": {
        "operating_cash_flow": 665.93,
        "investing_cash_flow": -45.67,
        "financing_cash_flow": -395.23,
        "cash_increase": 225.03,
        "ending_cash": 707.45
    },
    
    # 上期数据（用于计算增长率）
    "prior_year": {
        "revenue": 1275.56,
        "net_profit": 627.16,
        "total_assets": 2215.87,
        "accounts_receivable": 0.98,
        "inventory": 334.05
    }
}

# 示例行业基准数据
SAMPLE_INDUSTRY_BENCHMARKS = {
    "白酒": {
        "gross_margin": 75.0,
        "net_margin": 30.0,
        "roe": 25.0,
        "debt_ratio": 30.0,
        "current_ratio": 2.5,
        "receivable_turnover": 30.0,
        "inventory_turnover": 0.5
    }
}

# 示例风险信号
SAMPLE_MANIPULATION_SIGNALS = [
    {
        "type": "receivable_anomaly",
        "level": "低风险",
        "title": "应收账款与营收增速基本匹配",
        "description": "应收账款增长25.5%，与营收增速基本同步，无明显异常",
        "evidence": ["营收增长15.7%", "应收账款增长25.5%"],
        "impact": "风险较低",
        "recommendation": "保持常规关注"
    }
]

if __name__ == "__main__":
    import json
    print("示例财务数据结构：")
    print(json.dumps(SAMPLE_FINANCIAL_DATA, indent=2, ensure_ascii=False))
