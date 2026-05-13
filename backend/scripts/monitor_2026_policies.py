"""
2026年高考政策监控脚本
持续监控各省教育考试院、教育部官网、阳光高考网的政策更新

监控内容：
- 考试时间、科目安排
- 加分政策变化
- 录取批次调整
- 新高考改革动态
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib


class PolicyMonitor2026:
    """2026年政策监控器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.reports_dir = self.base_dir / "reports"
        self.policy_data_dir = self.reports_dir / "policy_data"

        # 确保目录存在
        self.policy_data_dir.mkdir(parents=True, exist_ok=True)

        # 监控配置
        self.monitoring_config = {
            "check_interval_hours": 12,  # 每12小时检查一次
            "notification_threshold": "medium",  # 重要及以上变化才通知
            "monitored_sources": [
                {
                    "name": "广东省教育考试院",
                    "url": "https://eea.gd.gov.cn/",
                    "type": "provincial",
                    "priority": "high",
                    "focus_areas": ["录取批次", "加分政策", "志愿填报时间"]
                },
                {
                    "name": "教育部官网",
                    "url": "https://www.moe.gov.cn/",
                    "type": "national",
                    "priority": "high",
                    "focus_areas": ["高考改革", "加分政策", "考试安排"]
                },
                {
                    "name": "阳光高考网",
                    "url": "https://gaokao.chsi.com.cn/",
                    "type": "platform",
                    "priority": "medium",
                    "focus_areas": ["特殊类型招生", "招生章程", "政策解读"]
                }
            ]
        }

        # 政策变化类型
        self.policy_change_types = {
            "exam_schedule": {"name": "考试时间安排", "severity": "high"},
            "bonus_points": {"name": "加分政策", "severity": "high"},
            "admission_batches": {"name": "录取批次调整", "severity": "high"},
            "gaokao_reform": {"name": "新高考改革", "severity": "high"},
            "application_rules": {"name": "志愿填报规则", "severity": "medium"},
            "special_admission": {"name": "特殊类型招生", "severity": "medium"},
            "score_reporting": {"name": "成绩发布时间", "severity": "medium"},
            "other": {"name": "其他政策", "severity": "low"}
        }

    def run_monitoring_cycle(self):
        """执行一次监控周期"""
        print("\n" + "="*80)
        print("2026年高考政策监控周期")
        print("="*80)
        print(f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "source_results": [],
            "policy_changes": [],
            "summary": {}
        }

        # 逐个监控数据源
        for source_config in self.monitoring_config["monitored_sources"]:
            print(f"\n监控 {source_config['name']}...")

            result = self._monitor_source(source_config)
            monitoring_results["source_results"].append(result)

            if result["has_changes"]:
                monitoring_results["policy_changes"].extend(result["changes"])
                print(f"  [发现变化] {len(result['changes'])} 项政策更新")
            else:
                print(f"  [无变化] 无政策更新")

        # 生成监控报告
        self._generate_monitoring_report(monitoring_results)

        # 保存监控结果
        self._save_monitoring_results(monitoring_results)

        # 如果有重要变化，发送通知
        if monitoring_results["policy_changes"]:
            self._send_policy_notifications(monitoring_results["policy_changes"])

        print(f"\n监控周期完成: 发现 {len(monitoring_results['policy_changes'])} 项政策变化")

    def _monitor_source(self, source_config: Dict) -> Dict:
        """监控单个数据源"""
        result = {
            "source": source_config["name"],
            "timestamp": datetime.now().isoformat(),
            "has_changes": False,
            "changes": [],
            "error": None
        }

        try:
            # 获取当前页面内容
            current_content = self._fetch_page_content(source_config["url"])

            if not current_content:
                result["error"] = "无法获取页面内容"
                return result

            # 计算内容哈希
            content_hash = hashlib.md5(current_content.encode()).hexdigest()

            # 读取上次哈希
            last_hash = self._get_last_content_hash(source_config["name"])

            if content_hash != last_hash:
                print(f"  检测到页面变化，分析政策更新...")
                # 分析具体变化
                changes = self._analyze_policy_changes(
                    source_config,
                    current_content,
                    last_hash
                )

                result["has_changes"] = True
                result["changes"] = changes

                # 更新哈希记录
                self._update_content_hash(source_config["name"], content_hash)
            else:
                print(f"  页面无变化")

        except Exception as e:
            result["error"] = str(e)

        return result

    def _fetch_page_content(self, url: str) -> str:
        """获取页面内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            return response.text

        except Exception as e:
            print(f"    [ERROR] 获取页面失败: {str(e)}")
            return ""

    def _get_last_content_hash(self, source_name: str) -> str:
        """获取上次的内容哈希"""
        hash_file = self.policy_data_dir / f"{source_name}_hash.txt"

        if hash_file.exists():
            with open(hash_file, 'r', encoding='utf-8') as f:
                return f.read().strip()

        return ""

    def _update_content_hash(self, source_name: str, content_hash: str):
        """更新内容哈希记录"""
        hash_file = self.policy_data_dir / f"{source_name}_hash.txt"

        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write(content_hash)

    def _analyze_policy_changes(
        self,
        source_config: Dict,
        current_content: str,
        last_hash: str
    ) -> List[Dict]:
        """分析政策变化"""
        changes = []

        # TODO: 实现具体的政策变化分析逻辑
        # 这里需要根据各个网站的HTML结构进行定制化解析

        # 示例：查找关键词
        keywords = {
            "exam_schedule": ["考试时间", "科目安排", "统考时间"],
            "bonus_points": ["加分政策", "照顾政策", "优先录取"],
            "admission_batches": ["录取批次", "批次调整", "填报时间"],
            "gaokao_reform": ["新高考", "高考改革", "3+1+2"],
            "application_rules": ["志愿填报", "平行志愿", "征集志愿"],
            "special_admission": ["强基计划", "综合评价", "专项计划"]
        }

        for change_type, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in current_content:
                    # 发现政策关键词，记录为变化
                    change_info = self.policy_change_types[change_type]

                    changes.append({
                        "type": change_type,
                        "name": change_info["name"],
                        "severity": change_info["severity"],
                        "source": source_config["name"],
                        "keyword": keyword,
                        "description": f"发现包含'{keyword'的政策更新",
                        "url": source_config["url"],
                        "detected_at": datetime.now().isoformat()
                    })

                    break  # 每个类型只记录一次

        return changes

    def _generate_monitoring_report(self, results: Dict):
        """生成监控报告"""
        total_changes = len(results["policy_changes"])
        high_severity_changes = sum(1 for c in results["policy_changes"] if c.get("severity") == "high")

        report = f"""
2026年高考政策监控报告
{'='*60}
监控时间: {results['timestamp']}
监控数据源: {len(results['source_results'])} 个
发现政策变化: {total_changes} 项
高严重性变化: {high_severity_changes} 项

"""

        if results["policy_changes"]:
            report += "政策变化详情:\n"
            for change in results["policy_changes"]:
                severity_symbol = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(change["severity"], "⚪")

                report += f"{severity_symbol} {change['name']} ({change['source']})\n"
                report += f"   描述: {change['description']}\n"
                report += f"   链接: {change['url']}\n\n"
        else：
            report += "✅ 无政策变化，系统运行正常\n"

        report += f"\n下次监控时间: {(datetime.now() + timedelta(hours=self.monitoring_config['check_interval_hours'])).strftime('%Y-%m-%d %H:%M:%S')}"

        # 保存报告
        report_file = self.reports_dir / f"policy_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n政策监控报告已保存: {report_file}")

    def _save_monitoring_results(self, results: Dict):
        """保存监控结果（JSON格式）"""
        results_file = self.policy_data_dir / f"monitoring_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def _send_policy_notifications(self, changes: List[Dict]):
        """发送政策变化通知"""
        # 只通知高严重性变化
        high_severity_changes = [c for c in changes if c.get("severity") == "high"]

        if not high_severity_changes:
            return

        print(f"\n[重要] 发现 {len(high_severity_changes)} 项高严重性政策变化，需要发送通知")

        # TODO: 实现具体的通知逻辑
        # 1. 记录到通知日志
        # 2. 通过校讯通短信通知管理员
        # 3. 在系统界面显示提示

        notification_log = {
            "timestamp": datetime.now().isoformat(),
            "severity": "high",
            "count": len(high_severity_changes),
            "changes": high_severity_changes
        }

        log_file = self.reports_dir / "policy_notifications.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(notification_log, f, ensure_ascii=False, indent=2)

        print(f"  通知已记录到: {log_file}")

    def get_monitoring_status(self) -> Dict:
        """获取当前监控状态"""
        status = {
            "last_monitoring": None,
            "next_monitoring": (datetime.now() + timedelta(hours=self.monitoring_config["check_interval_hours"])).isoformat(),
            "monitored_sources": len(self.monitoring_config["monitored_sources"]),
            "recent_changes": []
        }

        # 读取最近的监控结果
        results_files = sorted(self.policy_data_dir.glob("monitoring_results_*.json"))
        if results_files:
            latest_file = results_files[-1]
            with open(latest_file, 'r', encoding='utf-8') as f:
                latest_results = json.load(f)
                status["last_monitoring"] = latest_results.get("timestamp")
                status["recent_changes"] = latest_results.get("policy_changes", [])[:5]  # 最近5项变化

        return status


def main():
    """主函数"""
    monitor = PolicyMonitor2026()

    try:
        monitor.run_monitoring_cycle()
        return 0
    except Exception as e:
        print(f"\n[ERROR] 监控过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())