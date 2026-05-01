# FinLens - A股财报深度透视Agent

<p align="center">
  <img src="https://img.shields.io/badge/Context%20Window-1M%20Tokens-blue?style=for-the-badge" alt="1M Tokens">
  <img src="https://img.shields.io/badge/LLM-MiMo--V2.5--Pro-orange?style=for-the-badge" alt="MiMo V2.5">
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge" alt="Python">
</p>

## 📖 项目背景

FinLens 是为 **小米MiMo Orbit百万亿Token创造者激励计划** 打造的专业级A股财报分析工具。项目利用 MiMo-V2.5-Pro 的 **100万Token超长上下文窗口**能力，对A股上市公司年报进行深度透视，检测会计操纵信号，生成财务健康真实度评分。

### 🎯 为什么需要100万Token上下文？

传统的财务分析工具存在以下痛点：

| 痛点 | 传统方案 | FinLens方案 |
|------|---------|-------------|
| 年报数据量 | 只能分析摘要/节选 | 完整解析200+页年报全文 |
| 上下文连贯性 | 分割处理丢失关联信息 | 完整阅读保持语义连贯 |
| 异常检测 | 依赖固定阈值规则 | 理解业务逻辑综合判断 |
| 跨章节关联 | 各部分独立分析 | 全文关联分析发现隐藏风险 |

**核心价值**：100万Token上下文让模型能够像专业审计师一样，完整阅读年报所有章节，理解公司业务的完整故事，发现跨章节的关联异常。

---

## 🚀 核心功能

### 1. PDF财报解析
- 自动解析A股上市公司年报PDF
- 智能提取财务报表数据（资产负债表、利润表、现金流量表）
- 结构化存储便于后续分析

### 2. 财务指标计算
- **盈利能力**：ROE、ROA、毛利率、净利率、EPS
- **偿债能力**：资产负债率、流动比率、速动比率
- **运营效率**：存货周转率、应收账款周转率、总资产周转率
- **成长性**：营收增长率、净利润增长率、资产增长率
- **现金流**：经营现金流/净利润比率、现金流肖像

### 3. 会计操纵检测（核心亮点）
基于100万Token上下文深度理解，检测以下风险信号：
- 📈 应收账款异常增长（远超营收增速）
- 📦 存货异常积压
- 💰 经营现金流与净利润长期背离
- 🔄 频繁变更会计政策/会计估计
- 🤝 关联交易占比过高
- 📋 其他应收款异常
- 💎 商誉减值时机可疑
- 🔬 研发费用资本化率异常
- 💳 预付款项异常增长
- ⚠️ 非标审计意见

### 4. 行业对比
- 同行业上市公司横向对比
- 偏离行业均值的异常指标智能标记
- 行业排名分析

### 5. 智能报告生成
- 结构化Markdown格式报告
- 风险信号分级预警
- 投资建议参考

---

## 🛠️ 技术架构

```
FinLens/
├── README.md
├── requirements.txt      # 依赖清单
├── config.py             # 配置文件
├── main.py               # 主入口
├── agent/
│   ├── workflow.py       # Agent工作流调度
│   └── prompts.py        # 提示词模板
├── parsers/
│   └── pdf_parser.py     # PDF解析模块
├── analyzers/
│   ├── financial.py      # 财务指标计算
│   ├── detection.py      # 会计操纵检测
│   └── comparison.py     # 行业对比
├── generators/
│   └── report.py         # 报告生成
└── utils/
    └── helpers.py        # 工具函数
```

---

## 📦 安装使用

### 环境要求
- Python 3.10+
- MiMo-V2.5-Pro API密钥

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/FinLens.git
cd FinLens

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API密钥
# 编辑 config.py 文件，填入你的 MiMo API Key

# 5. 运行分析
python main.py --pdf_path ./sample_report.pdf --company_name "贵州茅台" --industry "白酒"
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--pdf_path` | 年报PDF文件路径 | `./annual_report.pdf` |
| `--company_name` | 公司名称 | `"贵州茅台"` |
| `--industry` | 所属行业 | `"白酒"` |
| `--output_dir` | 输出目录 | `./output` |
| `--interactive` | 交互模式 | 启用问答 |

---

## 💡 使用示例

### 基础分析
```python
from agent.workflow import FinLensWorkflow

# 初始化工作流
workflow = FinLensWorkflow(
    api_key="your-mimo-api-key",
    company_name="贵州茅台",
    industry="白酒"
)

# 执行完整分析
result = workflow.run("./annual_report.pdf")

# 输出报告
print(result["report"])
```

### 交互式问答
```python
# 启用交互模式，询问关于财报的各类问题
workflow.run_interactive("./annual_report.pdf")
```

示例问答：
- "公司是否存在财务造假风险？"
- "应收账款增长是否异常？"
- "现金流状况如何？"
- "与行业平均水平相比表现如何？"

---

## 🎓 会计操纵检测原理

FinLens 的会计操纵检测不是简单的阈值判断，而是基于深度语义理解：

### 检测维度

1. **勾稽关系异常**
   - 财务报表内部逻辑验证
   - 附注与报表数据一致性检查
   - 同比变化的合理性判断

2. **业务逻辑异常**
   - 理解行业特性（季节性、周期性）
   - 业务模式与财务数据的匹配度
   - 收入确认方式的合理性

3. **时间序列异常**
   - 多期数据趋势分析
   - 异常拐点识别
   - 政策变更影响评估

4. **文本语义分析**
   - 管理层讨论与财务数据的一致性
   - 会计政策变更的披露质量
   - 审计意见的深层含义

### 风险分级

| 等级 | 信号强度 | 说明 |
|------|---------|------|
| 🔴 高风险 | 明确异常 | 多项指标高度异常，需重点关注 |
| 🟡 中风险 | 存在疑点 | 部分指标异常，建议深入核实 |
| 🟢 低风险 | 基本正常 | 指标在合理范围内 |

---

## 🔑 API配置

在 `config.py` 中配置：

```python
# MiMo API 配置
MIMO_API_KEY = "your-api-key-here"
MIMO_BASE_URL = "https://api.minimax.chat/v1"
MIMO_MODEL = "MiMo-V2.5-Pro"

# API参数
TEMPERATURE = 0.3
MAX_TOKENS = 8192
```

---

## 📊 输出示例

分析完成后，生成结构化报告：

```markdown
# 贵州茅台 - 财务健康分析报告

## 📋 基本信息
- **分析日期**: 2024-01-15
- **报告期**: 2023年年报
- **行业**: 白酒

## 📊 财务指标总览
| 指标 | 数值 | 行业均值 | 偏离度 |
|------|------|---------|--------|
| ROE | 32.5% | 25.1% | +29.5% |
| 毛利率 | 91.8% | 75.2% | +22.1% |
| ... | ... | ... | ... |

## ⚠️ 风险信号检测
### 🔴 高风险信号
1. **应收账款增速异常**: 应收账款增长45%，远超营收增速12%
2. ...

### 🟡 中风险信号
1. ...

## 📈 综合评分
- **财务健康度**: 85/100
- **风险等级**: 🟢 低风险
- **投资建议**: 财务状况稳健，建议关注...

## 💬 智能问答摘要
基于年报全文理解生成的问答分析...
```

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- **小米MiMo团队** - 提供100万Token超长上下文API
- **Coze平台** - 提供强大的Agent开发框架
- 所有参与测试和反馈的社区成员

---

<p align="center">
  <strong>Built with ❤️ for the MiMo Orbit Hackathon</strong>
</p>
