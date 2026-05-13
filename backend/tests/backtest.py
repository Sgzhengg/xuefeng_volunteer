"""
学锋志愿教练 - 推荐系统历史回溯测试脚本

功能：
1. 从录取数据中提取测试样本
2. 调用推荐接口进行回溯测试
3. 统计分析推荐准确性
4. 生成详细测试报告

使用方法：
    python backtest.py              # 完整测试（500条）
    python backtest.py --quick      # 快速测试（50条）
    python backtest.py --sample 200 # 自定义样本量
    python backtest.py --rerun      # 重新运行测试

作者：学锋志愿教练团队
日期：2025-01-09
版本：1.0.0
"""

import json
import random
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from collections import defaultdict

import requests
from tqdm import tqdm

# ==================== 配置常量 ====================

# API配置
API_BASE_URL = "http://localhost:8001"
RECOMMEND_ENDPOINT = f"{API_BASE_URL}/api/v1/recommendation/generate"
API_TIMEOUT = 30  # 30秒超时

# 数据文件路径（从backend目录运行）
DATA_DIR = Path(__file__).parent.parent / "data"
ADMISSION_DATA_FILE = DATA_DIR / "major_rank_data.json"
SCORE_RANK_FILE = DATA_DIR / "score_rank_tables.json"
OUTPUT_DIR = Path(__file__).parent / "results"

# 测试配置
DEFAULT_SAMPLE_SIZE = 500
QUICK_TEST_SAMPLE_SIZE = 50

# 位次段配置
RANK_RANGES = [
    {"name": "1-10000", "min": 1, "max": 10000, "ratio": 0.10, "description": "985/211顶尖段"},
    {"name": "10001-30000", "min": 10001, "max": 30000, "ratio": 0.15, "description": "211/重点段"},
    {"name": "30001-70000", "min": 30001, "max": 70000, "ratio": 0.25, "description": "一本段"},
    {"name": "70001-120000", "min": 70001, "max": 120000, "ratio": 0.25, "description": "二本段"},
    {"name": "120001-200000", "min": 120001, "max": 200000, "ratio": 0.15, "description": "民办/专科段"},
    {"name": "200001-350000", "min": 200001, "max": 350000, "ratio": 0.10, "description": "专科段"},
]

# 概率区间配置
PROBABILITY_RANGES = [
    {"name": "80%-100%", "min": 80, "max": 100},
    {"name": "60%-80%", "min": 60, "max": 80},
    {"name": "40%-60%", "min": 40, "max": 60},
    {"name": "20%-40%", "min": 20, "max": 40},
    {"name": "0%-20%", "min": 0, "max": 20},
]

# 默认科目配置
DEFAULT_SUBJECTS = ["物理", "化学", "生物"]
DEFAULT_PREFERENCE = "balanced"

# ==================== 日志配置 ====================

def setup_logging() -> logging.Logger:
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'backtest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ==================== 数据类定义 ====================

class TestRecord:
    """测试记录类"""

    def __init__(self, rank: int, university_id: str, university_name: str,
                 major_id: str, major_name: str, year: int):
        self.rank = rank
        self.university_id = university_id
        self.university_name = university_name
        self.major_id = major_id
        self.major_name = major_name
        self.year = year

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "rank": self.rank,
            "university_id": self.university_id,
            "university_name": self.university_name,
            "major_id": self.major_id,
            "major_name": self.major_name,
            "year": self.year
        }


class TestResult:
    """测试结果类"""

    def __init__(self, test_record: TestRecord):
        self.test_record = test_record
        self.recommendations = []
        self.university_hit = False
        self.exact_hit = False
        self.probability_if_found = None
        self.response_time = 0
        self.error = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "test_record": self.test_record.to_dict(),
            "university_hit": self.university_hit,
            "exact_hit": self.exact_hit,
            "probability_if_found": self.probability_if_found,
            "response_time": self.response_time,
            "recommendation_count": len(self.recommendations),
            "top10_recommendations": [
                f"{r.get('university_name', '')} - {r.get('major_name', '')}"
                for r in self.recommendations[:10]
            ],
            "error": self.error
        }

# ==================== 数据提取模块 ====================

def load_admission_data() -> List[Dict]:
    """
    加载录取数据

    Returns:
        录取数据列表
    """
    logger.info(f"正在加载数据文件: {ADMISSION_DATA_FILE}")

    if not ADMISSION_DATA_FILE.exists():
        logger.error(f"数据文件不存在: {ADMISSION_DATA_FILE}")
        raise FileNotFoundError(f"数据文件不存在: {ADMISSION_DATA_FILE}")

    try:
        with open(ADMISSION_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = data.get("major_rank_data", [])
        logger.info(f"数据加载完成，共 {len(records):,} 条记录")

        return records

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise
    except Exception as e:
        logger.error(f"加载数据文件失败: {e}")
        raise


def load_score_rank_table() -> Dict[int, int]:
    """
    从 score_rank_tables.json 加载广东2025年的位次到分数映射

    Returns:
        {rank: score} 字典，按排名到分数的映射
    """
    logger.info(f"正在加载分数-位次表: {SCORE_RANK_FILE}")

    if not SCORE_RANK_FILE.exists():
        logger.warning(f"一分一段表文件不存在: {SCORE_RANK_FILE}，将使用估算公式")
        return {}

    try:
        with open(SCORE_RANK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 结构: {"provinces": {"广东": {"2025": {"table": [{"score": 750, "rank": 819, "cumulative": 819}, ...]}}}}
        provinces_data = data.get("provinces", {})
        province_data = provinces_data.get("广东", {}).get("2025", {})
        scores_table = province_data.get("table", [])

        if not scores_table:
            logger.warning("未找到广东2025分数位次数据")
            return {}

        # 构建 rank -> score 映射
        # scores_table 结构: [{"score": 750, "rank": 819, "cumulative": 819, "percentage": 0.1}, ...]
        rank_to_score = {}
        for entry in scores_table:
            score = entry.get("score")
            cum_rank = entry.get("cumulative")
            if score is not None and cum_rank is not None:
                rank_to_score[int(cum_rank)] = int(score)

        logger.info(f"加载了 {len(rank_to_score)} 条位次-分数映射 (广东2025)")
        return rank_to_score

    except Exception as e:
        logger.warning(f"加载分数位次表失败: {e}，将使用估算公式")
        return {}


def estimate_score_from_rank(rank: int, rank_to_score: Dict[int, int]) -> int:
    """
    根据位次估算分数

    优先使用真实一分一段表，回退到估算公式

    Args:
        rank: 考生位次
        rank_to_score: 位次到分数的映射表

    Returns:
        估算分数
    """
    if not rank_to_score:
        # 回退：硬编码估算公式
        return max(300, min(750, 750 - (rank // 1000) * 10))

    # 查找最接近的位次
    sorted_ranks = sorted(rank_to_score.keys())

    # 精确匹配
    if rank in rank_to_score:
        return rank_to_score[rank]

    # 查找上下边界
    lower_rank = None
    upper_rank = None
    for r in sorted_ranks:
        if r <= rank:
            lower_rank = r
        if r >= rank and upper_rank is None:
            upper_rank = r

    # 边界外处理
    if lower_rank is None:
        return rank_to_score[upper_rank]
    if upper_rank is None:
        return rank_to_score[lower_rank]

    # 线性插值
    lower_score = rank_to_score[lower_rank]
    upper_score = rank_to_score[upper_rank]
    if lower_rank == upper_rank:
        return lower_score

    ratio = (rank - lower_rank) / (upper_rank - lower_rank)
    interpolated = lower_score + (upper_score - lower_score) * ratio
    return max(300, min(750, int(round(interpolated))))


def filter_eligible_records(records: List[Dict]) -> List[Dict]:
    """
    筛选符合条件的测试记录

    Args:
        records: 原始录取数据

    Returns:
        筛选后的记录列表
    """
    logger.info("正在筛选符合条件的测试记录...")

    filtered = []
    for record in records:
        # 筛选条件：广东省 + 2025年
        if (record.get("province") == "广东" and
            record.get("year") == 2025 and
            record.get("min_rank")):  # 必须有位次数据

            # 确保必填字段完整
            if all(record.get(field) for field in [
                "university_name", "major_name", "min_rank"
            ]):
                filtered.append(record)

    logger.info(f"筛选完成，符合条件记录: {len(filtered):,} 条")

    if len(filtered) < 1000:
        logger.warning(f"筛选后的记录数量较少 ({len(filtered)} 条)，可能影响测试代表性")

    return filtered


def stratified_sampling(records: List[Dict], sample_size: int) -> List[TestRecord]:
    """
    分层随机抽样

    Args:
        records: 筛选后的录取数据
        sample_size: 目标样本量

    Returns:
        测试记录列表
    """
    logger.info(f"正在进行分层随机抽样，目标样本量: {sample_size}...")

    # 按位次段分组
    rank_groups = defaultdict(list)
    for record in records:
        rank = record["min_rank"]
        # 确定所属位次段
        for range_info in RANK_RANGES:
            if range_info["min"] <= rank <= range_info["max"]:
                rank_groups[range_info["name"]].append(record)
                break

    # 检查各段数据充足性
    logger.info("位次段数据分布：")
    for range_info in RANK_RANGES:
        group_name = range_info["name"]
        group_size = len(rank_groups[group_name])
        target_size = int(sample_size * range_info["ratio"])
        logger.info(f"  {group_name}: {group_size:,} 条 (目标: {target_size} 条, {range_info['description']})")

    # 从每个位次段抽取样本
    test_records = []

    for range_info in RANK_RANGES:
        group_name = range_info["name"]
        target_size = int(sample_size * range_info["ratio"])
        group_records = rank_groups[group_name]

        # 如果该段数据不足，全部抽取
        if len(group_records) <= target_size:
            selected = group_records
            logger.warning(f"位次段 {group_name} 数据不足，抽取全部 {len(selected)} 条")
        else:
            # 随机抽样
            selected = random.sample(group_records, target_size)

        # 转换为 TestRecord 对象
        for record in selected:
            test_record = TestRecord(
                rank=record["min_rank"],
                university_id=str(record.get("university_id", "")),
                university_name=record["university_name"],
                major_id=str(record.get("major_id", "")),
                major_name=record["major_name"],
                year=record["year"]
            )
            test_records.append(test_record)

    logger.info(f"抽样完成，实际抽取: {len(test_records)} 条测试记录")

    return test_records


# ==================== 推荐接口调用模块 ====================

def call_recommend_api(rank: int, province: str = "广东",
                       subjects: List[str] = None,
                       preference: str = "balanced",
                       rank_to_score: Dict[int, int] = None,
                       target_major: str = "计算机科学与技术") -> Tuple[bool, Dict, float]:
    """
    调用推荐接口

    Args:
        rank: 位次
        province: 省份
        subjects: 科目列表（暂不使用）
        preference: 推荐偏好（暂不使用）
        rank_to_score: 位次到分数的真实映射表
        target_major: 目标专业（从测试记录中提取）

    Returns:
        (是否成功, 响应数据, 响应时间)
    """
    # 使用真实一分一段表估算分数
    if rank_to_score:
        estimated_score = estimate_score_from_rank(rank, rank_to_score)
    else:
        estimated_score = max(300, min(750, 750 - (rank // 1000) * 10))

    # 省份名称映射（英文转中文）
    province_mapping = {
        "Guangdong": "广东",
        "Hunan": "湖南",
        "Jiangxi": "江西",
        "Guangxi": "广西",
        "Fujian": "福建",
        "Sichuan": "四川",
        "Anhui": "安徽",
        "Jiangsu": "江苏",
        "Zhejiang": "浙江",
        "Henan": "河南",
        "Hubei": "湖北",
        "Beijing": "北京",
        "Shanghai": "上海"
    }

    chinese_province = province_mapping.get(province, province)

    request_data = {
        "province": chinese_province,  # 使用中文省份名
        "score": estimated_score,     # 使用分数而不是位次
        "rank": rank,                 # 同时提供位次
        "subject_type": "理科",       # 固定为理科
        "target_majors": [target_major]  # 使用测试记录中的实际专业
    }

    start_time = time.time()

    try:
        response = requests.post(
            RECOMMEND_ENDPOINT,
            json=request_data,
            timeout=API_TIMEOUT
        )

        response_time = (time.time() - start_time) * 1000  # 转换为毫秒

        if response.status_code == 200:
            result = response.json()
            if result.get("success") or result.get("code") == 0:
                # 处理两种可能的响应格式
                if result.get("success"):
                    return True, result.get("data", result), response_time
                else:
                    return True, result.get("data", {}), response_time
            else:
                return False, {"error": result.get("message", "未知错误")}, response_time
        else:
            return False, {"error": f"HTTP {response.status_code}"}, response_time

    except requests.exceptions.Timeout:
        response_time = (time.time() - start_time) * 1000
        return False, {"error": "请求超时"}, response_time
    except requests.exceptions.ConnectionError:
        response_time = (time.time() - start_time) * 1000
        return False, {"error": "连接失败"}, response_time
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return False, {"error": str(e)}, response_time


def run_single_test(test_record: TestRecord,
                    rank_to_score: Dict[int, int] = None) -> TestResult:
    """
    运行单个测试用例

    Args:
        test_record: 测试记录
        rank_to_score: 位次到分数的映射表

    Returns:
        测试结果
    """
    test_result = TestResult(test_record)

    # 调用推荐接口（使用真实分数映射和实际专业）
    success, response_data, response_time = call_recommend_api(
        rank=test_record.rank,
        province="广东",
        subjects=DEFAULT_SUBJECTS,
        preference=DEFAULT_PREFERENCE,
        rank_to_score=rank_to_score,
        target_major=test_record.major_name
    )

    test_result.response_time = response_time

    if not success:
        test_result.error = response_data.get("error", "未知错误")
        return test_result

    # 解析推荐结果 - 支持多种API返回格式
    recommendations = []

    if response_data.get("code") == 0:
        # 新格式: {"code": 0, "data": {"recommendations": [...], "summary": {...}}}
        data = response_data.get("data", {})
        recommendations = data.get("recommendations", [])
        print(f"[DEBUG] 使用新API格式，推荐数量: {len(recommendations)}")

    elif response_data.get("success") and isinstance(response_data.get("data"), dict):
        # 旧格式: {"success": true, "data": {"冲刺": [...], "稳妥": [...], "保底": [...]}}
        service_data = response_data.get("data", {})
        for category in ["冲刺", "稳妥", "保底"]:
            category_recs = service_data.get(category, [])
            if isinstance(category_recs, list):
                recommendations.extend(category_recs)
        print(f"[DEBUG] 使用旧API格式，推荐数量: {len(recommendations)}")

    else:
        # 备用格式
        recommendations = response_data.get("recommendations", [])
        print(f"[DEBUG] 使用备用格式，推荐数量: {len(recommendations)}")

    test_result.recommendations = recommendations

    # 判定是否命中
    actual_university = test_record.university_name
    actual_major = test_record.major_name

    for rec in recommendations:
        rec_university = rec.get("university_name", "")
        rec_major = rec.get("major_name", "")

        # 院校命中判定
        if rec_university == actual_university:
            test_result.university_hit = True
            test_result.probability_if_found = rec.get("probability")

            # 精确命中判定
            if rec_major == actual_major:
                test_result.exact_hit = True
                break

    return test_result


# ==================== 测试执行模块 ====================

def run_backtest(test_records: List[TestRecord], show_progress: bool = True,
                 rank_to_score: Dict[int, int] = None) -> List[TestResult]:
    """
    运行回溯测试

    Args:
        test_records: 测试记录列表
        show_progress: 是否显示进度条
        rank_to_score: 位次到分数的映射表

    Returns:
        测试结果列表
    """
    logger.info(f"开始运行回溯测试，共 {len(test_records)} 条测试用例...")

    test_results = []

    # 创建进度条
    iterator = tqdm(test_records, desc="测试进度", unit="条") if show_progress else test_records

    for test_record in iterator:
        test_result = run_single_test(test_record, rank_to_score)
        test_results.append(test_result)

        # 更新进度条描述
        if show_progress:
            hit_count = sum(1 for r in test_results if r.university_hit)
            hit_rate = hit_count / len(test_results) * 100
            iterator.set_postfix({"命中率": f"{hit_rate:.1f}%"})

    logger.info(f"测试完成，共 {len(test_results)} 条结果")

    return test_results


# ==================== 统计分析模块 ====================

def calculate_statistics(test_records: List[TestRecord],
                        test_results: List[TestResult]) -> Dict:
    """
    计算测试统计数据

    Args:
        test_records: 测试记录列表
        test_results: 测试结果列表

    Returns:
        统计数据字典
    """
    logger.info("正在计算统计数据...")

    stats = {
        "test_config": {
            "total_tests": len(test_records),
            "api_endpoint": RECOMMEND_ENDPOINT,
            "default_subjects": DEFAULT_SUBJECTS,
            "default_preference": DEFAULT_PREFERENCE,
            "test_time": datetime.now().isoformat()
        },
        "overall_metrics": {},
        "rank_range_metrics": [],
        "probability_metrics": [],
        "performance_metrics": {}
    }

    # 1. 整体指标
    university_hits = sum(1 for r in test_results if r.university_hit)
    exact_hits = sum(1 for r in test_results if r.exact_hit)

    stats["overall_metrics"] = {
        "total_tests": len(test_records),
        "university_hits": university_hits,
        "university_hit_rate": university_hits / len(test_results) * 100,
        "exact_hits": exact_hits,
        "exact_hit_rate": exact_hits / len(test_results) * 100
    }

    logger.info(f"整体命中率: {university_hits}/{len(test_results)} = {stats['overall_metrics']['university_hit_rate']:.2f}%")

    # 2. 分位次段统计
    for range_info in RANK_RANGES:
        range_name = range_info["name"]

        # 筛选该位次段的测试结果
        range_results = [
            r for r in test_results
            if range_info["min"] <= r.test_record.rank <= range_info["max"]
        ]

        if not range_results:
            continue

        range_hits = sum(1 for r in range_results if r.university_hit)
        range_exact_hits = sum(1 for r in range_results if r.exact_hit)

        range_stat = {
            "rank_range": range_name,
            "description": range_info["description"],
            "test_count": len(range_results),
            "university_hits": range_hits,
            "university_hit_rate": range_hits / len(range_results) * 100,
            "exact_hits": range_exact_hits,
            "exact_hit_rate": range_exact_hits / len(range_results) * 100
        }

        stats["rank_range_metrics"].append(range_stat)

        logger.info(f"位次段 {range_name}: 命中率 {range_stat['university_hit_rate']:.2f}%")

    # 3. 概率准确度统计
    for prob_range in PROBABILITY_RANGES:
        range_name = prob_range["name"]
        min_prob = prob_range["min"]
        max_prob = prob_range["max"]

        # 筛选该概率区间的测试结果
        range_results = [
            r for r in test_results
            if r.probability_if_found is not None
            and min_prob <= r.probability_if_found < max_prob
        ]

        if not range_results:
            continue

        range_hits = sum(1 for r in range_results if r.university_hit)

        range_stat = {
            "probability_range": range_name,
            "test_count": len(range_results),
            "actual_hits": range_hits,
            "actual_hit_rate": range_hits / len(range_results) * 100 if range_results else 0,
            "expected_range": f"{min_prob}-{max_prob}%"
        }

        stats["probability_metrics"].append(range_stat)

        logger.info(f"概率区间 {range_name}: 实际命中率 {range_stat['actual_hit_rate']:.2f}%")

    # 4. 性能指标
    response_times = [r.response_time for r in test_results if r.response_time > 0]

    if response_times:
        stats["performance_metrics"] = {
            "total_requests": len(test_results),
            "total_time": sum(response_times) / 1000,  # 转换为秒
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": sorted(response_times)[len(response_times) // 2]
        }

        logger.info(f"平均响应时间: {stats['performance_metrics']['avg_response_time']:.2f}ms")

    # 5. 错误统计
    error_results = [r for r in test_results if r.error]
    if error_results:
        stats["error_metrics"] = {
            "error_count": len(error_results),
            "error_rate": len(error_results) / len(test_results) * 100,
            "common_errors": _get_common_errors(error_results)
        }

    return stats


def _get_common_errors(error_results: List[TestResult]) -> List[Dict]:
    """获取常见错误"""
    error_counts = defaultdict(int)
    for result in error_results:
        error_counts[result.error] += 1

    # 返回最常见的5个错误
    common_errors = [
        {"error": error, "count": count}
        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return common_errors


def extract_unhit_details(test_results: List[TestResult], limit: int = 50) -> List[Dict]:
    """
    提取未命中案例详情

    Args:
        test_results: 测试结果列表
        limit: 提取数量限制

    Returns:
        未命中案例详情列表
    """
    logger.info(f"正在提取未命中案例详情（前{limit}条）...")

    unhit_results = [r for r in test_results if not r.university_hit]

    # 按位次排序，优先显示高位次案例
    unhit_results.sort(key=lambda x: x.test_record.rank)

    unhit_details = []
    for result in unhit_results[:limit]:
        detail = {
            "rank": result.test_record.rank,
            "actual_university": result.test_record.university_name,
            "actual_major": result.test_record.major_name,
            "top10_recommendations": [
                f"{r.get('university_name', '')} - {r.get('major_name', '')}"
                for r in result.recommendations[:10]
            ],
            "probability_if_found": result.probability_if_found,
            "error": result.error
        }
        unhit_details.append(detail)

    logger.info(f"未命中案例: {len(unhit_details)}/{len(unhit_results)}")

    return unhit_details


# ==================== 输出生成模块 ====================

def ensure_output_dir() -> Path:
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR


def save_json_report(data: Dict, filename: str) -> Path:
    """
    保存JSON报告

    Args:
        data: 要保存的数据
        filename: 文件名

    Returns:
        保存的文件路径
    """
    output_dir = ensure_output_dir()
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"JSON报告已保存: {filepath}")

    return filepath


def save_csv_report(stats: Dict, filename: str) -> Path:
    """
    保存CSV报告

    Args:
        stats: 统计数据
        filename: 文件名

    Returns:
        保存的文件路径
    """
    output_dir = ensure_output_dir()
    filepath = output_dir / filename

    # 生成位次段命中率CSV
    import csv

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 表头
        writer.writerow([
            "位次段", "描述", "测试数", "院校命中数", "院校命中率(%)",
            "精确命中数", "精确命中率(%)"
        ])

        # 数据行
        for range_stat in stats.get("rank_range_metrics", []):
            writer.writerow([
                range_stat["rank_range"],
                range_stat["description"],
                range_stat["test_count"],
                range_stat["university_hits"],
                f"{range_stat["university_hit_rate"]:.2f}",
                range_stat["exact_hits"],
                f"{range_stat["exact_hit_rate"]:.2f}"
            ])

    logger.info(f"CSV报告已保存: {filepath}")

    return filepath


def generate_html_report(stats: Dict, unhit_details: List[Dict]) -> Path:
    """
    生成HTML测试报告

    Args:
        stats: 统计数据
        unhit_details: 未命中案例详情

    Returns:
        保存的文件路径
    """
    output_dir = ensure_output_dir()
    filepath = output_dir / f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    html_content = _generate_html_content(stats, unhit_details)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML报告已保存: {filepath}")

    return filepath


def _generate_html_content(stats: Dict, unhit_details: List[Dict]) -> str:
    """生成HTML报告内容"""

    overall = stats.get("overall_metrics", {})
    performance = stats.get("performance_metrics", {})
    rank_metrics = stats.get("rank_range_metrics", [])
    prob_metrics = stats.get("probability_metrics", [])

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>推荐系统回溯测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; }}
        h1 {{ color: #1976D2; border-bottom: 3px solid #1976D2; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; }}
        .metric-label {{ font-size: 14px; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #1976D2; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .hit-rate {{ font-weight: bold; color: #4CAF50; }}
        .grade-excellent {{ color: #4CAF50; font-weight: bold; }}
        .grade-good {{ color: #2196F3; font-weight: bold; }}
        .grade-pass {{ color: #FF9800; font-weight: bold; }}
        .grade-fail {{ color: #F44336; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 推荐系统回溯测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>📊 整体表现</h2>
        <div class="summary">
            <div class="metric-card">
                <div class="metric-value">{overall.get("university_hit_rate", 0):.1f}%</div>
                <div class="metric-label">院校命中率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overall.get("exact_hit_rate", 0):.1f}%</div>
                <div class="metric-label">精确命中率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overall.get("total_tests", 0)}</div>
                <div class="metric-label">测试样本数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{performance.get("avg_response_time", 0):.0f}ms</div>
                <div class="metric-label">平均响应时间</div>
            </div>
        </div>

        <h2>📈 分位次段表现</h2>
        <table>
            <tr>
                <th>位次段</th>
                <th>描述</th>
                <th>测试数</th>
                <th>院校命中数</th>
                <th>院校命中率</th>
                <th>精确命中数</th>
                <th>精确命中率</th>
                <th>评级</th>
            </tr>
    """

    for range_stat in rank_metrics:
        hit_rate = range_stat["university_hit_rate"]
        grade = _get_grade(hit_rate)

        html += f"""
            <tr>
                <td>{range_stat["rank_range"]}</td>
                <td>{range_stat["description"]}</td>
                <td>{range_stat["test_count"]}</td>
                <td>{range_stat["university_hits"]}</td>
                <td class="hit-rate">{hit_rate:.2f}%</td>
                <td>{range_stat["exact_hits"]}</td>
                <td>{range_stat["exact_hit_rate"]:.2f}%</td>
                <td class="grade-{grade}">{grade.upper()}</td>
            </tr>
        """

    html += """
        </table>

        <h2>🎲 概率准确度分析</h2>
        <table>
            <tr>
                <th>预测概率区间</th>
                <th>测试数</th>
                <th>实际命中数</th>
                <th>实际命中率</th>
                <th>评估</th>
            </tr>
    """

    for prob_stat in prob_metrics:
        actual_rate = prob_stat["actual_hit_rate"]
        expected_range = prob_stat["expected_range"]
        evaluation = _evaluate_probability_accuracy(actual_rate, expected_range)

        html += f"""
            <tr>
                <td>{prob_stat["probability_range"]}</td>
                <td>{prob_stat["test_count"]}</td>
                <td>{prob_stat["actual_hits"]}</td>
                <td class="hit-rate">{actual_rate:.2f}%</td>
                <td>{evaluation}</td>
            </tr>
        """

    html += """
        </table>

        <h2>⚡ 性能指标</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>数值</th>
            </tr>
            <tr>
                <td>总请求数</td>
                <td>""" + str(performance.get("total_requests", 0)) + """</td>
            </tr>
            <tr>
                <td>总耗时</td>
                <td>""" + f"{performance.get('total_time', 0):.2f}" + """秒</td>
            </tr>
            <tr>
                <td>平均响应时间</td>
                <td>""" + f"{performance.get('avg_response_time', 0):.2f}" + """毫秒</td>
            </tr>
            <tr>
                <td>最快响应时间</td>
                <td>""" + f"{performance.get('min_response_time', 0):.2f}" + """毫秒</td>
            </tr>
            <tr>
                <td>最慢响应时间</td>
                <td>""" + f"{performance.get('max_response_time', 0):.2f}" + """毫秒</td>
            </tr>
        </table>

        <h2>❌ 未命中案例（前10条）</h2>
        <table>
            <tr>
                <th>位次</th>
                <th>实际录取院校</th>
                <th>实际录取专业</th>
                <th>推荐前3</th>
            </tr>
    """

    for case in unhit_details[:10]:
        top3 = ", ".join(case.get("top10_recommendations", [])[:3])
        html += f"""
            <tr>
                <td>{case["rank"]:,}</td>
                <td>{case["actual_university"]}</td>
                <td>{case["actual_major"]}</td>
                <td>{top3}</td>
            </tr>
        """

    html += """
        </table>

        <p style="text-align: center; color: #999; margin-top: 40px;">
            学锋志愿教练 - 推荐系统回溯测试报告<br>
            """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
        </p>
    </div>
</body>
</html>
    """

    return html


def _get_grade(hit_rate: float) -> str:
    """根据命中率评级"""
    if hit_rate >= 85:
        return "excellent"
    elif hit_rate >= 75:
        return "good"
    elif hit_rate >= 65:
        return "pass"
    else:
        return "fail"


def _evaluate_probability_accuracy(actual_rate: float, expected_range: str) -> str:
    """评估概率预测准确性"""
    try:
        # 解析预期范围
        parts = expected_range.replace("%", "").split("-")
        min_expected = float(parts[0])
        max_expected = float(parts[1]) if len(parts) > 1 else min_expected

        # 检查是否在范围内
        if min_expected <= actual_rate <= max_expected:
            return "✅ 准确"
        elif abs(actual_rate - min_expected) <= 10 or abs(actual_rate - max_expected) <= 10:
            return "⚠️ 偏差较小"
        else:
            return "❌ 偏差较大"
    except:
        return "❓ 无法评估"


# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="推荐系统回溯测试")
    parser.add_argument("--quick", action="store_true", help="快速测试模式（50条样本）")
    parser.add_argument("--sample", type=int, help="自定义样本量")
    parser.add_argument("--rerun", action="store_true", help="重新运行测试")
    args = parser.parse_args()

    # 确定样本量
    if args.quick:
        sample_size = QUICK_TEST_SAMPLE_SIZE
        logger.info("🚀 快速测试模式")
    elif args.sample:
        sample_size = args.sample
        logger.info(f"🎯 自定义样本量: {sample_size}")
    else:
        sample_size = DEFAULT_SAMPLE_SIZE
        logger.info(f"📊 完整测试模式")

    # 检查API连接
    logger.info(f"检查API连接: {API_BASE_URL}")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        logger.info("✅ API连接正常")
    except:
        logger.error("❌ 无法连接到API，请确保后端服务已启动")
        return

    start_time = time.time()

    try:
        # 1. 加载录取数据
        records = load_admission_data()

        # 1.5. 加载一分一段表（用于真实分数映射）
        rank_to_score = load_score_rank_table()

        # 2. 筛选数据
        eligible_records = filter_eligible_records(records)

        if len(eligible_records) < sample_size:
            logger.warning(f"可用数据不足，调整样本量: {sample_size} -> {len(eligible_records)}")
            sample_size = len(eligible_records)

        # 3. 分层抽样
        test_records = stratified_sampling(eligible_records, sample_size)

        # 4. 运行测试（使用真实分数映射）
        test_results = run_backtest(test_records, show_progress=True,
                                    rank_to_score=rank_to_score)

        # 5. 统计分析
        stats = calculate_statistics(test_records, test_results)

        # 6. 提取未命中案例
        unhit_details = extract_unhit_details(test_results, limit=50)

        # 7. 生成报告
        logger.info("正在生成测试报告...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON报告
        json_report = {
            "statistics": stats,
            "unhit_details": unhit_details,
            "test_summary": {
                "total_tests": len(test_records),
                "university_hit_rate": stats["overall_metrics"]["university_hit_rate"],
                "exact_hit_rate": stats["overall_metrics"]["exact_hit_rate"],
                "test_duration": time.time() - start_time
            }
        }
        save_json_report(json_report, f"backtest_report_{timestamp}.json")
        save_json_report(unhit_details, f"backtest_unhit_details_{timestamp}.json")

        # CSV报告
        save_csv_report(stats, f"backtest_hit_rate_by_rank_{timestamp}.csv")

        # HTML报告
        generate_html_report(stats, unhit_details)

        # 输出最终结果
        total_time = time.time() - start_time
        logger.info("=" * 50)
        logger.info("🎉 测试完成！")
        logger.info(f"整体院校命中率: {stats['overall_metrics']['university_hit_rate']:.2f}%")
        logger.info(f"整体精确命中率: {stats['overall_metrics']['exact_hit_rate']:.2f}%")
        logger.info(f"平均响应时间: {stats['performance_metrics']['avg_response_time']:.2f}ms")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info("=" * 50)

        # 评级结果
        overall_hit_rate = stats['overall_metrics']['university_hit_rate']
        grade = _get_grade(overall_hit_rate)

        if grade == "excellent":
            logger.info("🏆 评级: 优秀 (≥85%)")
        elif grade == "good":
            logger.info("👍 评级: 良好 (75-85%)")
        elif grade == "pass":
            logger.info("✅ 评级: 及格 (65-75%)")
        else:
            logger.warning("⚠️ 评级: 不及格 (<65%)")

    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()