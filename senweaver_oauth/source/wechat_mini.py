"""
微信小程序认证源
"""

from typing import Any,Dict,Optional
from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthSource, AuthDefaultSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthWechatMiniSource(BaseAuthSource):
    """
    微信小程序认证源
    实现微信小程序登录功能
    
    小程序登录流程与常规OAuth流程不同：
    1. 小程序端调用 wx.login() 获取 code
    2. 服务端使用 code 换取 session_key 和 openid
    3. 小程序端调用 wx.getUserInfo() 获取加密的用户信息
    4. 服务端使用 session_key 解密用户信息
    5. 服务端使用解密后的用户信息生成用户信息对象
    6. 返回用户信息对象给前端
    
    注意：
    1. 小程序端调用 wx.login() 获取 code 时，需要将 code 发送到服务端进行换取 session_key 和 openid
    2. 小程序端调用 wx.getUserInfo() 获取加密的用户信息时，需要将 session_key 发送到服务端进行解密
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
            source=source or AuthDefaultSource.WECHAT_MINI
        )
        self.js_code2session_url = "https://api.weixin.qq.com/sns/jscode2session"
    
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌 - 实现抽象方法
        
        对于微信小程序，我们使用code换取session_key和openid
        
        Args:
            callback: 回调参数，包含code
            
        Returns:
            包含session_key和openid的响应
        """
        # 直接调用已有的code_to_session方法
        return self.code_to_session(callback.code)
    
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息 - 实现抽象方法
        
        对于微信小程序，需要客户端传递加密数据和iv
        可以通过kwargs参数传递encrypted_data和iv
        
        Args:
            token: 包含session_key的令牌
            **kwargs: 额外参数，支持encrypted_data和iv
            
        Returns:
            用户信息响应
        """
        # 从kwargs中获取加密数据和iv
        encrypted_data = kwargs.get('encrypted_data')
        iv = kwargs.get('iv')
        
        # 如果提供了加密数据和iv，则解密并返回用户信息
        if encrypted_data and iv:
            return self.decrypt_user_info(token, encrypted_data, iv)
        
        return AuthUserResponse.failure("需要提供encrypted_data和iv参数才能获取微信小程序用户信息")

    def login(self, callback: Dict[str, Any], **kwargs) -> AuthUserResponse:
        """
        微信小程序一键登录（整合code和用户信息）
        
        将微信小程序登录和获取用户信息两步操作合并为一步，简化前端调用流程
        1. 小程序端同时获取code和加密的用户信息
        2. 前端一次性提交所有数据
        3. 后端完成登录和用户信息解密
        """
        code = callback.get("code")
        encrypted_data = callback.get('encrypted_data')
        iv = callback.get('iv')
        if not code or not encrypted_data or not iv:
           return AuthUserResponse.failure("缺少参数")
        # 步骤1: 使用code换取session_key和openid
        token_response = self.code_to_session(code)
        if token_response.code != 200:
            return AuthUserResponse(
                code=token_response.code,
                status=token_response.status,
                message=token_response.message
            )
        token = token_response.data
        return self.decrypt_user_info(token, encrypted_data, iv)        
        
    def code_to_session(self, code: str) -> AuthTokenResponse:
        """
        使用code换取session_key和openid
        
        Args:
            code: 小程序登录时获取的code
            
        Returns:
            包含session_key和openid的响应
        """
        # 参数校验
        if not code:
            return AuthTokenResponse(
                code=400,
                message="登录凭证code不能为空"
            )
            
        # 准备请求参数
        params = {
            "appid": self.config.client_id,
            "secret": self.config.client_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        # 发送请求
        response = self.http_client.get(
            self.js_code2session_url, 
            params=params
        )
                    
        response_json = response
        
        # 微信返回结果特殊处理
        if "errcode" in response_json and response_json.get("errcode") != 0:
            return AuthTokenResponse(
                code=response_json.get("errcode", 400),
                message=response_json.get("errmsg", "获取session_key失败")
            )
            
        # 构建令牌对象
        token = AuthToken(
            access_token=response_json.get("session_key", ""),  # 使用session_key作为access_token
            token_type="Bearer",
            expires_in=7200,  # 默认过期时间，小程序session_key有效期由微信官方控制
            open_id=response_json.get("openid", ""),
            union_id=response_json.get("unionid", "")
        )
        
        return AuthTokenResponse(
            code=200,
            message="获取session_key成功",
            data=token
        )
    
    def decrypt_user_info(self, token: AuthToken, encrypted_data: str, iv: str) -> AuthUserResponse:
        """
        解密用户信息
        
        Args:
            token: 包含session_key的令牌
            encrypted_data: 小程序通过wx.getUserInfo获取的加密数据
            iv: 加密算法的初始向量
            
        Returns:
            用户信息响应
        """
        # 参数校验
        if not token or not token.access_token:
            return AuthUserResponse(
                code=400,
                message="session_key不能为空"
            )
            
        if not encrypted_data or not iv:
            return AuthUserResponse(
                code=400,
                message="加密数据或初始向量不能为空"
            )
            
        try:
            # 解密用户信息
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            import base64
            import json
            
            # Base64解码
            session_key = base64.b64decode(token.access_token)
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            
            # 初始化AES解密器
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            # 解密数据
            decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 去除PKCS#7填充
            padding = decrypted[-1]
            if padding < 1 or padding > 32:
                return AuthUserResponse(
                    code=400,
                    message="解密数据错误"
                )
            
            decrypted = decrypted[:-padding]
            
            # 将解密后的JSON转换为字典
            user_data = json.loads(decrypted)
            
            # 验证数据的有效性
            if user_data.get("watermark", {}).get("appid") != self.config.client_id:
                return AuthUserResponse(
                    code=400,
                    message="用户数据不合法，appid不匹配"
                )
                
            # 构建用户信息
            user = AuthUser(
                uuid=f"wechat_mini_{token.open_id}",
                username=user_data.get("nickName", ""),
                nickname=user_data.get("nickName", ""),
                avatar=user_data.get("avatarUrl", ""),
                gender=self._get_gender(user_data.get("gender", 0)),
                location=f"{user_data.get('country', '')} {user_data.get('province', '')} {user_data.get('city', '')}".strip(),
                token=token,
                source=self.source.name,
                raw_user_info=user_data
            )
            
            return AuthUserResponse(
                code=200,
                message="获取用户信息成功",
                data=user
            )
            
        except Exception as e:
            return AuthUserResponse(
                code=500,
                message=f"解密用户信息失败: {str(e)}"
            )
    
    def _get_gender(self, gender_code: int) -> AuthGender:
        """
        转换性别编码
        
        Args:
            gender_code: 性别编码（0:未知, 1:男, 2:女）
            
        Returns:
            性别枚举
        """
        if gender_code == 1:
            return AuthGender.MALE
        elif gender_code == 2:
            return AuthGender.FEMALE
        else:
            return AuthGender.UNKNOWN 
        
    def refresh_token(self, refresh_token: str) -> AuthTokenResponse:
        """
        刷新访问令牌（微信小程序不支持）
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            刷新结果
        """
        return AuthTokenResponse(
            code=400,
            message="微信小程序不支持刷新访问令牌"
        )
        
    def revoke_token(self, access_token: str) -> bool:
        """
        撤销访问令牌（微信小程序不支持）
        
        Args:
            access_token: 访问令牌
            
        Returns:
            撤销结果
        """
        return False 