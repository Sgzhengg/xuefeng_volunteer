"""
2025年高考录取数据批量导入脚本
支持读取各省教育考试院发布的CSV文件，自动转换格式并导入系统
"""
import os
import csv
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import chardet
from io import StringIO

# ==================== 配置 ====================

# Admin API配置
ADMIN_API_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# 数据目录
DATA_DIR = Path("data")
PROVINCE_DATA_DIR = Path("province_data_2025")
LOG_DIR = Path("logs")

# 支持的省份及其数据格式配置
PROVINCE_CONFIGS = {
    "广东": {
        "encoding": "gbk",
        "delimiter": ",",
        "column_mapping": {
            "院校名称": "university_name",
            "专业名称": "major_name",
            "年份": "year",
            "省份": "province",
            "最低位次": "min_rank",
            "最低分": "min_score"
        }
    },
    "河南": {
        "encoding": "gbk",
        "delimiter": ",",
        "column_mapping": {
            "院校名称": "university_name",
            "专业名称": "major_name",
            "年份": "year",
            "省份": "province",
            "最低位次": "min_rank",
            "最低分": "min_score"
        }
    },
    "山东": {
        "encoding": "gb2312",
        "delimiter": "\t",
        "column_mapping": {
            "学校名称": "university_name",
            "专业名称": "major_name",
            "年份": "year",
            "省份": "province",
            "最低排位": "min_rank",
            "最低分": "min_score"
        }
    },
    "四川": {
        "encoding": "gbk",
        "delimiter": ",",
        "column_mapping": {
            "院校名称": "university_name",
            "专业名称": "major_name",
            "年份": "year",
            "省份": "province",
            "最低位次": "min_rank",
            "最低分": "min_score"
        }
    }
}

# ==================== 日志配置 ====================

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 工具函数 ====================

class APIClient:
    """Admin API客户端"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.token = None
        self.username = username
        self.password = password

    def login(self) -> bool:
        """登录获取token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/admin/login",
                json={"username": self.username, "password": self.password},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.token = data["data"]["token"]
                    logger.info("管理员登录成功")
                    return True

            logger.error(f"登录失败: {response.text}")
            return False

        except Exception as e:
            logger.error(f"登录异常: {e}")
            return False

    def import_csv_file(self, csv_file_path: Path) -> Dict:
        """导入CSV文件"""
        if not self.token:
            if not self.login():
                return {"success": False, "error": "登录失败"}

        try:
            # 读取CSV文件
            with open(csv_file_path, 'rb') as f:
                files = {'file': (csv_file_path.name, f, 'text/csv')}
                headers = {'Authorization': f'Bearer {self.token}'}

                response = requests.post(
                    f"{self.base_url}/api/v1/admin/import/admission",
                    files=files,
                    headers=headers,
                    timeout=300  # 5分钟超时
                )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}


class CSVConverter:
    """CSV格式转换器"""

    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """检测文件编码"""
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'

    @staticmethod
    def standardize_csv(
        input_file: Path,
        output_file: Path,
        province_config: Dict
    ) -> bool:
        """标准化CSV格式"""
        try:
            # 检测编码
            encoding = province_config.get("encoding")
            if not encoding:
                encoding = CSVConverter.detect_encoding(input_file)

            # 读取原始CSV
            with open(input_file, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=province_config.get("delimiter", ","))
                rows = list(reader)

            if not rows:
                logger.warning(f"文件为空: {input_file}")
                return False

            # 获取列名映射
            column_mapping = province_config.get("column_mapping", {})

            # 转换数据
            standardized_rows = []
            for row in rows:
                new_row = {}
                for csv_col, standard_col in column_mapping.items():
                    if csv_col in row:
                        new_row[standard_col] = row[csv_col]

                # 验证必填字段
                required_fields = ['university_name', 'major_name', 'year', 'province', 'min_rank']
                if all(field in new_row and new_row[field].strip() for field in required_fields):
                    standardized_rows.append(new_row)

            if not standardized_rows:
                logger.warning(f"没有有效数据行: {input_file}")
                return False

            # 写入标准化CSV
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                if standardized_rows:
                    writer = csv.DictWriter(f, fieldnames=standardized_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(standardized_rows)

            logger.info(f"转换完成: {input_file} -> {output_file} ({len(standardized_rows)}行)")
            return True

        except Exception as e:
            logger.error(f"转换失败 {input_file}: {e}")
            return False


class DataImporter:
    """数据导入管理器"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.stats = {
            "total_files": 0,
            "success_files": 0,
            "failed_files": 0,
            "total_records": 0,
            "imported_records": 0,
            "duplicate_records": 0,
            "failed_records": 0
        }

    def import_province_data(self, province_name: str) -> bool:
        """导入省份的数据"""
        logger.info(f"开始导入 {province_name} 省份数据")

        province_dir = PROVINCE_DATA_DIR / province_name
        if not province_dir.exists():
            logger.error(f"省份数据目录不存在: {province_dir}")
            return False

        # 获取省份配置
        province_config = PROVINCE_CONFIGS.get(province_name)
        if not province_config:
            logger.warning(f"省份 {province_name} 无配置，使用默认配置")
            province_config = {}

        # 查找所有CSV文件
        csv_files = list(province_dir.glob("*.csv"))
        if not csv_files:
            logger.warning(f"省份数据目录无CSV文件: {province_dir}")
            return False

        logger.info(f"找到 {len(csv_files)} 个CSV文件")

        # 创建临时目录存放标准化文件
        temp_dir = PROVINCE_DATA_DIR / "temp"
        temp_dir.mkdir(exist_ok=True)

        # 处理每个文件
        for csv_file in csv_files:
            self.stats["total_files"] += 1

            logger.info(f"处理文件: {csv_file.name}")

            # 标准化CSV格式
            temp_file = temp_dir / f"standardized_{csv_file.name}"

            if province_config:
                success = CSVConverter.standardize_csv(csv_file, temp_file, province_config)
            else:
                # 无配置，直接使用原文件
                temp_file = csv_file
                success = True

            if not success:
                self.stats["failed_files"] += 1
                continue

            # 调用API导入
            result = self.api_client.import_csv_file(temp_file)

            if result.get("code") == 0:
                self.stats["success_files"] += 1
                data = result.get("data", {})
                self.stats["imported_records"] += data.get("imported_count", 0)
                self.stats["duplicate_records"] += data.get("duplicate_count", 0)
                self.stats["failed_records"] += data.get("failed_count", 0)

                logger.info(f"✓ 导入成功: {csv_file.name}")
                logger.info(f"  成功: {data.get('imported_count')}, "
                          f"重复: {data.get('duplicate_count')}, "
                          f"失败: {data.get('failed_count')}")
            else:
                self.stats["failed_files"] += 1
                logger.error(f"✗ 导入失败: {csv_file.name}")
                logger.error(f"  错误: {result.get('message')}")

            # 删除临时文件
            if temp_file.exists() and temp_file != csv_file:
                temp_file.unlink()

        return True

    def import_all_provinces(self):
        """导入所有省份数据"""
        logger.info("=" * 60)
        logger.info("开始批量导入2025年高考录取数据")
        logger.info("=" * 60)

        start_time = datetime.now()

        # 获取所有省份目录
        if not PROVINCE_DATA_DIR.exists():
            logger.error(f"数据目录不存在: {PROVINCE_DATA_DIR}")
            return

        province_dirs = [d for d in PROVINCE_DATA_DIR.iterdir() if d.is_dir()]

        if not province_dirs:
            logger.error(f"数据目录为空: {PROVINCE_DATA_DIR}")
            return

        logger.info(f"找到 {len(province_dirs)} 个省份数据目录")

        # 逐个导入
        for province_dir in province_dirs:
            province_name = province_dir.name
            self.import_province_data(province_name)

        # 统计结果
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("导入完成！统计信息：")
        logger.info(f"总文件数: {self.stats['total_files']}")
        logger.info(f"成功: {self.stats['success_files']}, 失败: {self.stats['failed_files']}")
        logger.info(f"总记录数: {self.stats['imported_records'] + self.stats['duplicate_records'] + self.stats['failed_records']}")
        logger.info(f"成功导入: {self.stats['imported_records']}")
        logger.info(f"重复记录: {self.stats['duplicate_records']}")
        logger.info(f"失败记录: {self.stats['failed_records']}")
        logger.info(f"耗时: {duration:.2f}秒")
        logger.info("=" * 60)

        # 保存统计结果
        self._save_stats(start_time, end_time)

    def _save_stats(self, start_time: datetime, end_time: datetime):
        """保存统计结果"""
        stats_file = LOG_DIR / f"stats_{start_time.strftime('%Y%m%d_%H%M%S')}.json"

        stats_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
            "stats": self.stats
        }

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)

        logger.info(f"统计结果已保存: {stats_file}")


# ==================== 主程序 ====================

def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║         2025年高考录取数据批量导入工具                      ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 检查目录
    if not PROVINCE_DATA_DIR.exists():
        print(f"❌ 数据目录不存在: {PROVINCE_DATA_DIR}")
        print(f"请创建数据目录并放入省份CSV文件:")
        print(f"  {PROVINCE_DATA_DIR}/广东/*.csv")
        print(f"  {PROVINCE_DATA_DIR}/河南/*.csv")
        print(f"  {PROVINCE_DATA_DIR}/山东/*.csv")
        return

    # 创建API客户端
    api_client = APIClient(ADMIN_API_URL, ADMIN_USERNAME, ADMIN_PASSWORD)

    # 测试连接
    print(f"🔄 连接到Admin API: {ADMIN_API_URL}")
    if not api_client.login():
        print("❌ 无法连接到Admin API，请检查：")
        print("   1. 后端服务是否启动")
        print("   2. API地址是否正确")
        print("   3. 管理员账号密码是否正确")
        return

    # 创建导入器
    importer = DataImporter(api_client)

    # 开始导入
    print(f"📂 数据目录: {PROVINCE_DATA_DIR}")
    print(f"📝 日志目录: {LOG_DIR}")
    print("")

    importer.import_all_provinces()


if __name__ == "__main__":
    main()