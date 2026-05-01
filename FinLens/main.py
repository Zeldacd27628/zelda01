# FinLens 主入口
# A股财报深度透视Agent

"""
FinLens - A股财报深度透视Agent

利用MiMo-V2.5-Pro的100万Token超长上下文，对A股上市公司年报
进行深度分析，检测会计操纵信号，生成财务健康真实度评分。
"""

import argparse
import sys
import warnings
from pathlib import Path
from datetime import datetime

# 抑制警告
warnings.filterwarnings("ignore")

# 导入项目模块
from agent.workflow import FinLensWorkflow
from config import OUTPUT_DIR, LOG_LEVEL
from utils.helpers import setup_logging, print_banner, format_duration

# 设置日志
logger = setup_logging(LOG_LEVEL)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog="FinLens",
        description="A股财报深度透视Agent - 利用100万Token上下文深度分析年报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础分析
  python main.py --pdf_path ./annual_report.pdf --company_name "贵州茅台" --industry "白酒"
  
  # 交互模式
  python main.py --pdf_path ./report.pdf --company_name "五粮液" --industry "白酒" --interactive
  
  # 自定义输出
  python main.py --pdf_path ./report.pdf --company_name "万科A" --industry "房地产" --output_dir ./results
        """
    )
    
    parser.add_argument(
        "--pdf_path", 
        type=str, 
        required=True,
        help="年报PDF文件路径"
    )
    
    parser.add_argument(
        "--company_name", 
        type=str, 
        required=True,
        help="公司名称"
    )
    
    parser.add_argument(
        "--industry", 
        type=str, 
        required=True,
        help="所属行业（如：白酒、医药、银行等）"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default=str(OUTPUT_DIR),
        help=f"输出目录（默认：{OUTPUT_DIR}）"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="启用交互式问答模式"
    )
    
    parser.add_argument(
        "--api_key", 
        type=str, 
        default=None,
        help="MiMo API密钥（也可在config.py中配置）"
    )
    
    parser.add_argument(
        "--export_json", 
        action="store_true",
        help="同时导出JSON格式结果"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="显示详细日志"
    )
    
    return parser.parse_args()


def validate_inputs(args):
    """验证输入参数"""
    errors = []
    
    # 检查PDF文件
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        errors.append(f"PDF文件不存在: {args.pdf_path}")
    elif not pdf_path.suffix.lower() == ".pdf":
        errors.append(f"文件不是PDF格式: {args.pdf_path}")
    elif pdf_path.stat().st_size == 0:
        errors.append(f"PDF文件为空: {args.pdf_path}")
    
    # 检查输出目录
    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"无法创建输出目录: {e}")
    
    return errors


def save_report(report: str, output_dir: Path, company_name: str, format: str = "md"):
    """保存报告到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company_name}_{timestamp}.{format}"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"报告已保存: {filepath}")
    return filepath


def save_json_report(data: dict, output_dir: Path, company_name: str):
    """保存JSON格式报告"""
    import json
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company_name}_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"JSON报告已保存: {filepath}")
    return filepath


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 打印横幅
    print_banner()
    
    # 验证输入
    errors = validate_inputs(args)
    if errors:
        logger.error("输入验证失败:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # 设置日志级别
    if args.verbose:
        logger.configure(extra={"verbosity": "DEBUG"})
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 确定API密钥
    api_key = args.api_key
    if not api_key:
        from config import MIMO_API_KEY
        api_key = MIMO_API_KEY
        if api_key == "YOUR_MIMO_API_KEY_HERE":
            logger.error("请在config.py中配置MIMO_API_KEY，或使用--api_key参数")
            sys.exit(1)
    
    logger.info(f"开始分析: {args.company_name} ({args.industry})")
    logger.info(f"PDF文件: {args.pdf_path}")
    
    try:
        # 初始化工作流
        workflow = FinLensWorkflow(
            api_key=api_key,
            company_name=args.company_name,
            industry=args.industry,
            output_dir=str(output_dir)
        )
        
        # 执行分析
        start_time = datetime.now()
        
        if args.interactive:
            # 交互模式
            logger.info("启动交互模式...")
            result = workflow.run_interactive(args.pdf_path)
        else:
            # 普通分析模式
            logger.info("开始执行财务分析...")
            result = workflow.run(args.pdf_path)
        
        duration = datetime.now() - start_time
        
        # 保存报告
        report_path = save_report(
            result["report"], 
            output_dir, 
            args.company_name
        )
        
        # 保存JSON（如果需要）
        if args.export_json:
            save_json_report(result, output_dir, args.company_name)
        
        # 打印摘要
        logger.info("=" * 60)
        logger.info("分析完成!")
        logger.info(f"耗时: {format_duration(duration)}")
        logger.info(f"报告: {report_path}")
        logger.info(f"风险等级: {result.get('risk_level', 'N/A')}")
        logger.info(f"综合评分: {result.get('overall_score', 'N/A')}")
        logger.info("=" * 60)
        
        # 打印简短报告预览
        print("\n" + "=" * 60)
        print("📊 报告预览")
        print("=" * 60)
        preview_lines = result["report"].split("\n")[:50]
        print("\n".join(preview_lines))
        print("\n... (完整报告已保存)")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("用户中断分析")
        return 130
    except Exception as e:
        logger.error(f"分析过程出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
