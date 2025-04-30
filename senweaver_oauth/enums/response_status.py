"""
响应状态枚举
"""
from enum import Enum, auto


class ResponseStatus(Enum):
    """
    OAuth响应状态枚举
    """
    SUCCESS = auto()  # 成功
    FAILURE = auto()  # 失败
    NOT_IMPLEMENTED = auto()  # 未实现
    TIMEOUT = auto()  # 超时
    UNAUTHORIZED = auto()  # 未授权
    ERROR = auto()  # 错误 