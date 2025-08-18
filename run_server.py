#!/usr/bin/env python3
"""
即梦图片生成 MCP 服务器启动脚本

使用方法:
    python run_server.py
    
或者使用uvx (推荐):
    uvx jimeng_image_server.py
"""

import asyncio
import sys
from jimeng_image_server import mcp

def main():
    """启动MCP服务器的主函数"""
    try:
        # 运行FastMCP服务器
        mcp.run()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


