"""
基于requests库的HTTP客户端实现
"""
import json
import requests
from typing import Dict, Any, Optional

from senweaver_oauth.http.http_client import HttpClient
from senweaver_oauth.http.http_config import HttpConfig


class RequestsHttpClient(HttpClient):
    """
    基于requests库的HTTP客户端实现
    """
    
    def __init__(self, config: Optional[HttpConfig] = None):
        """
        初始化
        
        Args:
            config: HTTP配置
        """
        self.config = config or HttpConfig()
        
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        GET请求
        
        Args:
            url: 请求URL
            params: 请求参数
            headers: 请求头
            
        Returns:
            响应数据，JSON格式
        """
        merged_headers = self._merge_headers(headers)
        response = requests.get(
            url=url,
            params=params,
            headers=merged_headers,
            timeout=self.config.timeout,
            proxies=self.config.proxy,
            verify=self.config.verify_ssl
        )
        return self._process_response(response)
        
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             params: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        POST请求
        
        Args:
            url: 请求URL
            data: 请求体数据
            params: 请求参数
            headers: 请求头
            
        Returns:
            响应数据，JSON格式
        """
        merged_headers = self._merge_headers(headers)
        response = requests.post(
            url=url,
            json=data,
            params=params,
            headers=merged_headers,
            timeout=self.config.timeout,
            proxies=self.config.proxy,
            verify=self.config.verify_ssl
        )
        return self._process_response(response)
        
    def put(self, url: str, data: Optional[Dict[str, Any]] = None, 
            params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        PUT请求
        
        Args:
            url: 请求URL
            data: 请求体数据
            params: 请求参数
            headers: 请求头
            
        Returns:
            响应数据，JSON格式
        """
        merged_headers = self._merge_headers(headers)
        response = requests.put(
            url=url,
            json=data,
            params=params,
            headers=merged_headers,
            timeout=self.config.timeout,
            proxies=self.config.proxy,
            verify=self.config.verify_ssl
        )
        return self._process_response(response)
        
    def delete(self, url: str, params: Optional[Dict[str, Any]] = None, 
               headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        DELETE请求
        
        Args:
            url: 请求URL
            params: 请求参数
            headers: 请求头
            
        Returns:
            响应数据，JSON格式
        """
        merged_headers = self._merge_headers(headers)
        response = requests.delete(
            url=url,
            params=params,
            headers=merged_headers,
            timeout=self.config.timeout,
            proxies=self.config.proxy,
            verify=self.config.verify_ssl
        )
        return self._process_response(response)
        
    def _merge_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        合并请求头
        
        Args:
            headers: 请求头
            
        Returns:
            合并后的请求头
        """
        merged_headers = self.config.headers.copy()
        if headers:
            merged_headers.update(headers)
        return merged_headers
        
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理响应数据
        
        Args:
            response: 响应对象
            
        Returns:
            处理后的响应数据
        """
        response.raise_for_status()
        
        # 尝试将响应内容解析为JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            # 如果不是JSON格式，则返回文本内容
            return {'content': response.text} 