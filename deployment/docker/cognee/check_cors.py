#!/usr/bin/env python3
"""
检查 CORS 配置的脚本
用于验证补丁是否正确应用
"""
import os
import sys

def check_cors_config():
    """检查 CORS 配置"""
    client_py_path = "/app/cognee/api/client.py"
    if len(sys.argv) > 1:
        client_py_path = sys.argv[1]
    
    print("=" * 60)
    print("CORS 配置检查")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(client_py_path):
        print(f"❌ 文件不存在: {client_py_path}")
        return False
    
    # 读取文件内容
    with open(client_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含补丁代码
    has_patch = "CozyCognee Patch" in content or 'if CORS_ALLOWED_ORIGINS.strip() == "*"' in content
    
    if has_patch:
        print("✅ 补丁已应用")
    else:
        print("❌ 补丁未应用")
    
    # 检查环境变量
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS")
    print(f"\n环境变量 CORS_ALLOWED_ORIGINS: {cors_origins}")
    
    if cors_origins:
        if cors_origins.strip() == "*":
            print("⚠️  使用 '*' 通配符，allow_credentials 将被设置为 False")
        else:
            origins_list = [o.strip() for o in cors_origins.split(",") if o.strip()]
            print(f"✅ 允许的来源: {origins_list}")
    else:
        print("⚠️  未设置 CORS_ALLOWED_ORIGINS，将使用默认值")
    
    # 检查代码中的关键部分
    print("\n代码检查:")
    if 'allow_credentials=allow_credentials' in content:
        print("✅ 使用动态 allow_credentials 变量")
    elif 'allow_credentials=True' in content:
        print("⚠️  使用固定的 allow_credentials=True（可能不支持 '*'）")
    
    if 'allowed_origins = ["*"]' in content:
        print("✅ 支持 '*' 通配符")
    
    print("\n" + "=" * 60)
    return has_patch

if __name__ == "__main__":
    success = check_cors_config()
    sys.exit(0 if success else 1)

