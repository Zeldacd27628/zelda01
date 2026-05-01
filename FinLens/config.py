# FinLens 配置文件
# A股财报深度透视Agent

import os
from pathlib import Path

# ============================================
# 项目路径配置
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / ".cache"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# ============================================
# MiMo API 配置
# ============================================
# 从环境变量或直接配置获取API密钥
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "YOUR_MIMO_API_KEY_HERE")
MIMO_BASE_URL = "https://api.minimax.chat/v1"
MIMO_MODEL = "MiMo-V2.5-Pro"

# API请求参数
API_TIMEOUT = 120           # 请求超时时间（秒）
MAX_RETRIES = 3             # 最大重试次数
TEMPERATURE = 0.3           # 生成温度（较低值保持稳定性）
TOP_P = 0.9                 # Top-p采样
MAX_TOKENS = 8192           # 单次最大输出Token

# ============================================
# 财务分析配置
# ============================================
# 异常检测阈值（可根据行业调整）
THRESHOLDS = {
    # 应收账款异常
    "receivable_growth_diff": 30,      # 应收账款增速与营收增速差异超过30%为异常
    
    # 存货异常
    "inventory_growth_threshold": 50,  # 存货增长超过50%为异常
    
    # 现金流背离
    "cash_flow_diff": 0.5,             # 经营现金流与净利润比值低于0.5长期为异常
    
    # 关联交易
    "related_party_ratio": 0.3,        # 关联交易占比超过30%为高风险
    
    # 其他应收款
    "other_receivable_ratio": 0.1,     # 其他应收款占比超过10%为异常
    
    # 商誉
    "goodwill_ratio": 0.2,             # 商誉占比超过20%需关注
    
    # 研发资本化
    "rd_capitalization_ratio": 0.5,    # 研发资本化率超过50%需关注
    
    # 预付款项
    "prepayment_growth": 100,          # 预付款项增长超过100%为异常
}

# 风险等级分数划分
RISK_SCORES = {
    "high_risk": 70,      # 高风险阈值
    "medium_risk": 40,    # 中风险阈值
    "low_risk": 0         # 低风险
}

# ============================================
# 行业分类配置
# ============================================
INDUSTRY_CATEGORIES = {
    "白酒": ["贵州茅台", "五粮液", "泸州老窖", "洋河股份", "山西汾酒", "古井贡酒"],
    "房地产": ["万科A", "保利发展", "招商蛇口", "金地集团", "华侨城A"],
    "银行": ["工商银行", "建设银行", "农业银行", "中国银行", "招商银行"],
    "保险": ["中国平安", "中国人寿", "中国太保", "新华保险"],
    "医药": ["恒瑞医药", "药明康德", "迈瑞医疗", "爱尔眼科"],
    "科技": ["腾讯控股", "阿里巴巴", "百度", "京东", "美团"],
    "制造业": ["比亚迪", "宁德时代", "海尔智家", "美的集团"],
    "电力": ["长江电力", "华能国际", "国电电力"],
    "煤炭": ["中国神华", "陕西煤业", "中煤能源"],
    "钢铁": ["宝钢股份", "鞍钢股份", "华菱钢铁"],
}

# 行业平均财务指标（简化示例）
INDUSTRY_BENCHMARKS = {
    "白酒": {
        "gross_margin": 75.0,
        "net_margin": 30.0,
        "roe": 25.0,
        "debt_ratio": 30.0,
        "current_ratio": 2.5,
        "receivable_turnover": 30.0,
    },
    "房地产": {
        "gross_margin": 25.0,
        "net_margin": 10.0,
        "roe": 15.0,
        "debt_ratio": 80.0,
        "current_ratio": 1.3,
        "receivable_turnover": 10.0,
    },
    "银行": {
        "gross_margin": None,
        "net_margin": None,
        "roe": 12.0,
        "debt_ratio": 92.0,
        "current_ratio": None,
        "receivable_turnover": None,
    },
    "医药": {
        "gross_margin": 60.0,
        "net_margin": 15.0,
        "roe": 18.0,
        "debt_ratio": 40.0,
        "current_ratio": 2.0,
        "receivable_turnover": 5.0,
    },
    "制造业": {
        "gross_margin": 25.0,
        "net_margin": 8.0,
        "roe": 15.0,
        "debt_ratio": 55.0,
        "current_ratio": 1.5,
        "receivable_turnover": 5.0,
    },
    "default": {
        "gross_margin": 30.0,
        "net_margin": 10.0,
        "roe": 15.0,
        "debt_ratio": 50.0,
        "current_ratio": 1.5,
        "receivable_turnover": 5.0,
    }
}

# ============================================
# 日志配置
# ============================================
LOG_LEVEL = "INFO"
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>"
)
LOG_ROTATION = "100 MB"
LOG_RETENTION = "30 days"

# ============================================
# 缓存配置
# ============================================
CACHE_ENABLED = True
CACHE_TTL = 86400 * 7  # 缓存有效期：7天
CACHE_MAX_SIZE = 1024 * 1024 * 100  # 100MB

# ============================================
# PDF解析配置
# ============================================
PDF_SETTINGS = {
    "extract_tables": True,          # 提取表格
    "extract_images": False,         # 提取图片
    "page_start": None,             # 从第几页开始（None=全部）
    "page_end": None,               # 从第几页结束（None=全部）
    "password": None,               # PDF密码（如有）
}

# ============================================
# 报告生成配置
# ============================================
REPORT_SETTINGS = {
    "include_raw_data": True,       # 包含原始数据
    "include_comparison": True,     # 包含行业对比
    "include_risk_signals": True,   # 包含风险信号
    "include_recommendations": True, # 包含建议
    "output_format": "markdown",     # 输出格式
}

# ============================================
# Agent配置
# ============================================
AGENT_CONFIG = {
    "max_iterations": 10,           # 最大迭代次数
    "reflection_threshold": 0.7,     # 反思阈值
    "confidence_threshold": 0.8,     # 置信度阈值
    "enable_critique": True,        # 启用批评机制
}
