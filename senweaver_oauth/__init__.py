"""
SenWeaver-OAuth - 强大、灵活且易用的OAuth授权集成组件
"""

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.request import AuthRequest
from senweaver_oauth.builder import AuthRequestBuilder
from senweaver_oauth.model import AuthCallback

__version__ = "0.1.2"
__author__ = "senweaver"

__all__ = ["AuthConfig", "AuthRequest", "AuthRequestBuilder", "AuthCallback"]
