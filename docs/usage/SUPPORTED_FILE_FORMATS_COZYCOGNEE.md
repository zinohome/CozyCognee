# CozyCognee 实际支持的文件格式

本文档基于我们当前的 Dockerfile 配置，列出了 **实际可用** 的文件格式。

## 📋 我们的 Dockerfile 配置

根据 `deployment/docker/cognee/Dockerfile`，我们安装了以下 extras：

```dockerfile
--extra debug --extra api --extra postgres --extra neo4j --extra llama-index \
--extra ollama --extra mistral --extra groq --extra anthropic --extra scraping
```

**关键点**：
- ✅ 安装了 `scraping` extra（包含 beautifulsoup4, playwright, lxml）
- ❌ **没有安装** `docs` extra（包含 unstructured 库）

## ✅ 实际支持的文件格式

### 1. 文本文件（TextLoader - 核心加载器，始终可用）

**扩展名**：
- `.txt` - 纯文本文件
- `.md` - Markdown 文件
- `.csv` - CSV 表格文件
- `.json` - JSON 数据文件
- `.xml` - XML 文件
- `.yaml`, `.yml` - YAML 配置文件
- `.log` - 日志文件

**MIME 类型**：
- `text/plain`
- `text/markdown`
- `text/csv`
- `application/json`
- `text/xml`, `application/xml`
- `text/yaml`, `application/yaml`

**依赖**：无需额外依赖（核心功能）

**cognify/memify 支持**：✅ 完全支持

---

### 2. PDF 文件（PyPdfLoader - 核心加载器）

**扩展名**：
- `.pdf` - PDF 文档

**MIME 类型**：
- `application/pdf`

**处理方式**：使用 `pypdf` 库逐页提取文本内容

**依赖**：`pypdf`（核心依赖，已安装）

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 如果 PDF 是扫描版（图片），可能无法提取文本
- 复杂布局的 PDF 可能提取效果不佳
- **不支持** AdvancedPdfLoader（需要 unstructured 库）

---

### 3. 图片文件（ImageLoader - 核心加载器）

**扩展名**：
- `.png`, `.jpg`, `.jpeg` - 常见图片格式
- `.gif`, `.webp` - 网络图片格式
- `.tif`, `.tiff` - TIFF 图片
- `.bmp` - 位图
- `.ico` - 图标
- `.heic` - HEIC 图片（iOS）
- `.avif` - AVIF 图片
- `.dwg`, `.xcf`, `.jpx`, `.apng`, `.cr2`, `.jxr`, `.psd` - 其他图片格式

**MIME 类型**：
- `image/png`, `image/jpeg`, `image/gif`, `image/webp`
- `image/tiff`, `image/bmp`
- `image/vnd.microsoft.icon` (ico)
- `image/heic`, `image/avif`
- 等等

**处理方式**：使用 LLM 的视觉模型（如 GPT-4 Vision）进行 OCR 和图片内容描述

**依赖**：需要配置支持视觉模型的 LLM（如 OpenAI GPT-4 Vision）

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 需要配置支持视觉模型的 LLM（如 OpenAI GPT-4 Vision）
- 处理速度可能较慢
- 图片中的文字会被提取为文本

---

### 4. 音频文件（AudioLoader - 核心加载器）

**扩展名**：
- `.mp3` - MP3 音频
- `.wav` - WAV 音频
- `.m4a` - M4A 音频
- `.ogg` - OGG 音频
- `.flac` - FLAC 无损音频
- `.aac` - AAC 音频
- `.amr` - AMR 音频
- `.aiff` - AIFF 音频
- `.mid` - MIDI 文件

**MIME 类型**：
- `audio/mpeg` (mp3)
- `audio/wav`, `audio/x-wav` (wav)
- `audio/mp4` (m4a)
- `audio/ogg` (ogg)
- `audio/flac` (flac)
- `audio/aac` (aac)
- `audio/amr` (amr)
- `audio/aiff` (aiff)
- `audio/midi` (mid)

**处理方式**：使用 LLM 的音频转录功能（如 Whisper）将音频转换为文本

**依赖**：需要配置支持音频转录的 LLM API

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 需要配置支持音频转录的 LLM API
- 处理时间取决于音频长度
- 转录质量取决于音频质量和语言

---

### 5. HTML/网页文件（BeautifulSoupLoader - 通过 scraping extra 提供）

**扩展名**：
- `.html`, `.htm` - HTML 文件

**MIME 类型**：
- `text/html`
- `text/plain` (如果内容被识别为 HTML)

**处理方式**：使用 BeautifulSoup 解析 HTML，提取结构化内容（标题、段落、表格等）

**依赖**：`beautifulsoup4`, `lxml`（通过 `--extra scraping` 安装）

**cognify/memify 支持**：✅ 完全支持

**特性**：
- 支持自定义 CSS 选择器提取规则
- 自动提取标题、段落、列表、表格等
- 支持 XPath 选择器（需要 lxml，已安装）
- 支持 Playwright 渲染 JavaScript 页面（已安装 playwright）

---

### 6. 代码文件（作为文本处理）

**扩展名**：
- `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, `.rb`, `.php`, `.swift`, `.kt` 等

**处理方式**：
- 根据 `guess_file_type` 的逻辑，如果文件类型无法确定，会被当作 `text/plain` 处理
- 代码文件通常会被识别为文本文件，使用 `TextLoader` 处理

**cognify/memify 支持**：✅ 支持（作为文本文件处理）

**注意事项**：
- 代码文件会被完整读取，包括注释和代码结构
- 如果无法自动识别，可以重命名为 `.txt` 扩展名

---

## ❌ 不支持的文件格式（需要 docs extra）

以下文件格式需要 `unstructured` 库，但我们的 Dockerfile **没有安装** `docs` extra，因此**不支持**：

### Office 文档
- ❌ `.docx`, `.doc` - Word 文档
- ❌ `.xlsx`, `.xls` - Excel 表格
- ❌ `.pptx`, `.ppt` - PowerPoint 演示文稿
- ❌ `.rtf` - 富文本格式
- ❌ `.odt`, `.ods`, `.odp` - OpenDocument 格式

### 其他文档
- ❌ `.epub` - 电子书
- ❌ `.eml`, `.msg` - 电子邮件文件

### 高级 PDF 处理
- ❌ AdvancedPdfLoader（需要 unstructured 库）
  - 注意：基础 PDF 处理（PyPdfLoader）仍然可用

---

## 📊 支持情况总结

| 文件类型 | 扩展名示例 | 加载器 | 状态 | cognify/memify |
|---------|-----------|--------|------|----------------|
| **文本文件** | `.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`, `.log` | TextLoader | ✅ 支持 | ✅ |
| **PDF** | `.pdf` | PyPdfLoader | ✅ 支持 | ✅ |
| **图片** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.tif`, `.bmp` 等 | ImageLoader | ✅ 支持 | ✅ |
| **音频** | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` 等 | AudioLoader | ✅ 支持 | ✅ |
| **HTML** | `.html`, `.htm` | BeautifulSoupLoader | ✅ 支持 | ✅ |
| **代码文件** | `.py`, `.js`, `.ts`, `.java`, `.cpp` 等 | TextLoader | ✅ 支持 | ✅ |
| **Office 文档** | `.docx`, `.xlsx`, `.pptx` | UnstructuredLoader | ❌ 不支持 | ❌ |
| **电子书** | `.epub` | UnstructuredLoader | ❌ 不支持 | ❌ |
| **电子邮件** | `.eml`, `.msg` | UnstructuredLoader | ❌ 不支持 | ❌ |

---

## 🔧 如何启用 Office 文档支持

如果需要支持 Office 文档（`.docx`, `.xlsx`, `.pptx` 等），需要修改 Dockerfile：

### 方法 1：添加 docs extra（推荐，但会增加镜像大小）

修改 `deployment/docker/cognee/Dockerfile`：

```dockerfile
# 添加 docs extra
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra debug --extra api --extra postgres --extra neo4j \
    --extra llama-index --extra ollama --extra mistral --extra groq \
    --extra anthropic --extra scraping --extra docs \
    --frozen --no-install-project --no-dev --no-editable
```

**注意**：`docs` extra 包含 `unstructured` 库，会**大幅增加镜像大小**（约 3-5GB），因为 unstructured 包含大量依赖。

### 方法 2：只安装 unstructured（不推荐）

可以尝试只安装 unstructured，但可能缺少某些依赖。

---

## 🌐 URL 支持

除了文件上传，Cognee 还支持：

- **HTTP/HTTPS URL**：网页链接
  - 使用 BeautifulSoupLoader 或 Tavily API 提取内容
  - 支持 Playwright 渲染 JavaScript 页面（已安装）
- **GitHub 仓库 URL**：自动克隆和处理
- **S3 路径**：`s3://bucket-name/path/to/file.pdf`

**处理方式**：
- URL 内容会被下载并处理
- 网页内容可以使用 BeautifulSoup 或 Tavily API 提取

**cognify/memify 支持**：✅ 完全支持

---

## ✅ cognify 和 memify 支持总结

**重要**：所有能够成功通过 `add()` 函数上传的文件，都可以进行 `cognify` 和 `memify` 操作。

### 原因

1. **add() 阶段**：文件被加载器处理，提取文本内容并存储
2. **cognify() 阶段**：处理已存储的文本内容，构建知识图谱
3. **memify() 阶段**：处理已存储的文本内容，创建记忆结构

因此，只要文件能够被加载器成功处理并提取文本，就可以进行后续的 `cognify` 和 `memify` 操作。

### 当前配置下完全支持的文件格式

✅ **文本文件**：`.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`, `.log`
✅ **PDF 文件**：`.pdf`（基础处理，不支持高级功能）
✅ **图片文件**：`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.tif`, `.tiff`, `.bmp`, `.ico`, `.heic`, `.avif` 等
✅ **音频文件**：`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.amr`, `.aiff`, `.mid`
✅ **HTML 文件**：`.html`, `.htm`
✅ **代码文件**：作为文本文件处理（`.py`, `.js`, `.ts`, `.java`, `.cpp` 等）

### 不支持的文件格式

❌ **Office 文档**：`.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`, `.rtf`, `.odt`, `.ods`, `.odp`
❌ **电子书**：`.epub`
❌ **电子邮件**：`.eml`, `.msg`
❌ **高级 PDF 处理**：表格提取、OCR 等功能

---

## 📚 相关文档

- [完整支持的文件格式列表](./SUPPORTED_FILE_FORMATS.md) - 包含所有可能的文件格式（需要完整安装）
- [API 使用指南](./README.md)
- [部署文档](../deployment/README.md)

