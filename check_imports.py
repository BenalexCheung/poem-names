#!/usr/bin/env python3
"""
检查项目中所有Python文件的导入是否正确
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def check_import(module_path, class_name=None):
    """检查模块导入"""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else [])
        if class_name:
            getattr(module, class_name)
        print(f"✅ {module_path}" + (f" -> {class_name}" if class_name else ""))
        return True
    except Exception as e:
        print(f"❌ {module_path}" + (f" -> {class_name}" if class_name else "") + f": {e}")
        return False

def main():
    """主检查函数"""
    print("🔍 检查项目导入...")

    # 检查主要模块
    checks = [
        ("gen_names.models", None),
        ("gen_names.views", "UserViewSet"),
        ("gen_names.serializers", None),
        ("gen_names.generator", None),
        ("gen_names.authentication.views", None),
        ("gen_names.authentication.serializers", None),
        ("gen_names.authentication.backends", None),
    ]

    all_passed = True
    for module_path, class_name in checks:
        if not check_import(module_path, class_name):
            all_passed = False

    if all_passed:
        print("\n🎉 所有导入检查通过！")
    else:
        print("\n⚠️  发现导入问题，请修复后再运行。")
        sys.exit(1)

if __name__ == "__main__":
    main()