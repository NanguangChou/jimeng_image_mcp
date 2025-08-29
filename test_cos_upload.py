#!/usr/bin/env python3
"""
腾讯云COS上传功能测试脚本
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_cos_config():
    """测试腾讯云COS配置"""
    print("=== 腾讯云COS配置测试 ===")
    
    # 检查环境变量
    secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
    region = os.getenv("TENCENT_COS_REGION", "ap-beijing")
    bucket = os.getenv("TENCENT_COS_BUCKET", "jimeng-images")
    domain = os.getenv("TENCENT_COS_DOMAIN", "")
    
    print(f"Secret ID: {'已设置' if secret_id else '未设置'}")
    print(f"Secret Key: {'已设置' if secret_key else '未设置'}")
    print(f"Region: {region}")
    print(f"Bucket: {bucket}")
    print(f"Domain: {domain if domain else '使用默认域名'}")
    
    if not secret_id or not secret_key:
        print("\n❌ 腾讯云COS配置不完整，请检查环境变量")
        return False
    
    # 检查依赖包
    try:
        from qcloud_cos import CosConfig, CosS3Client
        print("\n✅ 腾讯云COS SDK已安装")
    except ImportError:
        print("\n❌ 腾讯云COS SDK未安装，请运行: pip install cos-python-sdk-v5")
        return False
    
    print("\n✅ 腾讯云COS配置检查通过")
    return True

def test_cos_connection():
    """测试腾讯云COS连接"""
    print("\n=== 腾讯云COS连接测试 ===")
    
    try:
        from qcloud_cos import CosConfig, CosS3Client
        
        secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
        secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
        region = os.getenv("TENCENT_COS_REGION", "ap-beijing")
        bucket = os.getenv("TENCENT_COS_BUCKET", "jimeng-images")
        
        # 配置腾讯云COS
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key
        )
        client = CosS3Client(config)
        
        # 测试连接 - 获取存储桶信息
        response = client.head_bucket(Bucket=bucket)
        print(f"✅ 成功连接到存储桶: {bucket}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

async def test_upload_function():
    """测试上传功能"""
    print("\n=== 上传功能测试 ===")
    
    # 导入上传函数
    sys.path.append('.')
    from jimeng_image_server import upload_to_tencent_cos
    
    # 测试图片URL（使用一个公开的测试图片）
    test_image_url = "https://via.placeholder.com/300x200/0066cc/ffffff?text=Test"
    test_prompt = "测试图片"
    
    print(f"测试图片URL: {test_image_url}")
    print(f"测试提示词: {test_prompt}")
    
    try:
        result = await upload_to_tencent_cos(test_image_url, test_prompt)
        if result:
            print(f"✅ 上传成功: {result}")
            return True
        else:
            print("❌ 上传失败")
            return False
    except Exception as e:
        print(f"❌ 上传异常: {str(e)}")
        return False

async def main():
    print("腾讯云COS功能测试")
    print("=" * 50)
    
    # 测试配置
    if not test_cos_config():
        sys.exit(1)
    
    # 测试连接
    if not test_cos_connection():
        print("\n⚠️  连接测试失败，但配置正确。可能是网络问题或权限问题。")
        print("请检查：")
        print("1. 网络连接是否正常")
        print("2. 腾讯云API密钥是否有COS访问权限")
        print("3. 存储桶是否存在且可访问")
        sys.exit(1)
    
    # 测试上传
    if await test_upload_function():
        print("\n🎉 所有测试通过！腾讯云COS功能正常工作。")
    else:
        print("\n⚠️  上传测试失败，请检查网络和权限设置。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
