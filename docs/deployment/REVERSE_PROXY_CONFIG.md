# 反向代理配置文件位置

## 配置文件位置

所有反向代理配置文件都存储在 `/data/cognee` 目录下：

```
/data/cognee/
├── nginx/
│   ├── nginx.conf          # Nginx 配置文件
│   └── logs/               # Nginx 日志目录
│       ├── access.log
│       └── error.log
└── caddy/
    ├── Caddyfile           # Caddy 配置文件
    ├── data/               # Caddy 数据目录（证书等）
    └── config/             # Caddy 配置目录
```

## 配置文件路径

### Nginx

- **配置文件**: `/data/cognee/nginx/nginx.conf`
- **日志目录**: `/data/cognee/nginx/logs/`

### Caddy

- **配置文件**: `/data/cognee/caddy/Caddyfile`
- **数据目录**: `/data/cognee/caddy/data/`
- **配置目录**: `/data/cognee/caddy/config/`

## 初始化配置

首次部署前，需要将配置文件复制到 `/data/cognee` 目录：

```bash
# 创建目录
mkdir -p /data/cognee/nginx/logs
mkdir -p /data/cognee/caddy/{data,config}

# 复制 Nginx 配置文件
cp deployment/nginx/nginx.conf /data/cognee/nginx/nginx.conf

# 复制 Caddy 配置文件
cp deployment/caddy/Caddyfile /data/cognee/caddy/Caddyfile
```

## 修改配置

### Nginx

编辑配置文件：
```bash
vi /data/cognee/nginx/nginx.conf
```

重启服务使配置生效：
```bash
docker-compose -f deployment/docker-compose.1panel.yml restart nginx
```

### Caddy

编辑配置文件：
```bash
vi /data/cognee/caddy/Caddyfile
```

重启服务使配置生效：
```bash
docker-compose -f deployment/docker-compose.1panel.yml restart caddy
```

## 注意事项

1. **文件权限**：确保配置文件有正确的读取权限
   ```bash
   chmod 644 /data/cognee/nginx/nginx.conf
   chmod 644 /data/cognee/caddy/Caddyfile
   ```

2. **配置文件备份**：建议定期备份配置文件
   ```bash
   cp /data/cognee/nginx/nginx.conf /data/cognee/nginx/nginx.conf.backup
   cp /data/cognee/caddy/Caddyfile /data/cognee/caddy/Caddyfile.backup
   ```

3. **日志管理**：定期清理日志文件，避免占用过多磁盘空间
   ```bash
   # 清理 Nginx 日志（保留最近 7 天）
   find /data/cognee/nginx/logs -name "*.log" -mtime +7 -delete
   ```

4. **配置验证**：修改配置后，验证配置是否正确
   ```bash
   # Nginx 配置验证
   docker exec cognee_nginx nginx -t
   
   # Caddy 配置验证
   docker exec cognee_caddy caddy validate --config /etc/caddy/Caddyfile
   ```

