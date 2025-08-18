# 即梦图片生成 MCP 服务器 - 项目总结

## 📁 项目文件结构

```
mcp_server/
├── jimeng_image_server.py      # 主MCP服务器实现
├── requirements.txt            # Python依赖列表
├── pyproject.toml             # 项目配置文件
├── run_server.py              # 服务器启动脚本
├── env_example.txt            # 环境变量配置示例
├── example_usage.py           # 功能测试示例代码
├── claude_desktop_config.json # Claude Desktop配置示例
├── README.md                  # 详细使用说明
└── SUMMARY.md                 # 本文件：项目总结
```

## 🚀 快速启动

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**
   ```bash
   cp env_example.txt .env
   # 编辑 .env 文件，设置 JIMENG_SESSION_ID
   ```

3. **启动服务器**
   ```bash
   python jimeng_image_server.py
   ```

## 🛠️ MCP 工具功能

### 1. `generate_images` - 核心图片生成工具
- **用途**: 为网站开发生成AI图片，支持图片设计和占位填充
- **输入**: 提示词、模型选择、尺寸等参数 (会话ID通过环境变量自动获取)
- **输出**: 4张不同的图片链接，JSON格式返回
- **特点**: 30秒-1分钟生成时间，支持6种模型

### 2. `list_available_models` - 模型信息查询
- **用途**: 查看所有支持的即梦模型及其特点
- **输出**: 模型列表、默认模型、使用建议

### 3. `get_generation_tips` - 优化建议获取  
- **用途**: 获取提示词编写技巧和参数调优建议
- **内容**: 网站开发场景、提示词技巧、参数优化、工作流建议

## 💡 核心特性

✅ **智能参数验证**: 自动验证模型、尺寸、精细度等参数  
✅ **环境变量支持**: 可通过.env文件配置所有参数  
✅ **错误处理**: 完善的异常处理和用户友好的错误信息  
✅ **超时控制**: 可配置的API请求超时时间  
✅ **批量生成**: 每次返回4张不同图片供选择  
✅ **MCP标准**: 完全兼容MCP协议，可与所有MCP客户端集成  

## 🎯 使用场景

- **网站开发**: 横幅背景、产品展示图、用户头像占位符
- **内容创作**: 博客文章配图、社交媒体素材
- **原型设计**: 快速生成占位图片、设计参考
- **电商应用**: 产品展示图、广告素材

## 🔧 技术栈

- **MCP框架**: FastMCP (基于Model Context Protocol)
- **HTTP客户端**: httpx (异步HTTP请求)
- **配置管理**: python-dotenv (环境变量)
- **API集成**: 即梦图片生成API

## 📝 配置要点

1. **必须配置**: `JIMENG_SESSION_ID` - 即梦API认证 (通过环境变量设置)
2. **可选配置**: API地址、默认模型、图片尺寸、超时时间
3. **MCP客户端**: 在配置中指定服务器路径和环境变量
4. **简化调用**: session_id无需在API调用时传入，统一通过环境变量管理

## 🚨 注意事项

- 确保即梦API服务正常运行 (默认: http://localhost:8001)
- session_id需要有效且未过期
- 图片生成需要30秒-1分钟，请耐心等待
- 生成的图片链接可能有时效性，建议及时保存

## 🔗 相关链接

- [MCP协议官网](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [即梦API文档](../jimeng-free-api/README.md)
