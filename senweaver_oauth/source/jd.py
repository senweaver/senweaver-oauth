"""
京东认证源
"""
import uuid
import json
import time
import hashlib
from typing import Dict, Optional
from urllib.parse import urlencode

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_scope import AuthScope
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthJdSource(BaseAuthSource):
    """
    京东认证源
    实现京东登录功能
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.JD
        )
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        获取授权参数
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权参数
        """
        params = {
            "app_key": self.config.client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "scope": self.get_scopes(),
            "state": state or str(uuid.uuid4())
        }
        return params
        
    def build_authorize_url(self, params: Dict[str, str]) -> str:
        """
        构建授权URL
        
        Args:
            params: 授权参数
            
        Returns:
            授权URL
        """
        url = self.source.authorize_url
        query = urlencode(params)
        return f"{url}?{query}"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        params = {
            "app_key": self.config.client_id,
            "app_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "code": callback.code
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = self.http_client.post(
            self.source.access_token_url,
            data=params,
            headers=headers
        )
        
            
        data = response
        
        if not data.get("access_token"):
            return AuthTokenResponse(
                code=400,
                message=f"获取访问令牌失败: {data.get('error_description', '')}"
            )
            
        token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            open_id=data.get("uid", ""),
            time=data.get("time", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        京东API比较特殊，获取用户信息需要使用routerjson接口
        需要构建特定的请求参数，并使用应用密钥签名
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 京东API请求参数
        timestamp = str(int(time.time() * 1000))
        
        # API调用方法参数
        method_params = {
            "method": "jingdong.user.getUserInfoByOpenId",
            "access_token": token.access_token,
            "app_key": self.config.client_id,
            "timestamp": timestamp,
            "360buy_param_json": json.dumps({"openId": token.open_id})
        }
        
        # 计算签名，京东API使用特定的签名算法
        method_params["sign"] = self._sign(method_params)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = self.http_client.post(
            self.source.user_info_url,
            data=method_params,
            headers=headers
        )
                    
        data = response
        
        # 京东API响应格式比较复杂，需要解析多层嵌套的JSON
        response_data = data.get("jingdong_user_getUserInfoByOpenId_response", {})
        
        if "error_response" in response_data:
            error = response_data["error_response"]
            return AuthUserResponse(
                code=error.get("code", 400),
                message=error.get("zh_desc", "获取用户信息失败")
            )
            
        user_data = response_data.get("result", {}).get("data", {})
        user_info = user_data.get("userInfo", {})
        
        nickname = user_info.get("nickName", "")
        avatar = user_info.get("imageUrl", "")
        
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=nickname,
            nickname=nickname,
            avatar=avatar,
            gender=AuthGender.UNKNOWN,  # 京东API不提供性别
            email="",  # 京东API不提供邮箱
            token=token,
            source=self.source.name,
            raw_user_info=user_data
        )
        
        return AuthUserResponse(
            code=200,
            message="获取用户信息成功",
            data=user
        )
        
    def refresh_token(self, token: AuthToken) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            刷新后的访问令牌响应
        """
        if not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="不支持刷新访问令牌"
            )
            
        params = {
            "app_key": self.config.client_id,
            "app_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = self.http_client.post(
            self.source.refresh_token_url,
            data=params,
            headers=headers
        )
            
        data = response
        
        if not data.get("access_token"):
            return AuthTokenResponse(
                code=400,
                message=f"刷新访问令牌失败: {data.get('error_description', '')}"
            )
            
        new_token = AuthToken(
            access_token=data.get("access_token", ""),
            token_type="Bearer",
            expires_in=data.get("expires_in", 0),
            refresh_token=data.get("refresh_token", token.refresh_token),
            open_id=token.open_id,
            time=data.get("time", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="刷新访问令牌成功",
            data=new_token
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # 京东不支持标准方式撤销令牌
        return False
        
    def _sign(self, params: Dict[str, str]) -> str:
        """
        计算签名
        
        京东API使用特定的签名算法，将请求参数按照参数名ASCII码从小到大排序，
        然后拼接成字符串，并在字符串前后加上应用密钥，最后使用MD5加密得到签名
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 移除sign参数（如果存在）
        params_to_sign = {k: v for k, v in params.items() if k != "sign"}
        
        # 按照参数名ASCII码从小到大排序
        sorted_params = sorted(params_to_sign.items(), key=lambda x: x[0])
        
        # 拼接成字符串
        sign_str = self.config.client_secret
        for k, v in sorted_params:
            sign_str += f"{k}{v}"
        sign_str += self.config.client_secret
        
        # MD5加密
        md5 = hashlib.md5()
        md5.update(sign_str.encode("utf-8"))
        return md5.hexdigest().upper() 