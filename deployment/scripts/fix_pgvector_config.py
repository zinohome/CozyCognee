#!/usr/bin/env python3
"""
批量修复所有 docker-compose 文件，移除 pgvector 服务并更新配置
"""
import re
import sys
from pathlib import Path

def fix_docker_compose_file(file_path: Path):
    """修复单个 docker-compose 文件"""
    print(f"处理文件: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 更新向量数据库配置注释（第一个出现的地方，通常是 cognee 服务）
    content = re.sub(
        r'# ==================== 向量数据库配置 ====================\s*# 使用 pgvector \(独立的 pgvector 服务\)\s*- VECTOR_DB_PROVIDER=pgvector\s*- VECTOR_DB_URL=postgresql://[^\n]+\s*# 如果使用其他向量数据库',
        '# ==================== 向量数据库配置 ====================\n      # 使用 pgvector (向量数据存储在关系数据库中，与关系数据共享同一个 PostgreSQL 实例)\n      # 注意：Cognee 的设计是当 VECTOR_DB_PROVIDER=pgvector 时，会忽略 VECTOR_DB_URL，\n      # 而是使用 DATABASE_URL 指向的数据库。因此向量数据和关系数据在同一数据库中。\n      - VECTOR_DB_PROVIDER=pgvector\n      # VECTOR_DB_URL 会被忽略，不需要配置\n      # 如果使用其他向量数据库',
        content,
        count=1
    )
    
    # 2. 更新向量数据库配置（第二个出现的地方，通常是 cognee-mcp-direct 服务）
    content = re.sub(
        r'# ==================== 向量数据库配置 ====================\s*- VECTOR_DB_PROVIDER=pgvector\s*- VECTOR_DB_URL=postgresql://[^\n]+',
        '# ==================== 向量数据库配置 ====================\n      # 使用 pgvector (向量数据存储在关系数据库中，与关系数据共享同一个 PostgreSQL 实例)\n      # 注意：Cognee 的设计是当 VECTOR_DB_PROVIDER=pgvector 时，会忽略 VECTOR_DB_URL，\n      # 而是使用 DATABASE_URL 指向的数据库。因此向量数据和关系数据在同一数据库中。\n      - VECTOR_DB_PROVIDER=pgvector\n      # VECTOR_DB_URL 会被忽略，不需要配置',
        content,
        count=1
    )
    
    # 3. 删除 depends_on 中的 pgvector
    content = re.sub(
        r'      pgvector:\s+condition: service_started\s+',
        '',
        content
    )
    
    # 4. 更新 postgres 镜像
    content = re.sub(
        r'  # PostgreSQL 关系数据库\s+postgres:\s+image: postgres:15-alpine',
        '  # PostgreSQL 关系数据库（使用带 pgvector 扩展的镜像）\n  # 注意：向量数据也存储在此数据库中，Cognee 的设计是向量数据和关系数据在同一数据库\n  postgres:\n    image: pgvector/pgvector:0.8.1-pg17-trixie',
        content
    )
    content = re.sub(
        r'  # PostgreSQL 关系数据库（使用带 pgvector 扩展的镜像）\s+postgres:\s+image: pgvector/pgvector:pg15',
        '  # PostgreSQL 关系数据库（使用带 pgvector 扩展的镜像）\n  # 注意：向量数据也存储在此数据库中，Cognee 的设计是向量数据和关系数据在同一数据库\n  postgres:\n    image: pgvector/pgvector:0.8.1-pg17-trixie',
        content
    )
    
    # 5. 删除 pgvector 服务定义
    content = re.sub(
        r'  # pgvector 向量数据库[^\n]+\n  pgvector:\s+image: pgvector/pgvector:[^\n]+\s+container_name: cognee_pgvector\s+restart: unless-stopped\s+ports:\s+- "[^\n]+"\s+environment:\s+- POSTGRES_USER=[^\n]+\s+- POSTGRES_PASSWORD=[^\n]+\s+- POSTGRES_DB=[^\n]+\s+- PGDATA=[^\n]+\s+volumes:\s+- [^\n]+\s+networks:\s+- [^\n]+\s+labels:\s+createdBy: "[^\n]+"\s+interval: [^\n]+\s+timeout: [^\n]+\s+retries: [^\n]+\s+',
        '',
        content
    )
    
    # 6. 删除 volumes 中的 pgvector_data
    content = re.sub(
        r'  pgvector_data:\s*\n',
        '',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已更新")
        return True
    else:
        print(f"  - 无需更新")
        return False

def main():
    deployment_dir = Path(__file__).parent.parent
    docker_compose_files = list(deployment_dir.glob('docker-compose*.yml'))
    
    print(f"找到 {len(docker_compose_files)} 个 docker-compose 文件\n")
    
    updated_count = 0
    for file_path in sorted(docker_compose_files):
        if fix_docker_compose_file(file_path):
            updated_count += 1
        print()
    
    print(f"完成！共更新 {updated_count} 个文件")

if __name__ == '__main__':
    main()

