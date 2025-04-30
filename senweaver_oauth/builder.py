"""
认证请求构建器
"""
from typing import Optional, List, Callable, Type

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_source import AuthSource, AuthDefaultSource
from senweaver_oauth.request import AuthRequest
from senweaver_oauth.source.base import BaseAuthSource


class AuthRequestBuilder:
    """
    认证请求构建器
    支持链式调用和动态配置
    """
    
    def __init__(self):
        """
        初始化
        """
        self._source: Optional[str] = None
        self._auth_config: Optional[AuthConfig] = None
        self._auth_config_function: Optional[Callable[[str], AuthConfig]] = None
        self._extend_sources: List[Type[AuthSource]] = []
        
    @classmethod
    def builder(cls) -> 'AuthRequestBuilder':
        """
        创建构建器实例
        
        Returns:
            构建器实例
        """
        return cls()
        
    def source(self, source: str) -> 'AuthRequestBuilder':
        """
        设置认证源
        
        Args:
            source: 认证源名称
            
        Returns:
            构建器实例
        """
        self._source = source
        return self
        
    def auth_config(self, config: AuthConfig) -> 'AuthRequestBuilder':
        """
        设置认证配置
        
        Args:
            config: 认证配置
            
        Returns:
            构建器实例
        """
        self._auth_config = config
        return self
        
    def auth_config_function(self, function: Callable[[str], AuthConfig]) -> 'AuthRequestBuilder':
        """
        设置认证配置函数
        
        Args:
            function: 认证配置函数，接收认证源名称，返回认证配置
            
        Returns:
            构建器实例
        """
        self._auth_config_function = function
        return self
        
    def extend_source(self, sources: List[Type[AuthSource]]) -> 'AuthRequestBuilder':
        """
        扩展认证源
        
        Args:
            sources: 认证源类型列表
            
        Returns:
            构建器实例
        """
        self._extend_sources = sources
        return self
        
    def build(self) -> AuthRequest:
        """
        构建认证请求
        
        Returns:
            认证请求实例
        """
        if not self._source:
            raise ValueError("认证源不能为空")
            
        # 获取认证配置
        config = self._get_auth_config()
        
        # 获取认证源
        source = self._get_auth_source()
        if not source:
            raise ValueError(f"未找到认证源: {self._source}")
            
        # 获取认证源类
        auth_source_class = self._get_auth_source_class()
        if not auth_source_class:
            raise ValueError(f"未找到认证源类: {self._source}")
            
        # 创建认证源实例
        auth_source = auth_source_class(config)
        
        # 创建认证请求
        return AuthRequest(auth_source)
        
    def _get_auth_config(self) -> AuthConfig:
        """
        获取认证配置
        
        Returns:
            认证配置
        """
        if self._auth_config:
            return self._auth_config
            
        if self._auth_config_function:
            return self._auth_config_function(self._source)
            
        raise ValueError("认证配置不能为空")
        
    def _get_auth_source(self) -> Optional[AuthSource]:
        """
        获取认证源
        
        Returns:
            认证源，如果不存在则返回None
        """
        # 从默认认证源中获取
        source = AuthDefaultSource.get_source(self._source)
        if source:
            return source
            
        # 从扩展认证源中获取
        for source_class in self._extend_sources:
            if hasattr(source_class, self._source.upper()):
                return getattr(source_class, self._source.upper())
                
        return None
        
    def _get_auth_source_class(self) -> Optional[Type[BaseAuthSource]]:
        """
        获取认证源类
        
        Returns:
            认证源类，如果不存在则返回None
        """
        # 根据认证源名称获取对应的认证源类
        source_name = self._source.lower()
        
        # 标准方式：将下划线转为驼峰式，首字母大写
        parts = source_name.split('_')
        class_name = ''.join(p.title() for p in parts)
        
        # 尝试直接从source目录导入模块
        try:
            import importlib
            import sys
            
            # 打印调试信息
            print(f"尝试导入模块: senweaver_oauth.source.{source_name}")
            print(f"期望的类名: Auth{class_name}Source")
            
            # 列出所有已加载的模块
            loaded_modules = [m for m in sys.modules.keys() if m.startswith('senweaver_oauth.source')]
            print(f"已加载的source模块: {loaded_modules}")
            
            # 尝试导入模块
            module = importlib.import_module(f"senweaver_oauth.source.{source_name}")
            
            # 列出模块中的所有类
            module_attrs = dir(module)
            source_classes = [attr for attr in module_attrs if attr.startswith('Auth') and attr.endswith('Source')]
            print(f"模块中的认证源类: {source_classes}")
            
            # 获取指定的类
            source_class = getattr(module, f"Auth{class_name}Source")
            print(f"找到认证源类: {source_class.__name__}")
            
            return source_class
        except Exception as e:
            import traceback
            print(f"导入认证源类失败: {e}")
            print(traceback.format_exc())
            
            # 尝试第二种方式导入
            try:
                module = importlib.import_module(f"senweaver_oauth.source.auth_{source_name}_source")
                return getattr(module, f"Auth{class_name}Source")
            except Exception as e2:
                print(f"第二种方式导入失败: {e2}")
                return None 