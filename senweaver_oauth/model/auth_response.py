"""
响应信息模型
"""

from dataclasses import dataclass
from typing import Optional, TypeVar, Generic

from senweaver_oauth.enums.response_status import ResponseStatus
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser

T = TypeVar('T')


@dataclass
class AuthResponse(Generic[T]):
    """
    响应信息
    """
    code: int  # 状态码
    data: Optional[T] = None  # 响应数据
    status: ResponseStatus = ResponseStatus.SUCCESS  # 响应状态
    message: Optional[str] = None  # 响应消息
    
    @staticmethod
    def success(data: Optional[T] = None, message: Optional[str] = None) -> 'AuthResponse[T]':
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            成功响应对象
        """
        return AuthResponse(
            code=200,
            data=data,
            status=ResponseStatus.SUCCESS,
            message=message or 'Success'
        )
        
    @staticmethod
    def error(message: str, code: int = 500) -> 'AuthResponse[T]':
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 错误码
            
        Returns:
            错误响应对象
        """
        return AuthResponse(
            code=code,
            status=ResponseStatus.ERROR,
            message=message
        )
        
    @staticmethod
    def failure(message: str, code: int = 400) -> 'AuthResponse[T]':
        """
        失败响应
        
        Args:
            message: 失败消息
            code: 失败码
            
        Returns:
            失败响应对象
        """
        return AuthResponse(
            code=code,
            status=ResponseStatus.FAILURE,
            message=message
        )
        
    @staticmethod
    def unauthorized(message: str = 'Unauthorized') -> 'AuthResponse[T]':
        """
        未授权响应
        
        Args:
            message: 未授权消息
            
        Returns:
            未授权响应对象
        """
        return AuthResponse(
            code=401,
            status=ResponseStatus.UNAUTHORIZED,
            message=message
        )
        
    @staticmethod
    def not_implemented(message: str = 'Not Implemented') -> 'AuthResponse[T]':
        """
        未实现响应
        
        Args:
            message: 未实现消息
            
        Returns:
            未实现响应对象
        """
        return AuthResponse(
            code=501,
            status=ResponseStatus.NOT_IMPLEMENTED,
            message=message
        )
        
    @staticmethod
    def timeout(message: str = 'Timeout') -> 'AuthResponse[T]':
        """
        超时响应
        
        Args:
            message: 超时消息
            
        Returns:
            超时响应对象
        """
        return AuthResponse(
            code=408,
            status=ResponseStatus.TIMEOUT,
            message=message
        )


# 定义常用的响应类型
AuthTokenResponse = AuthResponse[AuthToken]
AuthUserResponse = AuthResponse[AuthUser] 