# 即梦图片生成 MCP 服务器

这是一个基于 Model Context Protocol (MCP) 的服务器，提供即梦AI图片生成功能。专为网站开发中的图片设计和占位填充场景而设计。

## 功能特性

- 🎨 **AI图片生成**: 支持通过文字描述生成高质量图片
- 🔧 **多模型支持**: 支持6种不同的即梦模型 (jimeng-3.0, jimeng-2.1等)
- ⚙️ **灵活配置**: 可自定义图片尺寸、精细度等参数
- 🚀 **MCP兼容**: 可与所有支持MCP的AI客户端集成
- 📝 **智能提示**: 内置提示词优化建议和最佳实践
- 🔄 **批量生成**: 每次调用返回4张不同的图片供选择

## 安装要求

- Python 3.8+
- 即梦API访问权限和session_id

## 快速开始

### 1. 安装依赖

```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用uv (推荐)
uv pip install -r requirements.txt
```

### 2. 配置环境

复制 `env_example.txt` 为 `.env` 并填入你的配置：

```bash
cp env_example.txt .env
```

编辑 `.env` 文件，至少需要设置：
```
JIMENG_SESSION_ID=your_actual_session_id_here
```

### 3. 启动服务器

```bash
# 方式一：直接运行
python jimeng_image_server.py

# 方式二：使用启动脚本
python run_server.py

# 方式三：使用uvx (推荐)
uvx jimeng_image_server.py
```

## 可用工具

### 1. generate_images - 生成AI图片

为网站开发生成AI图片，适用于图片设计和占位填充。

**参数：**
- `prompt` (必填): 图片描述提示词
- `model` (可选): 模型选择，默认 "jimeng-3.0"
- `negative_prompt` (可选): 反向提示词，默认为空
- `width` (可选): 图片宽度，默认1024
- `height` (可选): 图片高度，默认1024  
- `sample_strength` (可选): 精细度(0-1)，默认0.5

**注意：** `session_id` 通过环境变量 `JIMENG_SESSION_ID` 自动获取，无需在调用时传入。

**示例调用：**
```python
# 基础用法
result = await generate_images(
    prompt="现代简约的办公室内景，明亮的自然光"
)

# 高级用法
result = await generate_images(
    prompt="电商产品展示图，白色背景，专业摄影",
    model="jimeng-3.0",
    negative_prompt="模糊的,低质量,文字,水印",
    width=1920,
    height=1080,
    sample_strength=0.7
)
```

### 2. list_available_models - 列出可用模型

查看所有支持的即梦图片生成模型及其特点。

### 3. get_generation_tips - 获取优化建议

获取提示词编写技巧、参数调优建议和最佳实践。

## 提示词编写技巧

### 网站开发常用场景

1. **产品展示图**
   ```
   "电商产品展示图，白色背景，专业摄影，高分辨率"
   ```

2. **网站横幅**
   ```
   "现代科技感横幅背景，渐变色彩，商务风格"
   ```

3. **用户头像占位符**
   ```
   "简约的用户头像图标，扁平化设计，圆形"
   ```

4. **博客文章配图**
   ```
   "科技主题的插画风格配图，现代感，蓝色调"
   ```

### 提示词优化要点

- ✅ 使用具体、描述性的词汇
- ✅ 指定风格：插画、摄影、卡通等
- ✅ 包含情感和氛围描述
- ✅ 对商业用途指定"高分辨率"、"专业"等
- ❌ 避免版权相关内容
- ❌ 避免过于抽象的描述

## MCP客户端配置

### Claude Desktop配置

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "jimeng-image": {
      "command": "python",
      "args": ["/path/to/mcp_server/jimeng_image_server.py"],
      "env": {
        "JIMENG_SESSION_ID": "your_session_id_here"
      }
    }
  }
}
```

### 其他MCP客户端

参考各客户端的MCP服务器配置文档，使用以下启动命令：
```bash
python /path/to/jimeng_image_server.py
```

## API接口说明

本服务器调用的即梦图片生成API详情：

- **接口地址**: `POST http://localhost:8001/v1/images/generations`
- **认证方式**: Bearer token (session_id)
- **响应时间**: 30秒到1分钟
- **返回数量**: 每次4张图片

## 常见问题

### Q: 如何获取session_id？
A: session_id需要从即梦API服务获取，通常通过登录或认证流程获得。

### Q: 图片生成失败怎么办？
A: 检查以下几点：
1. session_id是否正确且未过期
2. 即梦API服务是否正常运行 (http://localhost:8001)
3. 网络连接是否稳定
4. 提示词是否符合内容政策

### Q: 可以同时生成多个不同尺寸的图片吗？
A: 每次调用只能指定一个尺寸，但会返回4张相同尺寸的不同图片。如需不同尺寸，请分别调用。

### Q: 图片链接的有效期是多久？
A: 图片链接可能有时效性，建议及时下载保存满意的图片。

## 技术支持

- MCP协议文档: https://modelcontextprotocol.io/
- FastMCP文档: https://github.com/jlowin/fastmcp
- 即梦API相关问题请联系即梦服务提供方

## 许可证

MIT License
