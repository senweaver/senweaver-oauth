"""
枚举类型模块
"""

from senweaver_oauth.enums.response_status import ResponseStatus
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_source import AuthSource, AuthDefaultSource
from senweaver_oauth.enums.auth_gender import AuthGender

__all__ = [
    'ResponseStatus',
    'AuthScope',
    'AuthSource',
    'AuthDefaultSource',
    'AuthGender'
] 