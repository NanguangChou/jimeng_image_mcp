#!/usr/bin/env python3
"""
腾讯云COS 性能优化版本

使用连接池、并发上传和缓存等优化技术提升性能
"""

import asyncio
import os
import sys
import time
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from qcloud_cos import CosConfig, CosS3Client
    from qcloud_cos.cos_exception import CosServiceError, CosClientError
    import httpx
except ImportError:
    print("请先安装依赖: pip install cos-python-sdk-v5 httpx")
    sys.exit(1)

class OptimizedTencentCOS:
    """性能优化的腾讯云COS客户端"""
    
    def __init__(self, max_workers: int = 4):
        self.secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
        self.region = os.getenv("TENCENT_COS_REGION", "ap-guangzhou")
        self.bucket = os.getenv("TENCENT_COS_BUCKET", "jimeng-images")
        self.domain = os.getenv("TENCENT_COS_DOMAIN", "")
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("腾讯云COS配置不完整")
        
        # 使用连接池的HTTP客户端
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        
        # 线程池用于同步操作
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 初始化COS客户端
        self._init_cos_client()
    
    def _init_cos_client(self):
        """初始化COS客户端"""
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme='https',
            Timeout=60,
            MaxRetry=3
        )
        self.cos_client = CosS3Client(config)
    
    @lru_cache(maxsize=128)
    def _get_content_type(self, file_extension: str) -> str:
        """缓存Content-Type映射"""
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml'
        }
        return content_type_map.get(file_extension.lower(), 'image/jpeg')
    
    async def download_image_batch(self, urls: List[str]) -> List[Optional[bytes]]:
        """批量异步下载图片"""
        async def download_single(url: str) -> Optional[bytes]:
            try:
                response = await self.http_client.get(url)
                response.raise_for_status()
                return response.content
            except Exception as e:
                print(f"下载失败 {url}: {str(e)}")
                return None
        
        # 并发下载
        tasks = [download_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"下载异常: {str(result)}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def upload_to_cos_sync(self, image_data: bytes, key: str, content_type: str) -> Optional[str]:
        """同步上传到COS（在线程池中执行）"""
        try:
            response = self.cos_client.put_object(
                Bucket=self.bucket,
                Body=image_data,
                Key=key,
                ContentType=content_type,
                StorageClass='STANDARD'
            )
            
            if response and response.get('ETag'):
                return self._build_url(key)
            return None
            
        except Exception as e:
            print(f"上传失败 {key}: {str(e)}")
            return None
    
    async def upload_to_cos_async(self, image_data: bytes, key: str, content_type: str) -> Optional[str]:
        """异步上传到COS"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.upload_to_cos_sync, 
            image_data, key, content_type
        )
    
    async def upload_images_batch(self, image_urls: List[str], prompts: List[str]) -> List[Optional[str]]:
        """批量上传图片"""
        if len(image_urls) != len(prompts):
            raise ValueError("图片URL和提示词数量不匹配")
        
        # 批量下载
        print(f"开始下载 {len(image_urls)} 张图片...")
        image_data_list = await self.download_image_batch(image_urls)
        
        # 准备上传任务
        upload_tasks = []
        for i, (image_data, prompt) in enumerate(zip(image_data_list, prompts)):
            if image_data is None:
                upload_tasks.append(None)
                continue
            
            # 生成文件名
            import uuid
            safe_prompt = self._sanitize_filename(prompt)
            unique_id = uuid.uuid4().hex[:8]
            key = f"jimeng/batch/{safe_prompt}_{unique_id}.png"
            
            # 创建上传任务
            task = self.upload_to_cos_async(image_data, key, 'image/png')
            upload_tasks.append(task)
        
        # 并发上传
        print(f"开始上传 {len(upload_tasks)} 张图片...")
        results = await asyncio.gather(*[task for task in upload_tasks if task is not None], 
                                     return_exceptions=True)
        
        # 处理结果
        final_results = []
        task_index = 0
        for task in upload_tasks:
            if task is None:
                final_results.append(None)
            else:
                if isinstance(results[task_index], Exception):
                    print(f"上传异常: {str(results[task_index])}")
                    final_results.append(None)
                else:
                    final_results.append(results[task_index])
                task_index += 1
        
        return final_results
    
    def _sanitize_filename(self, prompt: str, max_length: int = 50) -> str:
        """清理文件名"""
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ')
        safe_prompt = ''.join(c for c in prompt if c in safe_chars)
        
        if len(safe_prompt) > max_length:
            safe_prompt = safe_prompt[:max_length]
        
        safe_prompt = safe_prompt.replace(' ', '_')
        return safe_prompt or "image"
    
    def _build_url(self, key: str) -> str:
        """构建URL"""
        if self.domain:
            return f"https://{self.domain}/{key}"
        else:
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{key}"
    
    async def close(self):
        """关闭资源"""
        await self.http_client.aclose()
        self.executor.shutdown(wait=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.close())

async def performance_test():
    """性能测试"""
    print("腾讯云COS 性能优化测试")
    print("=" * 50)
    
    # 测试数据
    test_urls = [
        "https://via.placeholder.com/300x200/ff0000/ffffff?text=1",
        "https://via.placeholder.com/300x200/00ff00/ffffff?text=2",
        "https://via.placeholder.com/300x200/0000ff/ffffff?text=3",
        "https://via.placeholder.com/300x200/ffff00/000000?text=4",
        "https://via.placeholder.com/300x200/ff00ff/ffffff?text=5"
    ]
    
    test_prompts = [
        "红色测试图片",
        "绿色测试图片", 
        "蓝色测试图片",
        "黄色测试图片",
        "紫色测试图片"
    ]
    
    async with OptimizedTencentCOS(max_workers=4) as cos_client:
        # 测试连接
        try:
            response = cos_client.cos_client.head_bucket(Bucket=cos_client.bucket)
            print("✅ 连接测试成功")
        except Exception as e:
            print(f"❌ 连接测试失败: {str(e)}")
            return
        
        # 性能测试
        print(f"\n🚀 开始批量上传测试 ({len(test_urls)} 张图片)...")
        start_time = time.time()
        
        results = await cos_client.upload_images_batch(test_urls, test_prompts)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 统计结果
        success_count = sum(1 for r in results if r is not None)
        print(f"\n📊 性能测试结果:")
        print(f"  总耗时: {duration:.2f} 秒")
        print(f"  成功上传: {success_count}/{len(test_urls)}")
        print(f"  平均速度: {len(test_urls)/duration:.2f} 张/秒")
        
        # 显示结果
        print(f"\n📋 上传结果:")
        for i, (url, result) in enumerate(zip(test_urls, results)):
            status = "✅" if result else "❌"
            print(f"  {status} 图片 {i+1}: {result or '上传失败'}")

if __name__ == "__main__":
    asyncio.run(performance_test())


