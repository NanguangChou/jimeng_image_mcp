#!/usr/bin/env python3
"""
即梦图片生成 MCP 服务器使用示例

这个文件展示了如何在Python代码中测试MCP服务器的功能。
注意：这不是MCP客户端，只是用于测试服务器功能的示例代码。
"""

import asyncio
import json
import os
from jimeng_image_server import generate_images, list_available_models, get_generation_tips

async def test_image_generation():
    """测试图片生成功能"""
    print("🎨 测试图片生成功能...")
    
    # 检查环境变量是否设置
    session_id = os.getenv("JIMENG_SESSION_ID")
    
    if session_id is None:
        print("⚠️  警告: 环境变量JIMENG_SESSION_ID未设置，请在.env文件中设置真实的JIMENG_SESSION_ID")
        print("💡 测试将继续运行，但可能会收到错误消息")
    else:
        print(f"✅ 已从环境变量获取session_id: {session_id[:10]}...")
    
    # 测试基础图片生成 (session_id自动从环境变量获取)
    print("\n📝 生成网站横幅图片...")
    result = await generate_images(
        prompt="现代科技感网站横幅背景，蓝色渐变，商务风格，高分辨率",
        width=1920,
        height=1080
    )
    
    print("生成结果:")
    print(result)
    print("-" * 50)
    
    # 测试产品展示图生成 (session_id自动从环境变量获取)
    print("\n📱 生成产品展示图...")
    result = await generate_images(
        prompt="电商产品展示图，白色背景，专业摄影，商业用途",
        model="jimeng-3.0",
        negative_prompt="模糊的,低质量,文字,水印",
        width=1024,
        height=1024,
        sample_strength=0.7
    )
    
    print("生成结果:")
    print(result)
    print("-" * 50)

async def test_model_listing():
    """测试模型列表功能"""
    print("\n🔧 获取可用模型列表...")
    result = await list_available_models()
    print(result)
    print("-" * 50)

async def test_generation_tips():
    """测试获取生成技巧功能"""
    print("\n💡 获取图片生成优化建议...")
    result = await get_generation_tips()
    print(result)
    print("-" * 50)

async def main():
    """主测试函数"""
    print("🚀 即梦图片生成 MCP 服务器功能测试")
    print("=" * 60)
    
    try:
        # 测试各个功能
        await test_model_listing()
        await test_generation_tips()
        await test_image_generation()
        
        print("\n✅ 所有测试完成！")
        print("\n📋 下一步：")
        print("1. 确保已正确设置 .env 文件中的 JIMENG_SESSION_ID")
        print("2. 启动MCP服务器: python jimeng_image_server.py")
        print("3. 在支持MCP的客户端中配置并使用此服务器")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查即梦API服务是否正常运行 (http://localhost:8001)")
        print("2. 验证session_id是否正确")
        print("3. 确保网络连接正常")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
