#!/usr/bin/env python3
"""
腾讯云COS SDK 最新特性示例

展示如何使用腾讯云COS Python SDK的最新功能和最佳实践
"""

import asyncio
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from qcloud_cos import CosConfig, CosS3Client
    from qcloud_cos.cos_exception import CosServiceError, CosClientError
    from qcloud_cos.cos_auth import Auth
except ImportError:
    print("请先安装腾讯云COS SDK: pip install cos-python-sdk-v5")
    sys.exit(1)

class TencentCOSManager:
    """腾讯云COS管理器 - 使用最新SDK特性"""
    
    def __init__(self):
        self.secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
        self.region = os.getenv("TENCENT_COS_REGION", "ap-guangzhou")
        self.bucket = os.getenv("TENCENT_COS_BUCKET", "jimeng-images")
        self.domain = os.getenv("TENCENT_COS_DOMAIN", "")
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("腾讯云COS配置不完整")
        
        # 使用最新的配置方式
        self.config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme='https',  # 明确指定HTTPS
            Timeout=60,      # 设置超时时间
            MaxRetry=3       # 设置重试次数
        )
        
        self.client = CosS3Client(self.config)
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            # 使用head_bucket测试连接
            response = self.client.head_bucket(Bucket=self.bucket)
            print(f"✅ 成功连接到存储桶: {self.bucket}")
            return True
        except CosServiceError as e:
            print(f"❌ 服务错误: {e.get_error_code()} - {e.get_error_msg()}")
            return False
        except CosClientError as e:
            print(f"❌ 客户端错误: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 连接异常: {str(e)}")
            return False
    
    async def upload_file_async(self, file_path: str, key: str, 
                               content_type: Optional[str] = None) -> Optional[str]:
        """异步上传文件"""
        try:
            # 读取文件
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # 确定Content-Type
            if not content_type:
                content_type = self._get_content_type(file_path)
            
            # 上传文件
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=file_data,
                Key=key,
                ContentType=content_type,
                StorageClass='STANDARD',  # 明确指定存储类型
                ACL='public-read'  # 设置访问权限（可选）
            )
            
            # 验证上传结果
            if response and response.get('ETag'):
                url = self._build_url(key)
                print(f"✅ 文件上传成功: {url}")
                return url
            else:
                print("❌ 上传结果验证失败")
                return None
                
        except Exception as e:
            print(f"❌ 文件上传失败: {str(e)}")
            return None
    
    async def upload_from_url_async(self, url: str, key: str, 
                                   content_type: Optional[str] = None) -> Optional[str]:
        """从URL异步上传文件"""
        import httpx
        
        try:
            # 异步下载文件
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                file_data = response.content
            
            # 确定Content-Type
            if not content_type:
                content_type = response.headers.get('content-type', 'application/octet-stream')
            
            # 上传到COS
            cos_response = self.client.put_object(
                Bucket=self.bucket,
                Body=file_data,
                Key=key,
                ContentType=content_type,
                StorageClass='STANDARD'
            )
            
            if cos_response and cos_response.get('ETag'):
                url = self._build_url(key)
                print(f"✅ URL文件上传成功: {url}")
                return url
            else:
                print("❌ 上传结果验证失败")
                return None
                
        except Exception as e:
            print(f"❌ URL文件上传失败: {str(e)}")
            return None
    
    def list_objects(self, prefix: str = "", max_keys: int = 100) -> list:
        """列出对象"""
        try:
            response = self.client.list_objects(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            
            return objects
            
        except Exception as e:
            print(f"❌ 列出对象失败: {str(e)}")
            return []
    
    def delete_object(self, key: str) -> bool:
        """删除对象"""
        try:
            response = self.client.delete_object(Bucket=self.bucket, Key=key)
            print(f"✅ 对象删除成功: {key}")
            return True
        except Exception as e:
            print(f"❌ 对象删除失败: {str(e)}")
            return False
    
    def get_object_url(self, key: str, expires: int = 3600) -> str:
        """获取对象预签名URL"""
        try:
            url = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket,
                Key=key,
                Expired=expires
            )
            return url
        except Exception as e:
            print(f"❌ 获取预签名URL失败: {str(e)}")
            return ""
    
    def _get_content_type(self, file_path: str) -> str:
        """根据文件扩展名获取Content-Type"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def _build_url(self, key: str) -> str:
        """构建对象URL"""
        if self.domain:
            return f"https://{self.domain}/{key}"
        else:
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{key}"

async def main():
    """主函数 - 演示各种功能"""
    print("腾讯云COS SDK 最新特性演示")
    print("=" * 50)
    
    try:
        # 初始化COS管理器
        cos_manager = TencentCOSManager()
        
        # 测试连接
        if not cos_manager.test_connection():
            print("❌ 连接测试失败")
            return
        
        # 列出现有对象
        print("\n📋 列出现有对象:")
        objects = cos_manager.list_objects(prefix="jimeng/", max_keys=10)
        for obj in objects:
            print(f"  - {obj['key']} ({obj['size']} bytes)")
        
        # 演示从URL上传
        print("\n📤 演示从URL上传:")
        test_url = "https://via.placeholder.com/300x200/0066cc/ffffff?text=Demo"
        test_key = "jimeng/demo_image.png"
        
        uploaded_url = await cos_manager.upload_from_url_async(test_url, test_key)
        if uploaded_url:
            print(f"上传成功: {uploaded_url}")
            
            # 获取预签名URL
            presigned_url = cos_manager.get_object_url(test_key, expires=3600)
            print(f"预签名URL: {presigned_url}")
        
        # 演示删除对象
        print("\n🗑️  演示删除对象:")
        cos_manager.delete_object(test_key)
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())


