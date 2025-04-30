"""
HTTP客户端接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HttpClient(ABC):
    """
    HTTP客户端接口
    """
    
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass
        
    @abstractmethod
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
        pass 