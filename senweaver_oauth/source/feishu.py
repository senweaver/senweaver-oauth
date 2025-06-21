"""
飞书认证源
"""
import uuid
from typing import Dict, Optional

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource
from senweaver_oauth.enums.auth_gender import AuthGender


class AuthFeishuSource(BaseAuthSource):
    """
    飞书认证源
    实现飞书登录功能
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
            source=source or AuthDefaultSource.FEISHU
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
            "app_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
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
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{url}?{query}"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        # 飞书API需要使用JSON格式请求
        json_data = {
            "app_id": self.config.client_id,
            "app_secret": self.config.client_secret,
            "grant_type": "authorization_code",
            "code": callback.code
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = self.http_client.post(
            self.source.access_token_url, 
            json=json_data,
            headers=headers
        )
                    
        data = response
        
        # 飞书API返回格式：{"code": 0, "msg": "success", "data": {...}}
        if data.get("code") != 0:
            return AuthTokenResponse(
                code=data.get("code", 400),
                message=f"获取访问令牌失败: {data.get('msg', '')}"
            )
            
        token_data = data.get("data", {})
        
        token = AuthToken(
            access_token=token_data.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_data.get("expires_in", 0),
            refresh_token=token_data.get("refresh_token", ""),
            id_token=token_data.get("id_token", ""),
            open_id=token_data.get("open_id", ""),
            union_id=token_data.get("union_id", ""),
            tenant_key=token_data.get("tenant_key", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="获取访问令牌成功",
            data=token
        )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        response = self.http_client.get(self.source.user_info_url, headers=headers)
                    
        data = response
        
        # 飞书API返回格式：{"code": 0, "msg": "success", "data": {...}}
        if data.get("code") != 0:
            return AuthUserResponse(
                code=data.get("code", 400),
                message=f"获取用户信息失败: {data.get('msg', '')}"
            )
            
        user_data = data.get("data", {})
        
        # 构建用户信息
        name = user_data.get("name", "")
        avatar_url = user_data.get("avatar_url", "")
        email = user_data.get("email", "")
        mobile = user_data.get("mobile", "")
        
        user = AuthUser(
            uuid=f"{self.source.name}_{token.open_id}",
            username=name,
            nickname=name,
            avatar=avatar_url,
            gender=self._get_gender(user_data.get("gender", 0)),
            email=email,
            mobile=mobile,
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
        if not self.source.refresh_token_url or not token.refresh_token:
            return AuthTokenResponse(
                code=400,
                message="不支持刷新访问令牌"
            )
            
        # 飞书API需要使用JSON格式请求
        json_data = {
            "app_id": self.config.client_id,
            "app_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = self.http_client.post(
            self.source.refresh_token_url, 
            json=json_data,
            headers=headers
        )
                    
        data = response
        
        # 飞书API返回格式：{"code": 0, "msg": "success", "data": {...}}
        if data.get("code") != 0:
            return AuthTokenResponse(
                code=data.get("code", 400),
                message=f"刷新访问令牌失败: {data.get('msg', '')}"
            )
            
        token_data = data.get("data", {})
        
        new_token = AuthToken(
            access_token=token_data.get("access_token", ""),
            token_type="Bearer",
            expires_in=token_data.get("expires_in", 0),
            refresh_token=token_data.get("refresh_token", ""),
            open_id=token.open_id,
            union_id=token.union_id,
            tenant_key=token.tenant_key
        )
        
        return AuthTokenResponse(
            code=200,
            message="刷新访问令牌成功",
            data=new_token
        )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        飞书不提供标准的撤销令牌接口
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # 飞书不支持标准的撤销令牌接口
        return False 

    def _get_gender(self, gender: int) -> AuthGender:
        """
        转换性别编码
        
        飞书API性别：0表示未知，1表示男性，2表示女性
        
        Args:
            gender: 性别代码
            
        Returns:
            性别枚举
        """
        if gender == 1:
            return AuthGender.MALE
        elif gender == 2:
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 