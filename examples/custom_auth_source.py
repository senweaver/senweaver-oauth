"""
自定义认证源示例
"""

from senweaver_oauth import AuthConfig, AuthRequest, AuthRequestBuilder
from senweaver_oauth.enums.auth_source import AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


# 创建自定义认证源
class CustomAuthSource:
    """
    自定义认证源
    """
    # 自定义平台类型
    CUSTOM = AuthSource(
        name="custom",
        authorize_url="https://custom.example.com/oauth/authorize",
        access_token_url="https://custom.example.com/oauth/token",
        user_info_url="https://custom.example.com/api/user",
        refresh_token_url="https://custom.example.com/oauth/refresh_token",
        scope_delimiter=" "
    )


# 实现自定义认证源
class AuthCustomSource(BaseAuthSource):
    """
    自定义认证源实现
    """
    
    def __init__(self, config):
        """
        初始化
        
        Args:
            config: 认证配置
        """
        super().__init__(config, CustomAuthSource.CUSTOM)
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        Args:
            callback: 回调参数
            
        Returns:
            访问令牌
        """
        if not callback.code:
            return AuthTokenResponse.failure("授权码不能为空")
            
        params = {
            'grant_type': 'authorization_code',
            'code': callback.code,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'redirect_uri': self.config.redirect_uri
        }
        
        try:
            response = self.http_client.post(self.source.access_token_url, data=params)
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '获取访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type'),
                expires_in=response.get('expires_in', 7200),
                refresh_token=response.get('refresh_token'),
                scope=response.get('scope'),
                code=callback.code
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"获取访问令牌异常: {str(e)}")
        
    def get_user_info(self, token: AuthToken) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息
        """
        try:
            headers = {'Authorization': f"Bearer {token.access_token}"}
            response = self.http_client.get(self.source.user_info_url, headers=headers)
            
            if 'error' in response:
                return AuthUserResponse.failure(response.get('error_description', '获取用户信息失败'))
                
            user = AuthUser(
                uuid=str(response.get('id')),
                username=response.get('username'),
                nickname=response.get('nickname'),
                avatar=response.get('avatar'),
                blog=response.get('blog'),
                company=response.get('company'),
                location=response.get('location'),
                email=response.get('email'),
                remark=response.get('bio'),
                gender=response.get('gender'),
                source=self.source.name,
                token={
                    'access_token': token.access_token,
                    'refresh_token': token.refresh_token,
                    'expires_in': token.expires_in
                },
                raw_user_info=response
            )
            
            return AuthUserResponse.success(user)
            
        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}")
            
    def refresh_token(self, refresh_token: str) -> AuthTokenResponse:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌
        """
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        try:
            response = self.http_client.post(self.source.refresh_token_url, data=params)
            
            if 'error' in response:
                return AuthTokenResponse.failure(
                    message=response.get('error_description', '刷新访问令牌失败')
                )
                
            token = AuthToken(
                access_token=response.get('access_token'),
                token_type=response.get('token_type'),
                expires_in=response.get('expires_in', 7200),
                refresh_token=response.get('refresh_token'),
                scope=response.get('scope')
            )
            
            return AuthTokenResponse.success(token)
            
        except Exception as e:
            return AuthTokenResponse.error(f"刷新访问令牌异常: {str(e)}")


def main():
    """
    示例主函数
    """
    # 方式一：直接使用自定义认证源
    auth_config = AuthConfig(
        client_id="custom_client_id",
        client_secret="custom_client_secret",
        redirect_uri="http://localhost:8000/auth/custom/callback"
    )
    
    auth_request1 = AuthRequest.build(AuthCustomSource, auth_config)
    
    auth_url1 = auth_request1.authorize()
    print("方式一 - 授权URL:", auth_url1)
    
    # 方式二：使用AuthRequestBuilder
    auth_request2 = AuthRequestBuilder.builder() \
        .extend_source([CustomAuthSource]) \
        .source("custom") \
        .auth_config(auth_config) \
        .build()
    
    auth_url2 = auth_request2.authorize()
    print("方式二 - 授权URL:", auth_url2)


if __name__ == "__main__":
    main() 