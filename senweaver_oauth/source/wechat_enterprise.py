"""
企业微信认证源
"""

from typing import Optional, Dict, Any

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthWechatEnterpriseSource(BaseAuthSource):
    """
    企业微信认证源
    """
    
    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化
        
        Args:
            config: 认证配置
            source: 认证源，默认为企业微信
        """
        super().__init__(
            config=config,
            source=source or AuthDefaultSource.WECHAT_ENTERPRISE
        )
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        获取授权参数，重写父类方法，添加企业微信特有参数
        
        Args:
            state: 自定义state参数
            
        Returns:
            授权参数
        """
        params = super().get_authorize_params(state)
        
        # 添加企业微信特有参数
        params['appid'] = self.config.client_id
        # 移除标准OAuth2参数
        if 'client_id' in params:
            del params['client_id']
        
        return params
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌，企业微信与标准OAuth2流程不同
        
        Args:
            callback: 回调参数
            
        Returns:
            访问令牌
        """
        if not callback.code:
            return AuthTokenResponse.failure("授权码不能为空")
            
        # 获取访问令牌
        params = {
            'corpid': self.config.client_id,
            'corpsecret': self.config.client_secret
        }
        
        try:
            response = self.http_client.get(
                self.source.access_token_url, 
                params=params
            )
            
            if response.get('errcode') != 0:
                return AuthTokenResponse.failure(
                    message=response.get('errmsg', '获取访问令牌失败')
                )
                
            # 构建token
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type='Bearer',
                refresh_token=None,  # 企业微信不支持刷新令牌
                expires_in=response.get('expires_in', 7200),  # 默认2小时
                scope=None,
                code=callback.code
            )
            
            # 保存额外信息，用于获取用户信息
            token.ext_data = {
                'code': callback.code
            }
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"获取访问令牌异常: {str(e)}")
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息
        """
        try:
            # 获取code
            code = None
            if hasattr(token, 'ext_data') and token.ext_data:
                code = token.ext_data.get('code')
                
            if not code:
                return AuthUserResponse.failure("无法获取用户授权码")
                
            # 企业微信需要先获取用户身份
            params = {
                'access_token': token.access_token,
                'code': code
            }
            
            response = self.http_client.get(
                self.source.user_info_url, 
                params=params
            )
            
            if response.get('errcode') != 0:
                return AuthUserResponse.failure(response.get('errmsg', '获取用户信息失败'))
            
            # 获取用户ID
            user_id = response.get('UserId')
            
            # 获取用户详细信息
            user_detail_url = "https://qyapi.weixin.qq.com/cgi-bin/user/get"
            detail_params = {
                'access_token': token.access_token,
                'userid': user_id
            }
            
            detail_response = self.http_client.get(
                user_detail_url, 
                params=detail_params
            )
            
            if detail_response.get('errcode') != 0:
                return AuthUserResponse.failure(detail_response.get('errmsg', '获取用户详细信息失败'))
            
            # 解析性别
            gender = AuthGender.UNKNOWN
            if detail_response.get('gender') == 1:
                gender = AuthGender.MALE
            elif detail_response.get('gender') == 2:
                gender = AuthGender.FEMALE
                
            user = AuthUser(
                uuid=user_id,
                username=detail_response.get('userid', ''),
                nickname=detail_response.get('name'),
                avatar=detail_response.get('avatar'),
                email=detail_response.get('email'),
                mobile=detail_response.get('mobile'),
                gender=gender,
                source=self.source.name,
                token=token,
                raw_user_info=detail_response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}") 