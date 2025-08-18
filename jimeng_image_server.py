#!/usr/bin/env python3
"""
即梦图片生成 MCP 服务器

这个MCP服务器提供了调用即梦图片生成API的功能，用于网站开发中的图片设计和占位填充。
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化FastMCP服务器
mcp = FastMCP("jimeng-image-generator")

# 常量配置 (可通过环境变量覆盖)
JIMENG_API_BASE = os.getenv("JIMENG_API_BASE", "http://localhost:8001")
JIMENG_SESSION_ID = os.getenv("JIMENG_SESSION_ID")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "jimeng-3.0")
DEFAULT_WIDTH = int(os.getenv("DEFAULT_WIDTH", "1024"))
DEFAULT_HEIGHT = int(os.getenv("DEFAULT_HEIGHT", "1024"))
DEFAULT_SAMPLE_STRENGTH = float(os.getenv("DEFAULT_SAMPLE_STRENGTH", "0.5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120000"))

# 可用模型列表
AVAILABLE_MODELS = [
    "jimeng-3.0",
    "jimeng-2.1", 
    "jimeng-2.0-pro",
    "jimeng-2.0",
    "jimeng-1.4",
    "jimeng-xl-pro"
]

async def make_jimeng_request(url: str, data: Dict[str, Any], session_id: str) -> Dict[str, Any] | None:
    """向即梦API发送请求"""
    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"error": "请求超时，图片生成可能需要更长时间"}
        except httpx.HTTPStatusError as e:
            return {"error": f"API请求失败: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"请求发生错误: {str(e)}"}

@mcp.tool()
async def generate_images(
    prompt: str,
    model: str = DEFAULT_MODEL,
    negative_prompt: str = "",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    sample_strength: float = DEFAULT_SAMPLE_STRENGTH
) -> str:
    """
    生成AI图片，适用于网站开发中的图片设计和占位填充
    
    Args:
        prompt: 图片描述提示词，必填。例如："少女祈祷中..."、"现代办公室背景"、"产品展示图"等
        model: 模型选择，可选值：jimeng-3.0(默认)、jimeng-2.1、jimeng-2.0-pro、jimeng-2.0、jimeng-1.4、jimeng-xl-pro
        negative_prompt: 反向提示词，描述不想要的元素，默认为空
        width: 图片宽度，默认1024像素
        height: 图片高度，默认1024像素  
        sample_strength: 精细度，取值范围0-1，默认0.5
    
    Returns:
        包含4个图片链接的JSON字符串，每次调用返回4个不同的图片供选择
    """
    
    # 从环境变量获取session_id
    if JIMENG_SESSION_ID is None:
        return json.dumps({
            "error": "环境变量JIMENG_SESSION_ID未设置",
            "help": "请在.env文件中设置JIMENG_SESSION_ID环境变量"
        }, ensure_ascii=False, indent=2)
    
    # 验证模型参数
    if model not in AVAILABLE_MODELS:
        return json.dumps({
            "error": f"不支持的模型: {model}",
            "available_models": AVAILABLE_MODELS
        }, ensure_ascii=False, indent=2)
    
    # 验证参数范围
    if not (0 <= sample_strength <= 1):
        return json.dumps({
            "error": "sample_strength 必须在 0-1 范围内"
        }, ensure_ascii=False, indent=2)
    
    if width <= 0 or height <= 0:
        return json.dumps({
            "error": "图片尺寸必须大于0"
        }, ensure_ascii=False, indent=2)
    
    # 构建请求数据
    request_data = {
        "model": model,
        "prompt": prompt,
        "negativePrompt": negative_prompt,
        "width": width,
        "height": height,
        "sample_strength": sample_strength
    }
    
    # 调用即梦API
    url = f"{JIMENG_API_BASE}/v1/images/generations"
    result = await make_jimeng_request(url, request_data, JIMENG_SESSION_ID)
    
    if result is None:
        return json.dumps({
            "error": "无法连接到即梦API服务"
        }, ensure_ascii=False, indent=2)
    
    if "error" in result:
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # 格式化响应，提取关键信息
    if "data" in result and len(result["data"]) > 0:
        formatted_result = {
            "success": True,
            "generated_at": result.get("created", "未知时间"),
            "model_used": model,
            "prompt_used": prompt,
            "image_count": len(result["data"]),
            "images": []
        }
        
        for i, img_data in enumerate(result["data"], 1):
            formatted_result["images"].append({
                "index": i,
                "url": img_data.get("url", ""),
                "description": f"基于提示词'{prompt}'生成的图片 #{i}"
            })
        
        return json.dumps(formatted_result, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "error": "API返回了空的图片数据",
            "raw_response": result
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def list_available_models() -> str:
    """
    列出所有可用的即梦图片生成模型
    
    Returns:
        可用模型列表的JSON字符串，包含模型名称和描述
    """
    models_info = {
        "available_models": [
            {
                "name": "jimeng-3.0",
                "description": "最新版本，图片质量最高，推荐使用",
                "is_default": True
            },
            {
                "name": "jimeng-2.1", 
                "description": "稳定版本，平衡质量与速度"
            },
            {
                "name": "jimeng-2.0-pro",
                "description": "专业版本，适合高质量需求"
            },
            {
                "name": "jimeng-2.0",
                "description": "标准版本"
            },
            {
                "name": "jimeng-1.4",
                "description": "较早版本，兼容性好"
            },
            {
                "name": "jimeng-xl-pro",
                "description": "XL专业版本，支持更大尺寸"
            }
        ],
        "default_model": DEFAULT_MODEL,
        "usage_note": "选择模型时请考虑图片质量需求和生成时间的平衡"
    }
    
    return json.dumps(models_info, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_generation_tips() -> str:
    """
    获取图片生成的最佳实践建议
    
    Returns:
        包含提示词编写技巧和参数调优建议的字符串
    """
    tips = {
        "prompt_tips": [
            "使用具体、描述性的词汇，如'现代简约的办公室内景'而不是'办公室'",
            "可以指定风格，如'插画风格'、'摄影风格'、'卡通风格'等",
            "包含情感和氛围描述，如'温馨的'、'专业的'、'活力四射的'",
            "对于网站使用，可以指定'高分辨率'、'商业用途'、'专业摄影'等关键词"
        ],
        "negative_prompt_tips": [
            "在negative_prompt中描述不想要的元素",
            "常用排除项：'模糊的'、'低质量'、'扭曲的'、'不完整的'",
            "对于商业用途，可以排除：'水印'、'版权标识'、'文字'等"
        ],
        "parameter_optimization": {
            "sample_strength": {
                "0.3-0.5": "适合需要更多创意和变化的图片",
                "0.5-0.7": "平衡创意和准确度，大多数情况的最佳选择", 
                "0.7-1.0": "更严格遵循提示词，适合需要精确控制的场景"
            },
            "size_recommendations": {
                "web_headers": "1920x1080 或 1600x900",
                "product_images": "1024x1024 (正方形)",
                "thumbnails": "512x512 或 640x640",
                "mobile_banners": "1080x1920 (竖屏)"
            }
        },
        "workflow_suggestions": [
            "每次生成会返回4张图片，建议先看所有选项再决定",
            "如果需要微调，可以调整prompt或参数重新生成",
            "生成时间约30秒到1分钟，请耐心等待",
            "建议保存满意的图片URL，因为链接可能有时效性"
        ]
    }
    
    return json.dumps(tips, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 运行MCP服务器
    mcp.run(transport='stdio')
