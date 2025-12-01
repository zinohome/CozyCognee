# Cognee 支持的文件格式（完整版）

本文档列出了 Cognee **理论上**支持的所有文件格式（需要完整安装所有 extras），以及哪些格式可以正常进行 `cognify` 和 `memify` 操作。

**注意**：如果您使用的是 CozyCognee 的 Docker 镜像，请查看 [CozyCognee 实际支持的文件格式](./SUPPORTED_FILE_FORMATS_COZYCOGNEE.md) 了解当前配置下实际可用的格式。

## 📋 概述

Cognee 使用加载器（Loader）系统来处理不同类型的文件。所有能够成功通过 `add()` 函数上传的文件，都可以进行 `cognify` 和 `memify` 操作，因为这两个操作处理的是已经提取的文本内容。

## ✅ 支持的文件格式

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

**处理方式**：直接读取文本内容

**cognify/memify 支持**：✅ 完全支持

---

### 2. PDF 文件（PyPdfLoader - 核心加载器）

**扩展名**：
- `.pdf` - PDF 文档

**MIME 类型**：
- `application/pdf`

**处理方式**：使用 `pypdf` 库逐页提取文本内容

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 如果 PDF 是扫描版（图片），可能无法提取文本
- 复杂布局的 PDF 可能提取效果不佳

---

### 3. 高级 PDF 处理（AdvancedPdfLoader - 可选加载器）

**扩展名**：
- `.pdf` - PDF 文档

**MIME 类型**：
- `application/pdf`

**处理方式**：使用 `unstructured` 库进行布局感知的文本提取，支持表格和图片识别

**依赖**：需要安装 `unstructured` 库（通过 `--extra scraping` 安装）

**cognify/memify 支持**：✅ 完全支持

**优势**：
- 更好的表格提取
- 支持 OCR（如果配置）
- 布局感知的文本提取

**回退机制**：如果处理失败，会自动回退到 PyPdfLoader

---

### 4. Office 文档（UnstructuredLoader - 可选加载器）

**扩展名**：
- `.docx`, `.doc` - Word 文档
- `.odt` - OpenDocument 文本
- `.xlsx`, `.xls` - Excel 表格
- `.ods` - OpenDocument 表格
- `.pptx`, `.ppt` - PowerPoint 演示文稿
- `.odp` - OpenDocument 演示文稿
- `.rtf` - 富文本格式
- `.html`, `.htm` - HTML 文件
- `.eml`, `.msg` - 电子邮件文件
- `.epub` - 电子书

**MIME 类型**：
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (docx)
- `application/msword` (doc)
- `application/vnd.oasis.opendocument.text` (odt)
- `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (xlsx)
- `application/vnd.ms-excel` (xls)
- `application/vnd.oasis.opendocument.spreadsheet` (ods)
- `application/vnd.openxmlformats-officedocument.presentationml.presentation` (pptx)
- `application/vnd.ms-powerpoint` (ppt)
- `application/vnd.oasis.opendocument.presentation` (odp)
- `application/rtf` (rtf)
- `text/html` (html)
- `message/rfc822` (eml)
- `application/epub+zip` (epub)

**处理方式**：使用 `unstructured` 库的 `auto-partition` 功能提取文本

**依赖**：需要安装 `unstructured` 库（通过 `--extra scraping` 安装）

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 表格内容会被提取为文本
- 图片和图表可能无法提取内容（除非使用 OCR）

---

### 5. 图片文件（ImageLoader - 核心加载器）

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

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 需要配置支持视觉模型的 LLM（如 OpenAI GPT-4 Vision）
- 处理速度可能较慢
- 图片中的文字会被提取为文本

---

### 6. 音频文件（AudioLoader - 核心加载器）

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

**cognify/memify 支持**：✅ 完全支持

**注意事项**：
- 需要配置支持音频转录的 LLM API
- 处理时间取决于音频长度
- 转录质量取决于音频质量和语言

---

### 7. HTML/网页文件（BeautifulSoupLoader - 可选加载器）

**扩展名**：
- `.html`, `.htm` - HTML 文件

**MIME 类型**：
- `text/html`
- `text/plain` (如果内容被识别为 HTML)

**处理方式**：使用 BeautifulSoup 解析 HTML，提取结构化内容（标题、段落、表格等）

**依赖**：需要安装 `beautifulsoup4` 库（通过 `--extra scraping` 安装）

**cognify/memify 支持**：✅ 完全支持

**特性**：
- 支持自定义 CSS 选择器提取规则
- 自动提取标题、段落、列表、表格等
- 支持 XPath 选择器（需要 lxml）

---

## 🔄 加载器优先级

当多个加载器可以处理同一文件类型时，按以下优先级选择：

1. `text_loader` - 文本加载器
2. `pypdf_loader` - PDF 加载器
3. `image_loader` - 图片加载器
4. `audio_loader` - 音频加载器
5. `unstructured_loader` - 结构化文档加载器
6. `advanced_pdf_loader` - 高级 PDF 加载器

## 📝 代码文件支持

**注意**：代码文件（如 `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, `.rb` 等）目前**没有专门的加载器**。

**处理方式**：
- 根据 `guess_file_type` 的逻辑，如果文件类型无法确定，会被当作 `text/plain` 处理
- 代码文件通常会被识别为文本文件，使用 `TextLoader` 处理
- 如果无法自动识别，可以重命名为 `.txt` 扩展名

**cognify/memify 支持**：✅ 支持（作为文本文件处理）

**建议**：
- 代码文件可以直接上传，通常会被自动识别为文本文件
- 如果无法识别，可以重命名为 `.txt` 扩展名
- 代码文件会被完整读取，包括注释和代码结构

## 🌐 URL 支持

除了文件上传，Cognee 还支持：

- **HTTP/HTTPS URL**：网页链接
- **GitHub 仓库 URL**：自动克隆和处理
- **S3 路径**：`s3://bucket-name/path/to/file.pdf`

**处理方式**：
- URL 内容会被下载并处理
- 网页内容可以使用 BeautifulSoup 或 Tavily API 提取

**cognify/memify 支持**：✅ 完全支持

## ✅ cognify 和 memify 支持总结

**重要**：所有能够成功通过 `add()` 函数上传的文件，都可以进行 `cognify` 和 `memify` 操作。

### 原因

1. **add() 阶段**：文件被加载器处理，提取文本内容并存储
2. **cognify() 阶段**：处理已存储的文本内容，构建知识图谱
3. **memify() 阶段**：处理已存储的文本内容，创建记忆结构

因此，只要文件能够被加载器成功处理并提取文本，就可以进行后续的 `cognify` 和 `memify` 操作。

### 完全支持的文件格式

✅ **文本文件**：`.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`, `.log`
✅ **PDF 文件**：`.pdf`
✅ **Office 文档**：`.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt`, `.rtf`, `.odt`, `.ods`, `.odp`
✅ **图片文件**：`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.tif`, `.tiff`, `.bmp`, `.ico`, `.heic`, `.avif` 等
✅ **音频文件**：`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.amr`, `.aiff`, `.mid`
✅ **HTML 文件**：`.html`, `.htm`
✅ **电子书**：`.epub`
✅ **电子邮件**：`.eml`, `.msg`
✅ **代码文件**：作为文本文件处理（`.py`, `.js`, `.ts`, `.java`, `.cpp` 等）

### 可能有限制的格式

⚠️ **扫描版 PDF**：如果 PDF 是纯图片（扫描版），可能无法提取文本
⚠️ **加密 PDF**：加密的 PDF 文件无法处理
⚠️ **损坏的文件**：损坏的文件可能无法处理

## 🔧 依赖要求

### 核心加载器（始终可用）
- `text_loader` - 无需额外依赖
- `pypdf_loader` - 需要 `pypdf`（通常已包含）
- `image_loader` - 需要支持视觉模型的 LLM API
- `audio_loader` - 需要支持音频转录的 LLM API

### 可选加载器（需要额外安装）
- `unstructured_loader` - 需要 `unstructured` 库（通过 `--extra scraping` 安装）
- `advanced_pdf_loader` - 需要 `unstructured` 库（通过 `--extra scraping` 安装）
- `beautiful_soup_loader` - 需要 `beautifulsoup4` 库（通过 `--extra scraping` 安装）

## 📚 相关文档

- [API 使用指南](./README.md)
- [部署文档](../deployment/README.md)
- [开发文档](../development/README.md)

