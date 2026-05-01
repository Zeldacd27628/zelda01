# 工具函数模块
# 各类辅助函数

"""
FinLens工具函数集合
"""

import re
import sys
from typing import Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

# 尝试导入loguru（如果可用）
try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logger = logging.getLogger("FinLens")


def setup_logging(level: str = "INFO") -> Any:
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        logger实例
    """
    if LOGURU_AVAILABLE:
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
                   "<level>{message}</level>",
            colorize=True
        )
        
        return logger
    else:
        # 使用标准logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s"
        )
        return logging.getLogger("FinLens")


def clean_text(text: str) -> str:
    """
    清理文本，去除多余空白字符
    
    Args:
        text: 原始文本
    
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    # 恢复段落分隔
    text = text.replace(' . ', '.\n')
    text = text.replace('。 ', '。\n')
    
    return text


def parse_financial_number(text: str) -> Optional[float]:
    """
    解析财务报表中的数字
    
    支持格式：
    - 普通数字: 1234567.89
    - 千元格式: 1,234,567.89
    - 中文万元: 1234.56万
    - 中文亿元: 12.34亿
    - 带括号负数: (1234) 表示 -1234
    
    Args:
        text: 数字字符串
    
    Returns:
        解析后的数值，如果解析失败返回None
    """
    if not text:
        return None
    
    # 转换为字符串
    text = str(text).strip()
    
    # 处理空值标记
    if any(marker in text for marker in ['—', '—', '--', 'N/A', 'NA', '']):
        return None
    
    # 处理括号（表示负数）
    is_negative = False
    if '(' in text and ')' in text:
        is_negative = True
        text = re.sub(r'[()]', '', text)
    
    # 去除货币符号和其他符号
    text = re.sub(r'[¥$,，、]', '', text)
    
    # 提取数字部分
    # 处理中文单位
    chinese_units = {
        '万': 10000,
        '亿': 100000000,
        '千': 1000,
        '百': 100
    }
    
    unit = 1
    for unit_name, unit_value in chinese_units.items():
        if unit_name in text:
            text = text.replace(unit_name, '')
            unit = unit_value
            break
    
    # 移除逗号
    text = text.replace(',', '')
    
    # 提取数字
    match = re.search(r'[-+]?\d+\.?\d*', text)
    
    if match:
        try:
            value = float(match.group()) * unit
            return -value if is_negative else value
        except ValueError:
            return None
    
    return None


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认返回值（当除数为零时）
    
    Returns:
        除法结果或默认值
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_percentage(value: float, base: float, default: float = 0.0) -> float:
    """
    计算百分比
    
    Args:
        value: 数值
        base: 基数
        default: 默认返回值
    
    Returns:
        百分比值
    """
    if base == 0:
        return default
    return (value / base) * 100


def format_number(value: Union[int, float], precision: int = 2) -> str:
    """
    格式化数字用于显示
    
    Args:
        value: 数值
        precision: 小数位数
    
    Returns:
        格式化后的字符串
    """
    if value is None:
        return "N/A"
    
    if isinstance(value, int):
        return f"{value:,}"
    
    return f"{value:,.{precision}f}"


def format_percentage(value: float, precision: int = 2) -> str:
    """
    格式化百分比用于显示
    
    Args:
        value: 百分比值（如 25.5 表示 25.5%）
        precision: 小数位数
    
    Returns:
        格式化后的百分比字符串
    """
    if value is None:
        return "N/A"
    
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{precision}f}%"


def format_duration(duration: timedelta) -> str:
    """
    格式化时长用于显示
    
    Args:
        duration: timedelta对象
    
    Returns:
        格式化后的时长字符串
    """
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}秒"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}分{seconds}秒"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}小时{minutes}分"


def print_banner():
    """打印项目横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   █████╗ ██╗██████╗ ███████╗██╗   ██╗██████╗ ███████╗         ║
║  ██╔══██╗██║██╔══██╗██╔════╝██║   ██║██╔══██╗██╔════╝         ║
║  ███████║██║██████╔╝███████╗██║   ██║██████╔╝███████╗         ║
║  ██╔══██║██║██╔══██╗╚════██║██║   ██║██╔══██╗╚════██║         ║
║  ██║  ██║██║██████╔╝███████║╚██████╔╝██████╔╝███████║         ║
║  ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝         ║
║                                                                  ║
║  ───────────────────────────────────────────────────────────    ║
║           A股财报深度透视Agent | Financial Report Deep Dive      ║
║  ───────────────────────────────────────────────────────────    ║
║                                                                  ║
║  📊 核心能力:                                                    ║
║     • 100万Token超长上下文深度分析                                ║
║     • 会计操纵信号智能检测                                        ║
║     • 财务健康度综合评分                                          ║
║     • 行业对比横向分析                                            ║
║                                                                  ║
║  Powered by MiMo-V2.5-Pro                                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
    
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
    
    Returns:
        Path对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """
    获取项目根目录
    
    Returns:
        项目根目录Path对象
    """
    return Path(__file__).parent.parent


def merge_dicts(*dicts: dict) -> dict:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
    
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def calculate_growth_rate(current: float, prior: float) -> Optional[float]:
    """
    计算增长率
    
    Args:
        current: 当期值
        prior: 上期值
    
    Returns:
        增长率（百分比）
    """
    if prior == 0:
        return None
    return ((current - prior) / prior) * 100


def round_to_precision(value: float, precision: int = 2) -> float:
    """
    四舍五入到指定精度
    
    Args:
        value: 数值
        precision: 小数位数
    
    Returns:
        四舍五入后的值
    """
    return round(value, precision)


def is_valid_pdf_path(path: str) -> bool:
    """
    检查是否为有效的PDF文件路径
    
    Args:
        path: 文件路径
    
    Returns:
        是否有效
    """
    p = Path(path)
    return p.exists() and p.suffix.lower() == '.pdf' and p.stat().st_size > 0


def extract_year_from_text(text: str) -> Optional[int]:
    """
    从文本中提取年份
    
    Args:
        text: 文本
    
    Returns:
        年份或None
    """
    # 匹配20xx年的格式
    match = re.search(r'20\d{2}年?', text)
    if match:
        year_str = match.group().replace('年', '')
        try:
            return int(year_str)
        except ValueError:
            pass
    return None


class ProgressTracker:
    """简单的进度跟踪器"""
    
    def __init__(self, total: int, description: str = "进度"):
        """
        初始化进度跟踪器
        
        Args:
            total: 总数
            description: 描述
        """
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        percentage = (self.current / self.total) * 100
        bar_length = 30
        filled = int(bar_length * self.current / self.total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r{self.description}: [{bar}] {self.current}/{self.total} ({percentage:.1f}%)", end="")
        
        if self.current >= self.total:
            print()
    
    def finish(self):
        """完成"""
        self.current = self.total
        self.update(0)
