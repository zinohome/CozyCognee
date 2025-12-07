# Cognee SDK 发布指南

本文档介绍如何将 cognee-sdk 发布到 PyPI。

## 📋 发布前检查清单

- [ ] 所有测试通过：`pytest`
- [ ] 代码质量检查通过：`ruff check .` 和 `mypy cognee_sdk/`
- [ ] 更新版本号（在 `pyproject.toml` 中）
- [ ] 更新 CHANGELOG.md
- [ ] 确保所有更改已提交到 Git
- [ ] 创建 Git tag

## 🚀 发布步骤

### 1. 准备发布环境

```bash
cd cognee_sdk

# 安装构建工具
pip install --upgrade build twine

# 确保虚拟环境已激活
source venv/bin/activate
```

### 2. 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
version = "0.1.0"  # 更新为新版本，如 "0.1.1"
```

### 3. 更新 CHANGELOG

在 `CHANGELOG.md` 中添加新版本的变更记录。

### 4. 构建分发包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info

# 构建分发包
python -m build
```

这会生成：
- `dist/cognee_sdk-0.1.0.tar.gz` - 源码分发包
- `dist/cognee_sdk-0.1.0-py3-none-any.whl` - 轮子分发包

### 5. 检查分发包

```bash
# 检查分发包
twine check dist/*
```

### 6. 测试发布（推荐）

首先发布到 TestPyPI 进行测试：

```bash
# 发布到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ cognee-sdk
```

### 7. 发布到 PyPI

```bash
# 发布到正式 PyPI
twine upload dist/*
```

需要输入 PyPI 的用户名和密码（或 API token）。

### 8. 创建 Git Tag

```bash
# 创建版本标签
git tag -a v0.1.0 -m "Release version 0.1.0"

# 推送标签
git push origin v0.1.0
```

## 🔐 PyPI 账户设置

### 创建 PyPI 账户

1. 访问 https://pypi.org/account/register/
2. 注册账户并验证邮箱

### 使用 API Token（推荐）

1. 登录 PyPI
2. 进入 Account settings → API tokens
3. 创建新的 API token
4. 使用 token 作为密码：

```bash
twine upload dist/*
# Username: __token__
# Password: pypi-xxxxxxxxxxxxx（你的 API token）
```

## 📝 版本号规范

遵循 [语义化版本](https://semver.org/)：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

示例：
- `0.1.0` → `0.1.1`（bug 修复）
- `0.1.0` → `0.2.0`（新功能）
- `0.1.0` → `1.0.0`（重大变更）

## 🔄 发布后验证

```bash
# 等待几分钟后，验证发布
pip install --upgrade cognee-sdk

# 验证版本
python -c "import cognee_sdk; print(cognee_sdk.__version__)"
```

## ⚠️ 注意事项

1. **版本号不能回退**：一旦发布到 PyPI，不能使用相同的版本号重新发布
2. **测试先行**：建议先在 TestPyPI 上测试
3. **文档同步**：确保 README 和文档是最新的
4. **依赖检查**：确保所有依赖都已正确声明

## 🐛 常见问题

### Q: 发布失败，提示版本已存在

A: 需要更新版本号，不能重复使用已发布的版本号。

### Q: 如何撤销已发布的版本？

A: PyPI 不允许删除已发布的版本，但可以标记为"隐藏"或发布新版本修复问题。

### Q: 可以发布预发布版本吗？

A: 可以，使用版本后缀如 `0.1.0a1`（alpha）、`0.1.0b1`（beta）、`0.1.0rc1`（release candidate）。

## 📚 参考资源

- [PyPI 官方文档](https://packaging.python.org/en/latest/)
- [Python 打包指南](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Twine 文档](https://twine.readthedocs.io/)

