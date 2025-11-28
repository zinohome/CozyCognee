#!/usr/bin/env python3
"""
CozyCognee MCP CORS 补丁脚本
在构建时修改 server.py 以支持 CORS_ALLOWED_ORIGINS 环境变量和 "*" 通配符
"""
import sys
import re

def patch_cors_config(file_path):
    """修改 CORS 配置以支持环境变量和 * 通配符"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经打过补丁
    if "CozyCognee Patch" in content:
        print(f"✓ {file_path} already patched")
        return True
    
    # 检查是否已经支持 "*" 通配符（即使没有 CozyCognee Patch 注释）
    # 检查是否有处理 "*" 的逻辑（使用正则表达式匹配，更宽松）
    if re.search(r'CORS_ALLOWED_ORIGINS\.strip\(\)\s*==\s*["\']\*["\']', content):
        print(f"✓ {file_path} already supports '*' wildcard")
        return True
    
    # 更宽松的检查：检查是否有 "*" 相关的逻辑
    if '"*"' in content and 'allow_credentials = False' in content and 'CORS_ALLOWED_ORIGINS' in content:
        # 检查是否在同一个函数中
        if re.search(r'CORS_ALLOWED_ORIGINS.*?\*.*?allow_credentials\s*=\s*False', content, re.DOTALL):
            print(f"✓ {file_path} already supports '*' wildcard (detected via pattern)")
            return True
    
    # 模式：匹配当前代码结构（支持环境变量但不支持 "*"）
    # 匹配 run_sse_with_cors 和 run_http_with_cors 函数中的 CORS 配置
    # 查找模式：从 "# Read allowed origins" 到 "allow_credentials=True" 的整个块
    
    # SSE 版本的匹配模式
    sse_pattern = r'(# Read allowed origins from environment variable \(comma-separated\).*?allow_credentials = True\n    \n    sse_app\.add_middleware\(\n        CORSMiddleware,\n        allow_origins=allowed_origins,\n        allow_credentials=allow_credentials,)'
    
    # HTTP 版本的匹配模式
    http_pattern = r'(# Read allowed origins from environment variable \(comma-separated\).*?allow_credentials = True\n    \n    http_app\.add_middleware\(\n        CORSMiddleware,\n        allow_origins=allowed_origins,\n        allow_credentials=allow_credentials,)'
    
    # 补丁后的代码（支持 "*" 通配符）
    patched_sse_code = '''# Read allowed origins from environment variable (comma-separated)
    # CozyCognee Patch: Support "*" to allow all origins
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
    if CORS_ALLOWED_ORIGINS:
        # Support "*" to allow all origins (for development/testing)
        if CORS_ALLOWED_ORIGINS.strip() == "*":
            allowed_origins = ["*"]
            # When using "*", we cannot use allow_credentials=True
            # This is a browser security restriction
            allow_credentials = False
        else:
            allowed_origins = [
                origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
            ]
            allow_credentials = True
    else:
        allowed_origins = [
            os.getenv("UI_APP_URL", "http://localhost:3000"),
        ]
        allow_credentials = True
    
    sse_app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,'''
    
    patched_http_code = patched_sse_code.replace('sse_app', 'http_app')
    
    patched = False
    
    # 替换 SSE 版本的 CORS 配置
    if re.search(sse_pattern, content, re.DOTALL):
        content = re.sub(sse_pattern, patched_sse_code, content, flags=re.DOTALL)
        patched = True
        print(f"✓ Patched run_sse_with_cors")
    
    # 替换 HTTP 版本的 CORS 配置
    if re.search(http_pattern, content, re.DOTALL):
        content = re.sub(http_pattern, patched_http_code, content, flags=re.DOTALL)
        patched = True
        print(f"✓ Patched run_http_with_cors")
    
    # 如果正则匹配失败，尝试更简单的字符串替换
    if not patched:
        # 查找并替换简单的模式（不支持 "*" 的版本）
        simple_pattern = '''if CORS_ALLOWED_ORIGINS:
        if CORS_ALLOWED_ORIGINS.strip() == "*":
            # 使用 * 时不能设置 allow_credentials=True
            allowed_origins = ["*"]
            allow_credentials = False
        else:
            allowed_origins = [
                origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
            ]
            allow_credentials = True
    else:
        allowed_origins = [
            os.getenv("UI_APP_URL", "http://localhost:3000"),
        ]
        allow_credentials = True'''
        
        # 如果已经包含这个模式，说明已经支持 "*"，不需要补丁
        if simple_pattern in content:
            print(f"✓ {file_path} already supports '*' wildcard (different format)")
            return True
        
        # 尝试匹配更简单的模式（没有 "*" 支持的版本）
        old_pattern = '''if CORS_ALLOWED_ORIGINS:
        allowed_origins = [
            origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
        ]
    else:
        allowed_origins = [
            os.getenv("UI_APP_URL", "http://localhost:3000"),
        ]'''
        
        new_pattern = '''if CORS_ALLOWED_ORIGINS:
        # CozyCognee Patch: Support "*" to allow all origins
        if CORS_ALLOWED_ORIGINS.strip() == "*":
            allowed_origins = ["*"]
            # When using "*", we cannot use allow_credentials=True
            # This is a browser security restriction
            allow_credentials = False
        else:
            allowed_origins = [
                origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
            ]
            allow_credentials = True
    else:
        allowed_origins = [
            os.getenv("UI_APP_URL", "http://localhost:3000"),
        ]
        allow_credentials = True'''
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern, 2)  # 替换两次（SSE 和 HTTP）
            patched = True
            print(f"✓ Patched CORS configuration (simple pattern)")
    
    if patched:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Successfully patched {file_path}")
        return True
    else:
        # 如果无法匹配模式，再次检查是否已经支持 "*"
        # 这可能是代码格式略有不同，但功能已经支持
        if re.search(r'CORS_ALLOWED_ORIGINS.*?strip.*?\*', content, re.DOTALL):
            print(f"⚠ Warning: Could not find exact CORS configuration pattern in {file_path}")
            print("But the file appears to already support '*' wildcard.")
            print("✓ Skipping patch (already supported)")
            return True
        
        print(f"⚠ Warning: Could not find CORS configuration pattern in {file_path}")
        print("File may already be patched or has a different structure.")
        # 如果代码中有 CORS_ALLOWED_ORIGINS 和 allow_origins，说明至少支持环境变量
        # 在这种情况下，即使没有 "*" 支持，也返回 True（避免构建失败）
        # 用户可以通过环境变量设置具体的 URL 列表
        if 'CORS_ALLOWED_ORIGINS = os.getenv' in content and 'allow_origins' in content:
            print("✓ File has CORS configuration with environment variable support")
            print("  (If '*' support is needed, it may need manual patching)")
            return True
        
        return False

if __name__ == "__main__":
    file_path = "/app/src/server.py"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    success = patch_cors_config(file_path)
    sys.exit(0 if success else 1)

