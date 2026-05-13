"""
2026年出分后紧急采集脚本
在高考出分后（6月23-25日）密集监控各省考试院，第一时间获取投档线数据

关键时间节点：
- 6月23-25日：各省一分一段表
- 7月上中旬：提前批投档线
- 7月中下旬：本科批投档线
- 8月上旬：专科批投档线

优先级：P0（最高优先级）
"""

import json
import requests
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
import hashlib


class EmergencyCollector2026:
    """2026年出分后紧急采集器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.emergency_dir = self.base_dir / "reports" / "emergency_collection"

        # 确保目录存在
        self.emergency_dir.mkdir(parents=True, exist_ok=True)

        # 紧急采集配置
        self.emergency_config = {
            "active": False,  # 激活状态
            "start_date": "2026-06-23",  # 预计开始日期
            "end_date": "2026-08-15",    # 预计结束日期
            "high_frequency_mode": False,  # 高频模式（出分后激活）
            "notification_enabled": True,
            "auto_import_enabled": True
        }

        # 各省考试院紧急采集配置
        self.emergency_sources = {
            "广东": {
                "urls": ["https://eea.gd.gov.cn/"],
                "check_interval_minutes": 15,  # 出分后每15分钟检查一次
                "file_patterns": ["投档线", "排位", "一分一段", "分数段"],
                "contact": "广东省教育考试院",
                "priority": "P0",
                "status": "standby"  # standby, active, completed
            },
            "湖南": {
                "urls": ["https://www.hneeb.cn/"],
                "check_interval_minutes": 30,
                "file_patterns": ["投档线", "分数线"],
                "contact": "湖南省教育考试院",
                "priority": "P0",
                "status": "standby"
            },
            "江西": {
                "urls": ["https://www.jxeea.cn/"],
                "check_interval_minutes": 30,
                "file_patterns": ["投档线", "一分一段"],
                "contact": "江西省教育考试院",
                "priority": "P0",
                "status": "standby"
            },
            "广西": {
                "urls": ["https://www.gxeea.cn/"],
                "check_interval_minutes": 30,
                "file_patterns": ["投档线", "分数段"],
                "contact": "广西壮族自治区教育考试院",
                "priority": "P0",
                "status": "standby"
            },
            "湖北": {
                "urls": ["https://www.hbea.edu.cn/"],
                "check_interval_minutes": 30,
                "file_patterns": ["投档线", "一分一段"],
                "contact": "湖北省教育考试院",
                "priority": "P0",
                "status": "standby"
            },
            # 可以继续添加其他省份...
        }

        # 数据类型优先级
        self.data_type_priority = {
            "一分一段表": {"priority": "P0", "expected_date": "2026-06-23"},
            "提前批投档线": {"priority": "P0", "expected_date": "2026-07-10"},
            "本科批投档线": {"priority": "P0", "expected_date": "2026-07-20"},
            "专科批投档线": {"priority": "P1", "expected_date": "2026-08-05"}
        }

    def activate_emergency_mode(self):
        """激活紧急采集模式"""
        print("\n" + "="*80)
        print("激活2026年出分后紧急采集模式")
        print("="*80)

        self.emergency_config["active"] = True
        self.emergency_config["high_frequency_mode"] = True
        self.emergency_config["activated_at"] = datetime.now().isoformat()

        print(f"激活时间: {self.emergency_config['activated_at']}")
        print("监控频率: 每15-30分钟检查一次各省考试院")
        print("数据类型: 一分一段表、投档线")
        print("自动导入: 启用")
        print("通知功能: 启用")

        # 保存激活状态
        self._save_emergency_config()

        print("\n[SUCCESS] 紧急采集模式已激活")

    def run_emergency_cycle(self):
        """执行一次紧急采集周期"""
        if not self.emergency_config["active"]:
            print("[INFO] 紧急采集模式未激活，跳过")
            return

        print("\n" + "="*80)
        print("紧急采集周期执行")
        print("="*80)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        cycle_results = {
            "timestamp": datetime.now().isoformat(),
            "cycle_type": "emergency",
            "total_checks": 0,
            "new_data_found": 0,
            "province_results": [],
            "notifications": []
        }

        # 按优先级检查各省
        for province, config in sorted(
            self.emergency_sources.items(),
            key=lambda x: x[1]["priority"]
        ):
            if config["status"] != "active":
                continue

            print(f"\n检查 {province}省...")
            result = self._check_province_emergency(province, config)
            cycle_results["province_results"].append(result)
            cycle_results["total_checks"] += 1

            if result["new_data"]:
                cycle_results["new_data_found"] += len(result["new_data"])
                print(f"  [发现新数据] {len(result['new_data'])} 项")

                # 立即通知
                if self.emergency_config["notification_enabled"]:
                    notification = self._create_emergency_notification(province, result["new_data"])
                    cycle_results["notifications"].append(notification)
                    print(f"  [通知] 已发送紧急通知")
            else：
                print(f"  [无新数据]")

            # 请求间隔
            time.sleep(2)  # 避免请求过快

        # 保存结果
        self._save_emergency_results(cycle_results)

        print(f"\n紧急采集周期完成: 检查 {cycle_results['total_checks']} 个省份，发现 {cycle_results['new_data_found']} 项新数据")

        # 如果发现重要数据，立即导入
        if cycle_results["new_data_found"] > 0 and self.emergency_config["auto_import_enabled"]:
            print("\n[自动导入] 正在导入新数据...")
            self._emergency_import_data(cycle_results)

    def _check_province_emergency(self, province: str, config: Dict) -> Dict:
        """检查单个省份的紧急数据"""
        result = {
            "province": province,
            "timestamp": datetime.now().isoformat(),
            "new_data": [],
            "error": None
        }

        try:
            # 检查各个URL
            for url in config["urls"]:
                print(f"  访问 {url}...")

                # 获取页面内容
                content = self._fetch_page_content(url)

                if not content:
                    continue

                # 检查是否包含目标关键词
                found_patterns = []
                for pattern in config["file_patterns"]:
                    if pattern in content:
                        found_patterns.append(pattern)

                if found_patterns:
                    print(f"    发现关键词: {', '.join(found_patterns)}")

                    # 尝试下载数据
                    downloaded_data = self._download_emergency_data(province, url, found_patterns)
                    if downloaded_data:
                        result["new_data"].extend(downloaded_data)

        except Exception as e:
            result["error"] = str(e)

        return result

    def _fetch_page_content(self, url: str) -> str:
        """获取页面内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            response.encoding = 'utf-8'

            return response.text

        except Exception as e:
            print(f"    [ERROR] 获取页面失败: {str(e)}")
            return ""

    def _download_emergency_data(self, province: str, url: str, patterns: List[str]) -> List[Dict]:
        """下载紧急数据"""
        downloaded = []

        # TODO: 实现具体的数据下载逻辑
        # 这里需要根据各个网站的具体结构来解析和下载数据

        # 示例：假设发现了"一分一段表"
        if "一分一段" in patterns:
            data = {
                "type": "一分一段表",
                "province": province,
                "url": url,
                "downloaded_at": datetime.now().isoformat(),
                "status": "pending_parse"  # 待解析
            }
            downloaded.append(data)

        return downloaded

    def _create_emergency_notification(self, province: str, new_data: List[Dict]) -> Dict:
        """创建紧急通知"""
        notification = {
            "type": "emergency_data",
            "severity": "high",
            "province": province,
            "timestamp": datetime.now().isoformat(),
            "message": f"{province}省发现{len(new_data)}项新数据",
            "data_types": [d["type"] for d in new_data],
            "action_required": "立即验证并导入数据"
        }

        # 保存通知
        notification_file = self.emergency_dir / f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(notification_file, 'w', encoding='utf-8') as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)

        return notification

    def _emergency_import_data(self, cycle_results: Dict):
        """紧急数据导入"""
        # TODO: 实现具体的数据导入逻辑
        print("  数据导入功能待实现")

    def _save_emergency_results(self, results: Dict):
        """保存紧急采集结果"""
        results_file = self.emergency_dir / f"emergency_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def _save_emergency_config(self):
        """保存紧急采集配置"""
        config_file = self.emergency_dir / "emergency_config.json"

        config_data = {
            "config": self.emergency_config,
            "sources": self.emergency_sources,
            "data_types": self.data_type_priority
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

    def get_emergency_status(self) -> Dict:
        """获取紧急采集状态"""
        status = {
            "active": self.emergency_config["active"],
            "high_frequency_mode": self.emergency_config["high_frequency_mode"],
            "activated_at": self.emergency_config.get("activated_at"),
            "monitored_provinces": len(self.emergency_sources),
            "active_provinces": sum(1 for s in self.emergency_sources.values() if s["status"] == "active"),
            "completed_provinces": sum(1 for s in self.emergency_sources.values() if s["status"] == "completed"),
            "recent_collections": self._get_recent_collections()
        }

        return status

    def _get_recent_collections(self) -> List[Dict]:
        """获取最近的采集记录"""
        # 读取最近的紧急采集结果
        results_files = sorted(self.emergency_dir.glob("emergency_results_*.json"))
        recent = []

        for result_file in results_files[-5:]:  # 最近5次
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
                recent.append({
                    "timestamp": result_data.get("timestamp"),
                    "new_data_count": result_data.get("new_data_found", 0),
                    "provinces_checked": result_data.get("total_checks", 0)
                })

        return recent

    def start_background_monitoring(self):
        """启动后台监控线程"""
        if not self.emergency_config["active"]:
            print("[INFO] 紧急采集模式未激活，无法启动后台监控")
            return

        print("[INFO] 启动后台监控线程...")

        def monitoring_loop():
            while self.emergency_config["active"]:
                try:
                    self.run_emergency_cycle()

                    # 等待下一次检查（根据最小间隔）
                    min_interval = min(
                        s.get("check_interval_minutes", 30)
                        for s in self.emergency_sources.values()
                    )

                    print(f"[INFO] 下一次检查将在 {min_interval} 分钟后")
                    time.sleep(min_interval * 60)

                except Exception as e:
                    print(f"[ERROR] 后台监控出错: {str(e)}")
                    time.sleep(300)  # 出错后等待5分钟再继续

        # 启动监控线程
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()

        print("[SUCCESS] 后台监控线程已启动")


def main():
    """主函数"""
    collector = EmergencyCollector2026()

    # 检查是否需要激活紧急模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "activate":
        collector.activate_emergency_mode()
        return 0

    # 执行一次采集周期
    try:
        collector.run_emergency_cycle()
        return 0
    except Exception as e:
        print(f"\n[ERROR] 采集过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())