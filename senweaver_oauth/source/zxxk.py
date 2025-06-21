"""
学科网认证源
"""

import hashlib
import time
import uuid

from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.enums.auth_gender import AuthGender
from senweaver_oauth.enums.auth_source import AuthDefaultSource, AuthSource
from senweaver_oauth.model.auth_callback import AuthCallback
from senweaver_oauth.model.auth_response import AuthTokenResponse, AuthUserResponse
from senweaver_oauth.model.auth_token import AuthToken
from senweaver_oauth.model.auth_user import AuthUser
from senweaver_oauth.source.base import BaseAuthSource


class AuthZxxkSource(BaseAuthSource):
    """
    学科网认证源
    AuthConfig(
            client_id="必填,分配的 AppKey",
            client_secret="必填,分配的 AppSecret",
            redirect_uri="必填,授权回调地址",
            extras={
              "service": "必填，学科网的服务，注意域名后面的斜杠不能少",
              "open_id": "为当前用户 open_id，有时必填",
              "extra": "静默注册时，填写手机号",
              "service_args": { //如题库参数
                "_m": "当使⽤iframe嵌套题库⻚⾯时,平台域名地址",
                "_n":"合作⽅接收通知地址,callbackmode值⾮1时必填",
                "_callbackmode":"不传时-⻚⾯刷新加载，传1时-⻚⾯⽆刷新加载",
                "_pmm":"是否向⽗⻚⾯发送⼴播消息,传1时向⽗⻚⾯发送⼴播",
              }              
            }
        )
    """

    def __init__(self, config: AuthConfig, source: Optional[AuthSource] = None):
        """
        初始化

        Args:
            config: 认证配置
            source: 认证源，默认为学科网
        """
        super().__init__(config=config, source=source or AuthDefaultSource.ZXXK)

    def _get_timestamp(self) -> str:
        """
        获取当前时间的时间戳（毫秒），并以字符串形式返回。
        """
        return str(int(time.time() * 1000))

    def authorize(self, state: Optional[str] = None, **kwargs) -> str:
        """
        生成授权URL

        Args:
            service: 学科网的服务，注意域名后面的斜杠不能少
            state: 自定义state参数，用于防止CSRF攻击
            open_id: 学科网返回给应用的OpenId
            extra: 静默注册时，填写手机号

        Returns:
            授权URL
        """
        service = kwargs.get("service")
        if not service:
            raise ValueError("service is required")

        open_id = kwargs.get("open_id")

        extra = kwargs.get("extra")

        # 生成随机state参数
        if not state:
            state = str(uuid.uuid4())

        # 缓存state参数，默认有效期3分钟
        self.cache_store.set(state, state, 180)

        open_id = self.aes_encrypt(open_id, self.config.client_secret)
        timespan = self.aes_encrypt(self._get_timestamp(), self.config.client_secret)
        extra = self.aes_encrypt(extra, self.config.client_secret)
        # 构建授权参数
        params = {
            "client_id": self.config.client_id,
            "open_id": open_id,
            "service": service,
            "redirect_uri": self.config.redirect_uri,
            "timespan": timespan,
            "extra": extra,
        }
        params["signature"] = self._sign(params)
        params["state"] = state or str(uuid.uuid4())
        # 生成授权URL
        return self.build_authorize_url(params)

    def _sign(self, params: Dict[str, str]) -> str:
        """
        计算签名

        签名算法，将请求参数按照参数名ASCII码从小到大排序，
        然后拼接成字符串，最后使用MD5加密得到签名

        Args:
            params: 请求参数

        Returns:
            签名字符串
        """

        # 按照参数名ASCII码从小到大排序
        sorted_params = sorted(params.items())

        # 拼接成字符串
        sign_str = ""
        for k, v in sorted_params:
            sign_str += v
        sign_str += self.config.client_secret

        # MD5加密
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    def build_authorize_url(self, params: Dict[str, Any]) -> str:
        """
        将所有参数值进行URL编码，防止特殊字符影响URL解析。
        :param params: 参数字典
        :return: 编码后的参数字符串
        """
        url = self.source.authorize_url
        query = urlencode(params)
        return f"{url}?{query}"

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
            "client_id": self.config.client_id,
            "code": callback.code,
            "redirect_uri": self.config.redirect_uri,
        }
        params["signature"] = self._sign(params)

        headers = {"Accept": "application/json"}
        query = urlencode(params)
        try:
            response = self.http_client.post(
                f"{self.source.access_token_url}?{query}", headers=headers
            )

            if response.get("error"):
                return AuthTokenResponse.failure(
                    message=response.get("error", "获取访问令牌失败")
                )

            # 提取令牌信息
            token = AuthToken(
                access_token=response.get("access_token"),
                expires_in=response.get("expires", 0),
                token_type="Bearer",
                code=callback.code,
            )

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
            headers = {"Accept": "application/json"}
            response = self.http_client.get(
                f"{self.source.user_info_url}?access_token={token.access_token}",
                headers=headers,
            )

            if response.get("error"):
                return AuthUserResponse.failure(
                    response.get("error", "获取用户信息失败")
                )

            token.open_id = response.get("open_id")
            # 获取用户信息
            parsed = urlparse(self.source.user_info_url)
            oauth_server_url = f"{parsed.scheme}://{parsed.netloc}"
            service = self.config.extras.get("service")
            service_url = None
            if service:
                service_args = self.config.extras.get("service_args",{})
                service_args = service_args.copy()                
                service_args["_openid"] = token.open_id
                service_query = urlencode({"service":f"{service}?{urlencode(service_args)}"})            
                service_url = f"{oauth_server_url}/login?{service_query}"
            user = AuthUser(
                uuid=str(response.get("open_id")),
                username=response.get("open_id"),
                gender=AuthGender.UNKNOWN,
                source=self.source.name,
                token=token,
                raw_user_info=response,
                service_url=service_url,
            )

            return AuthUserResponse.success(user)

        except Exception as e:
            return AuthUserResponse.error(f"获取用户信息异常: {str(e)}")

    def aes_encrypt(self, text: str, key: str) -> str:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding
        from cryptography.hazmat.backends import default_backend
        import base64

        """
        使用AES/ECB/PKCS5Padding方式加密字符串，返回Base64编码的密文。
        :param text: 需要加密的明文字符串
        :param key: 密钥字符串（长度需为16/24/32字节）
        :return: Base64编码的加密字符串
        """
        if not text or not key:
            return ""
        # 确保key为16/24/32字节
        key_bytes = key.encode("utf-8")
        if len(key_bytes) not in (16, 24, 32):
            raise ValueError("Key must be 16, 24, or 32 bytes long")
        # PKCS7填充（等价于Java的PKCS5Padding）
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode("utf-8")) + padder.finalize()
        # AES-ECB加密
        cipher = Cipher(
            algorithms.AES(key_bytes), modes.ECB(), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        # Base64编码
        return base64.b64encode(encrypted).decode("utf-8")
