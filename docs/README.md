# CozyCognee 文档

欢迎使用 CozyCognee 文档！本文档提供了完整的部署、开发和使用指南。

## 📚 文档目录

### [部署文档](./deployment/README.md)
详细的部署指南，包括：
- 标准 Docker Compose 部署
- 1Panel 部署
- 环境配置
- 服务说明
- 故障排查

### [pgvector 配置指南](./deployment/PGVECTOR_SETUP.md)
pgvector 向量数据库配置和使用指南：
- PostgreSQL 配置
- 环境变量设置
- 性能优化
- 故障排查

### [服务分离配置](./deployment/PGVECTOR_SEPARATION.md)
PostgreSQL 和 pgvector 服务分离配置说明：
- 服务配置
- 代码限制说明
- 配置方案
- 推荐配置

### [开发文档](./development/README.md)
开发环境配置和开发指南：
- 开发环境设置
- 本地开发
- Docker 开发
- 代码同步

### [使用文档](./usage/README.md)
使用方法和最佳实践：
- 快速开始
- API 使用
- 前端使用
- MCP 集成

### [知识库](./knowledge/README.md)
心理咨询知识库，面向心理咨询师实际操作：
- 心理咨询基础理论
- 咨询技巧和方法
- 常见心理问题处理
- 咨询流程和规范
- 案例分析和实践
- **青少年心理咨询专题**（新增）
  - 青少年心理咨询基础
  - 青少年常见心理问题及处理
  - 青少年咨询技巧和方法
  - 青少年咨询案例分析

## 🚀 快速链接

- [项目主页](../README.md)
- [部署指南](./deployment/README.md)
- [pgvector 配置](./deployment/PGVECTOR_SETUP.md)
- [开发指南](./development/README.md)
- [使用指南](./usage/README.md)
- [知识库](./knowledge/README.md)

## 📖 文档结构

```
docs/
├── README.md           # 本文档
├── deployment/         # 部署相关文档
│   ├── README.md      # 部署指南
│   └── PGVECTOR_SETUP.md # pgvector 配置指南
├── development/        # 开发相关文档
│   ├── README.md      # 开发指南
│   ├── LOCAL_DEV_SETUP.md # 本地开发配置
│   └── QUICK_START_COGNEE.md # 快速启动
├── usage/             # 使用相关文档
│   └── README.md      # 使用指南
└── knowledge/         # 知识库
    ├── README.md      # 知识库索引
    ├── 01-psychological-counseling-fundamentals.md # 心理咨询基础理论
    ├── 02-counseling-techniques-and-methods.md # 咨询技巧和方法
    ├── 03-common-psychological-issues.md # 常见心理问题处理
    ├── 04-counseling-process-and-standards.md # 咨询流程和规范
    ├── 05-case-analysis-and-practice.md # 案例分析和实践
    ├── 06-adolescent-counseling-fundamentals.md # 青少年心理咨询基础
    ├── 07-adolescent-common-issues.md # 青少年常见心理问题及处理
    ├── 08-adolescent-counseling-techniques.md # 青少年咨询技巧和方法
    └── 09-adolescent-case-analysis.md # 青少年咨询案例分析
```

## 🔍 查找帮助

- **部署问题**: 查看 [部署文档](./deployment/README.md) 的故障排查部分
- **pgvector 配置**: 查看 [pgvector 配置指南](./deployment/PGVECTOR_SETUP.md)
- **开发问题**: 查看 [开发文档](./development/README.md) 的常见问题部分
- **使用问题**: 查看 [使用文档](./usage/README.md) 的故障排查部分
- **心理咨询知识**: 查看 [知识库](./knowledge/README.md) 获取心理咨询相关知识和实践指导

## 📝 贡献文档

如果您发现文档有误或需要改进，欢迎提交 Issue 或 Pull Request！

## 🔗 相关资源

- [Cognee 官方文档](https://docs.cognee.ai)
- [Cognee GitHub](https://github.com/topoteretes/cognee)
- [pgvector 官方文档](https://github.com/pgvector/pgvector)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Docker 文档](https://docs.docker.com)
- [1Panel 文档](https://1panel.cn/docs/)
