"""
测试OpenAPI生成问题
"""
import sys
import traceback
sys.path.append('D:\\xuefeng_volunteer\\backend')

try:
    print("Testing OpenAPI schema generation...")

    from app.main import app
    print("[OK] App imported successfully")

    # 尝试生成OpenAPI schema
    print("\nGenerating OpenAPI schema...")
    schema = app.openapi()
    print("[OK] OpenAPI schema generated successfully")
    print(f"Schema keys: {list(schema.keys())}")
    print(f"Total endpoints: {len(schema.get('paths', {}))}")

    # 检查路径
    print("\nFirst few paths:")
    for i, path in enumerate(list(schema.get('paths', {}).keys())[:5]):
        print(f"  {i+1}. {path}")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
