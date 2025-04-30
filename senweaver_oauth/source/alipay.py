"""
支付宝认证源
"""
import uuid
import base64
from datetime import datetime
from typing import Dict, Optional, Any
from urllib.parse import urlencode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_der_private_key

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource
from senweaver_oauth.enums.auth_gender import AuthGender

class AuthAlipaySource(BaseAuthSource):
    """
    支付宝认证源
    实现支付宝登录功能
    
    支付宝授权流程较为特殊，需要对接口请求内容进行签名
    完整实现需要依赖第三方的支付宝SDK
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
            source=source or AuthDefaultSource.ALIPAY
        )
        # 获取私钥
        self.private_key = config.client_secret
        # 获取公钥
        self.public_key = config.public_key        
        # 获取App ID
        self.app_id = config.client_id
        # 签名类型
        self.sign_type = config.extras.get("sign_type", "RSA2")
        
    def get_authorize_params(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        获取授权参数
        
        支付宝授权流程中，需要构建特定的请求参数并进行签名
        
        Args:
            state: 自定义state参数，用于防止CSRF攻击
            
        Returns:
            授权参数
        """
        
        # 公共请求参数
        params = {
            "app_id": self.config.client_id,
            "scope": self.get_scopes(),
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
        query = urlencode(params)
        return f"{url}?{query}"
        
    def get_access_token(self, callback: AuthCallback) -> AuthTokenResponse:
        """
        获取访问令牌
        
        支付宝的接口调用需要构建公共请求参数和业务参数，并对请求内容进行签名
        
        Args:
            callback: 授权回调参数
            
        Returns:
            访问令牌响应
        """
        # 公共请求参数
        params = {
            "app_id": self.app_id,
            "method": "alipay.system.oauth.token",
            "charset": "utf-8",
            "sign_type": self.sign_type,
            "timestamp": self._get_timestamp_str(),
            "grant_type": "authorization_code",
            "code": callback.code
        }
        
        # 计算签名
        if self.private_key:
            sign = self._sign(params)
            params["sign"] = sign
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.get(
                self.source.access_token_url,
                params=params,
                headers=headers
            )
            data = response.get("alipay_system_oauth_token_response", {})
            
            if "error_response" in response:
                error = response["error_response"]
                return AuthTokenResponse(
                    code=error.get("code", 400),
                    message=error.get("msg", "获取访问令牌失败")
                )
                
            token = AuthToken(
                access_token=data.get("access_token", ""),
                token_type="Bearer",
                expires_in=data.get("expires_in", 0),
                refresh_token=data.get("refresh_token", ""),
                open_id=data.get("open_id", "")
            )
            
            return AuthTokenResponse(
                code=200,
                message="获取访问令牌成功",
                data=token
            )
            
        except Exception as e:
            return AuthTokenResponse(
                code=500,
                message=f"获取访问令牌失败: {str(e)}"
            )
        
    def get_user_info(self, token: AuthToken, **kwargs) -> AuthUserResponse:
        """
        获取用户信息
        
        Args:
            token: 访问令牌
            
        Returns:
            用户信息响应
        """
        # 公共请求参数
        params = {
            "app_id": self.app_id,
            "method": "alipay.user.info.share",
            "charset": "utf-8",
            "sign_type": self.sign_type,
            "timestamp": self._get_timestamp_str(),
            "version": "1.0",
            "auth_token": token.access_token
        }
        
        # 计算签名
        if self.private_key:
            sign = self._sign(params)
            params["sign"] = sign
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.get(
                self.source.user_info_url,
                params=params,
                headers=headers
            )
            
            data = response.get("alipay_user_info_share_response", {})
            
            if data.get("code") != "10000":
                return AuthUserResponse(
                    code=data.get("code", 400),
                    message=data.get("msg", "获取用户信息失败")
                )
                
            user = AuthUser(
                uuid=f"{self.source.name}_{token.open_id}",
                username=data.get("nick_name", ""),
                nickname=data.get("nick_name", ""),
                avatar=data.get("avatar", ""),
                gender=self._get_gender(data.get("gender", "")),
                email="",  # 支付宝不会返回邮箱
                mobile=data.get("mobile", ""),
                location=f"{data.get('province', '')}{data.get('city', '')}",
                token=token,
                source=self.source.name,
                raw_user_info=data  # 添加原始用户信息
            )
            
            return AuthUserResponse(
                code=200,
                message="获取用户信息成功",
                data=user
            )
            
        except Exception as e:
            return AuthUserResponse(
                code=500,
                message=f"获取用户信息失败: {str(e)}"
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
            
        # 公共请求参数
        params = {
            "app_id": self.app_id,
            "method": "alipay.system.oauth.token",
            "charset": "utf-8",
            "sign_type": self.sign_type,
            "timestamp": self._get_timestamp_str(),
            "version": "1.0",
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token
        }
        
        # 计算签名
        if self.private_key:
            sign = self._sign(params)
            params["sign"] = sign
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            'Accept': 'application/json'
        }
        
        try:
            response = self.http_client.get(
                self.source.access_token_url,
                params=params,
                headers=headers
            )
            
            data = response.get("alipay_system_oauth_token_response", {})
            
            if "error_response" in response:
                error = response["error_response"]
                return AuthTokenResponse(
                    code=error.get("code", 400),
                    message=error.get("msg", "刷新访问令牌失败")
                )
                
            new_token = AuthToken(
                access_token=data.get("access_token", ""),
                token_type="Bearer",
                expires_in=data.get("expires_in", 0),
                refresh_token=data.get("refresh_token", ""),
                open_id=data.get("open_id", token.open_id)
            )
            
            return AuthTokenResponse(
                code=200,
                message="刷新访问令牌成功",
                data=new_token
            )
            
        except Exception as e:
            return AuthTokenResponse(
                code=500,
                message=f"刷新访问令牌失败: {str(e)}"
            )
        
    def revoke_token(self, token: AuthToken) -> bool:
        """
        撤销访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            是否成功
        """
        # 支付宝不支持标准方式撤销令牌
        return False
        
    def _get_gender(self, gender: str) -> AuthGender:
        """
        转换性别编码
        
        Args:
            gender: 性别字符串
            
        Returns:
            性别整数，0: 未知, 1: 男, 2: 女
        """
        if gender == "m":
            return AuthGender.MALE  # 男
        elif gender == "f":
            return AuthGender.FEMALE  # 女
        else:
            return AuthGender.UNKNOWN  # 未知
            
    def _get_timestamp_str(self) -> str:
        """
        获取当前时间戳字符串
        
        Returns:
            时间戳字符串，格式为：2021-01-01 12:00:00
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _sign(self, params: Dict[str, Any]) -> str:
        """
        计算签名
        
        按照支付宝开放平台的签名规则计算签名：
        1. 筛选并排序请求参数
        2. 拼接请求参数
        3. 计算签名值
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        if not self.private_key:
            return "signature_placeholder"
            
        # 1. 筛选并排序
        sorted_params = sorted(
            [(k, v) for k, v in params.items() if v and k != "sign"], 
            key=lambda x: x[0]
        )
        
        # 2. 拼接请求参数
        data_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 3. 计算签名值
        return self._sign_data(data_str)
        
    
        
    def _sign_data(self, data_str: str) -> str:
        """
        计算签名值
        
        Args:
            data_str: 待签名的字符串
            
        Returns:
            签名值
        """
        try:
            # 将私钥字符串转换为私钥对象
            private_key = self._load_private_key(self.private_key)
            if not private_key:
                return "signature_placeholder"
                
            # 根据签名类型选择哈希算法
            if self.sign_type == "RSA":
                # SHA1算法
                hash_algorithm = hashes.SHA1()
            else:
                # SHA256算法（RSA2）
                hash_algorithm = hashes.SHA256()
                
            # 计算签名
            signature = private_key.sign(
                data_str.encode('utf-8'),
                padding.PKCS1v15(),
                hash_algorithm
            )
            
            # Base64编码
            sign = base64.b64encode(signature).decode('utf-8')
            return sign
        except Exception as e:
            # 如果签名失败，记录错误并返回占位符
            print(f"签名失败: {str(e)}")
            return "signature_error"
            
    def _load_private_key(self, key_data):
        """
        加载私钥，支持多种格式
        
        Args:
            key_data: 私钥数据，可以是字符串或字节
            
        Returns:
            私钥对象，加载失败则返回None
        """
        if not key_data:
            return None
            
        # 确保key_data是字节类型
        if isinstance(key_data, str):
            key_data = key_data.encode('utf-8')
            
        # 尝试添加PEM头尾标记（如果缺少）
        if b'-----BEGIN' not in key_data:
            formatted_key = b'-----BEGIN RSA PRIVATE KEY-----\n'
            # 按64个字符分行
            chunks = [key_data[i:i+64] for i in range(0, len(key_data), 64)]
            for chunk in chunks:
                formatted_key += chunk + b'\n'
            formatted_key += b'-----END RSA PRIVATE KEY-----'
            key_data = formatted_key
            
        try:
            # 首先尝试以PEM格式加载
            return load_pem_private_key(key_data, password=None)
        except Exception as e:
            print(f"PEM格式加载失败: {str(e)}")
            try:
                # 如果PEM加载失败，尝试以DER格式加载
                return load_der_private_key(key_data, password=None)
            except Exception as e:
                print(f"DER格式加载失败: {str(e)}")
                return None 