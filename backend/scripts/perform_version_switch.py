"""
数据版本切换脚本
执行数据版本的切换操作
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.collection_service import get_collection_service


def backup_current_data(year: int) -> Path:
    """备份当前年份数据"""
    backup_dir = project_root / "data" / "backups" / f"backup_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 备份文件列表
    files_to_backup = [
        "universities_list.json",
        "major_rank_data.json",
        "majors_list.json"
    ]

    print(f"备份 {year} 年数据到: {backup_dir}")

    for filename in files_to_backup:
        src_file = project_root / "data" / filename
        if src_file.exists():
            dst_file = backup_dir / filename
            shutil.copy2(src_file, dst_file)
            print(f"  已备份: {filename}")
        else:
            print(f"  跳过: {filename} (不存在)")

    return backup_dir


def restore_backup(backup_path: Path) -> bool:
    """从备份恢复数据"""
    data_dir = project_root / "data"

    print(f"从备份恢复数据: {backup_path}")

    for backup_file in backup_path.glob("*.json"):
        target_file = data_dir / backup_file.name
        shutil.copy2(backup_file, target_file)
        print(f"  已恢复: {backup_file.name}")

    return True


def switch_data_version(from_year: int, to_year: int, auto_mode: bool = False) -> dict:
    """
    切换数据版本

    Args:
        from_year: 源年份
        to_year: 目标年份
        auto_mode: 自动模式（无需确认）

    Returns:
        切换结果
    """
    print(f"\n{'='*50}")
    print(f"数据版本切换: {from_year} → {to_year}")
    print(f"{'='*50}")

    service = get_collection_service()

    # 1. 检查目标版本状态
    print(f"\n[1/4] 检查目标版本状态...")
    target_version = service.get_version(to_year)

    if not target_version:
        return {
            "success": False,
            "message": f"版本 {to_year} 不存在"
        }

    print(f"  状态: {target_version['status']}")
    print(f"  数据完整度: {target_version['data_completeness']}%")
    print(f"  院校数量: {target_version['university_count']}")
    print(f"  专业数量: {target_version['major_count']}")

    if target_version['status'] not in ['ready', 'active']:
        return {
            "success": False,
            "message": f"版本 {to_year} 状态为 {target_version['status']}，无法切换"
        }

    # 2. 备份当前数据
    print(f"\n[2/4] 备份当前数据...")
    try:
        backup_path = backup_current_data(from_year)
    except Exception as e:
        return {
            "success": False,
            "message": f"备份失败: {str(e)}"
        }

    # 3. 确认切换
    print(f"\n[3/4] 确认切换...")
    if not auto_mode:
        confirm = input(f"确认要切换到 {to_year} 年数据吗？(yes/no): ")
        if confirm.lower() != 'yes':
            return {
                "success": False,
                "message": "用户取消切换"
            }

    # 4. 执行切换
    print(f"\n[4/4] 执行版本切换...")

    result = service.switch_version(
        to_year=to_year,
        switch_type="auto" if auto_mode else "manual",
        switched_by="script",
        reason=f"从 {from_year} 年切换到 {to_year} 年"
    )

    if result["success"]:
        print(f"  ✓ 切换成功!")
        print(f"  当前活跃版本: {to_year}")

        # 记录备份位置
        print(f"\n备份数据保存在: {backup_path}")
        print(f"如需回退，请使用备份目录: {backup_path.name}")
    else:
        print(f"  ✗ 切换失败: {result['message']}")

    return result


def rollback_to_backup(backup_path: Path) -> dict:
    """
    回滚到指定备份

    Args:
        backup_path: 备份目录路径

    Returns:
        回滚结果
    """
    print(f"\n{'='*50}")
    print(f"数据回滚")
    print(f"{'='*50}")

    service = get_collection_service()

    # 获取当前活跃版本
    current_version = service.get_active_version()
    current_year = current_version['year'] if current_version else 2026

    # 从备份路径解析年份
    try:
        backup_year = int(backup_path.name.split('_')[1])
    except (IndexError, ValueError):
        backup_year = 2025

    print(f"当前版本: {current_year}")
    print(f"回退到: {backup_year}")

    # 恢复数据
    try:
        restore_backup(backup_path)

        # 切换版本
        result = service.switch_version(
            to_year=backup_year,
            switch_type="rollback",
            switched_by="script",
            reason=f"从 {current_year} 回退到 {backup_year}"
        )

        if result["success"]:
            print(f"  ✓ 回滚成功!")
        else:
            print(f"  ✗ 版本切换失败: {result['message']}")

        return result

    except Exception as e:
        return {
            "success": False,
            "message": f"回滚失败: {str(e)}"
        }


def list_backups() -> list:
    """列出所有备份"""
    backup_dir = project_root / "data" / "backups"

    if not backup_dir.exists():
        return []

    backups = []
    for backup_path in sorted(backup_dir.iterdir(), reverse=True):
        if backup_path.is_dir():
            # 解析备份信息
            name_parts = backup_path.stem.split('_')
            if len(name_parts) >= 3:
                try:
                    year = int(name_parts[1])
                    backups.append({
                        "path": backup_path,
                        "name": backup_path.name,
                        "year": year,
                        "created": datetime.fromtimestamp(backup_path.stat().st_ctime).isoformat()
                    })
                except ValueError:
                    continue

    return backups


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据版本切换工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 切换命令
    switch_parser = subparsers.add_parser("switch", help="切换数据版本")
    switch_parser.add_argument("--to", type=int, required=True, help="目标年份")
    switch_parser.add_argument("--from", type=int, dest="from_year", help="源年份（默认：当前活跃版本）")
    switch_parser.add_argument("--auto", action="store_true", help="自动模式（无需确认）")

    # 回滚命令
    rollback_parser = subparsers.add_parser("rollback", help="回滚到备份")
    rollback_parser.add_argument("backup", help="备份目录名称")

    # 列出备份命令
    subparsers.add_parser("list-backups", help="列出所有备份")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "switch":
        service = get_collection_service()

        # 确定源年份
        from_year = args.from_year
        if from_year is None:
            current_version = service.get_active_version()
            from_year = current_version['year'] if current_version else 2025

        result = switch_data_version(from_year, args.to, args.auto)

        if result["success"]:
            print(f"\n✓ {result['message']}")
            sys.exit(0)
        else:
            print(f"\n✗ {result['message']}")
            sys.exit(1)

    elif args.command == "rollback":
        backup_dir = project_root / "data" / "backups" / args.backup

        if not backup_dir.exists():
            print(f"错误: 备份不存在: {backup_dir}")
            sys.exit(1)

        result = rollback_to_backup(backup_dir)

        if result["success"]:
            print(f"\n✓ 回滚成功")
            sys.exit(0)
        else:
            print(f"\n✗ {result['message']}")
            sys.exit(1)

    elif args.command == "list-backups":
        backups = list_backups()

        if not backups:
            print("没有找到备份")
        else:
            print("\n可用的备份:")
            print("-" * 50)
            for backup in backups:
                print(f"  {backup['name']}")
                print(f"    年份: {backup['year']}")
                print(f"    创建时间: {backup['created']}")
                print()


if __name__ == "__main__":
    main()
