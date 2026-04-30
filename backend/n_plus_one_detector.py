"""
N+1查询问题检测和消除脚本
识别代码中的性能问题并提供修复方案
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

class NPlusOneDetector:
    """N+1查询检测器"""

    def __init__(self):
        self.project_root = Path("app")
        self.issues = []

    def scan_codebase(self) -> Dict[str, Any]:
        """扫描代码库，识别N+1查询问题"""
        print("开始扫描N+1查询问题...")

        scan_result = {
            "total_files_scanned": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "issues": []
        }

        # 扫描Python文件
        python_files = list(self.project_root.rglob("*.py"))
        scan_result["total_files_scanned"] = len(python_files)

        for file_path in python_files:
            file_issues = self._analyze_file(file_path)
            if file_issues:
                scan_result["files_with_issues"] += 1
                scan_result["total_issues"] += len(file_issues)
                scan_result["issues"].extend(file_issues)

        print(f"扫描完成：扫描了{scan_result['total_files_scanned']}个文件")
        print(f"发现{scan_result['files_with_issues']}个文件有N+1查询问题")
        print(f"总计{scan_result['total_issues']}个问题")

        return scan_result

    def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """分析单个文件的N+1查询问题"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # 解析AST
            tree = ast.parse(content)

            # 检查循环内查询数据库的模式
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    issues.extend(self._check_loop_for_queries(node, lines, file_path))
                elif isinstance(node, ast.While):
                    issues.extend(self._check_loop_for_queries(node, lines, file_path))

        except Exception as e:
            issues.append({
                "file": str(file_path),
                "line": 0,
                "type": "parse_error",
                "message": f"无法解析文件: {str(e)}",
                "severity": "low"
            })

        return issues

    def _check_loop_for_queries(
        self,
        loop_node: ast.For,
        lines: List[str],
        file_path: Path
    ) -> List[Dict[str, Any]]:
        """检查循环内的数据库查询"""
        issues = []

        # 检查循环体
        for body_item in loop_node.body:
            if isinstance(body_item, list):
                for statement in body_item:
                    if isinstance(statement, ast.Call):
                        # 检查是否是数据库查询
                        if self._is_database_call(statement):
                            issues.append({
                                "file": str(file_path),
                                "line": statement.lineno,
                                "type": "n_plus_one_query",
                                "message": "循环内发现数据库查询，可能导致N+1问题",
                                "severity": "high",
                                "suggestion": "建议使用批量查询或预加载"
                            })

        return issues

    def _is_database_call(self, call_node: ast.Call) -> bool:
        """检查是否是数据库调用"""
        # 检查常见的数据库操作
        database_keywords = [
            "query", "execute", "select", "insert", "update", "delete",
            "find", "filter", "search"
        ]

        # 简化的检查逻辑
        for keyword in database_keywords:
            if keyword in ast.dump(call_node).lower():
                return True

        return False

    def generate_optimization_suggestions(
        self,
        scan_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []

        if scan_result["total_issues"] == 0:
            return [{
                "type": "good",
                "message": "未发现N+1查询问题，代码质量良好"
            }]

        # 按严重程度分组
        high_severity = [i for i in scan_result["issues"] if i.get("severity") == "high"]
        medium_severity = [i for i in scan_result["issues"] if i.get("severity") == "medium"]

        if high_severity:
            suggestions.append({
                "type": "high_priority",
                "count": len(high_severity),
                "message": f"发现{len(high_severity)}个高优先级N+1查询问题",
                "actions": [
                    "使用批量查询替代循环查询",
                    "实现预加载机制",
                    "使用join或include减少查询次数"
                ]
            })

        if medium_severity:
            suggestions.append({
                "type": "medium_priority",
                "count": len(medium_severity),
                "message": f"发现{len(medium_severity)}个中等优先级问题",
                "actions": [
                    "考虑添加缓存层",
                    "优化查询逻辑"
                ]
            })

        return suggestions

    def generate_fix_example(self) -> str:
        """生成修复示例"""
        return """
# N+1查询问题修复示例

## ❌ 错误示例（N+1查询）
for university in universities:
    admission = db.query(
        "SELECT * FROM admission_scores WHERE university_id = ?",
        (university.id,)
    )

## ✅ 正确示例（批量查询）
university_ids = [u.id for u in universities]
admissions = db.query(
    "SELECT * FROM admission_scores WHERE university_id IN (?)",
    (university_ids,)
)

# 或使用ORM的join
admissions = db.query(AdmissionScore).filter(
    AdmissionScore.university_id.in_(university_ids)
).all()

## 🚀 进一步优化：使用select_related/prefetch
admissions = University.query.options(
    select_related('admission_scores'),
    prefetch_related('majors')
).all()
        """


def main():
    """主函数"""
    detector = NPlusOneDetector()

    print("=== N+1查询检测 ===")

    # 扫描代码库
    scan_result = detector.scan_codebase()

    # 生成优化建议
    suggestions = detector.generate_optimization_suggestions(scan_result)

    print("\n=== 优化建议 ===")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['message']}")
        if 'actions' in suggestion:
            print("   建议操作:")
            for action in suggestion['actions']:
                print(f"   - {action}")

    # 生成修复示例
    print("\n=== 修复示例 ===")
    print(detector.generate_fix_example())

    # 保存报告
    report = {
        "scan_summary": scan_result,
        "optimization_suggestions": suggestions,
        "fix_examples": detector.generate_fix_example()
    }

    import json
    with open('n_plus_one_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n报告已保存到: n_plus_one_report.json")


if __name__ == "__main__":
    main()