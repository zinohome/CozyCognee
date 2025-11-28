#!/usr/bin/env python3
"""
CozyCognee CORS 补丁脚本
在构建时修改 client.py 以支持 CORS_ALLOWED_ORIGINS=*
"""
import re
import sys

def patch_cors_config(file_path):
    """修改 CORS 配置以支持 * 通配符"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 CORS 配置部分
    pattern = r'(# Read allowed origins from environment variable \(comma-separated\)\nCORS_ALLOWED_ORIGINS = os\.getenv\("CORS_ALLOWED_ORIGINS"\)\nif CORS_ALLOWED_ORIGINS:\n    allowed_origins = \[\n        origin\.strip\(\) for origin in CORS_ALLOWED_ORIGINS\.split\(","\) if origin\.strip\(\)\n    \]\nelse:\n    allowed_origins = \[\n        os\.getenv\("UI_APP_URL", "http://localhost:3000"\),\n    \]  # Block all except explicitly set origins\n\napp\.add_middleware\(\n    CORSMiddleware,\n    allow_origins=allowed_origins,  # Now controlled by env var\n    allow_credentials=True,)'
    
    replacement = '''# Read allowed origins from environment variable (comma-separated)
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
    ]  # Block all except explicitly set origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Now controlled by env var
    allow_credentials=allow_credentials,'''
    
    # 使用更简单的模式匹配
    old_pattern = '''# Read allowed origins from environment variable (comma-separated)
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
if CORS_ALLOWED_ORIGINS:
    allowed_origins = [
        origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
    ]
else:
    allowed_origins = [
        os.getenv("UI_APP_URL", "http://localhost:3000"),
    ]  # Block all except explicitly set origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Now controlled by env var
    allow_credentials=True,'''
    
    if old_pattern in content:
        new_content = content.replace(old_pattern, replacement)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Successfully patched {file_path}")
        return True
    else:
        print(f"⚠ Warning: CORS configuration pattern not found in {file_path}")
        print("File may already be patched or has a different structure.")
        return False

if __name__ == "__main__":
    file_path = "/app/cognee/api/client.py"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    success = patch_cors_config(file_path)
    sys.exit(0 if success else 1)

