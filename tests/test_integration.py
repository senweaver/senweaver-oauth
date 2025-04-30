"""
集成测试用例
"""
import unittest
from unittest.mock import patch, MagicMock

from senweaver_oauth import AuthConfig, AuthRequest, AuthRequestBuilder
from senweaver_oauth.source.github import AuthGithubSource


class TestIntegration(unittest.TestCase):
    """
    集成测试用例
    """
    
    def setUp(self):
        """
        测试前准备
        """
        self.auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        
    @patch('senweaver_oauth.source.auth_github_source.AuthGithubSource.get_access_token')
    @patch('senweaver_oauth.source.auth_github_source.AuthGithubSource.get_user_info')
    def test_github_auth_flow(self, mock_get_user_info, mock_get_access_token):
        """
        测试GitHub认证流程
        """
        # 创建模拟对象
        mock_token_response = MagicMock()
        mock_token_response.code = 200
        mock_token_response.data = MagicMock()
        
        mock_user_response = MagicMock()
        mock_user_response.code = 200
        mock_user_response.data = MagicMock()
        mock_user_response.data.uuid = "123456"
        mock_user_response.data.username = "test_user"
        mock_user_response.data.nickname = "Test User"
        mock_user_response.data.avatar = "https://example.com/avatar.png"
        mock_user_response.data.email = "test@example.com"
        
        # 设置模拟对象的返回值
        mock_get_access_token.return_value = mock_token_response
        mock_get_user_info.return_value = mock_user_response
        
        # 创建认证请求
        auth_request = AuthRequest.build(AuthGithubSource, self.auth_config)
        
        # 生成授权URL
        authorize_url = auth_request.authorize("test_state")
        
        # 验证授权URL
        self.assertIn("https://github.com/login/oauth/authorize", authorize_url)
        self.assertIn("client_id=test_client_id", authorize_url)
        self.assertIn("redirect_uri=http://localhost:8000/callback", authorize_url)
        self.assertIn("state=test_state", authorize_url)
        
        # 模拟回调
        callback = {
            "code": "test_code",
            "state": "test_state"
        }
        
        # 登录
        response = auth_request.login(callback)
        
        # 验证结果
        self.assertEqual(response.code, 200)
        self.assertEqual(response.data.uuid, "123456")
        self.assertEqual(response.data.username, "test_user")
        self.assertEqual(response.data.nickname, "Test User")
        self.assertEqual(response.data.avatar, "https://example.com/avatar.png")
        self.assertEqual(response.data.email, "test@example.com")
        
        # 验证模拟对象的调用
        mock_get_access_token.assert_called_once()
        self.assertEqual(mock_get_access_token.call_args[0][0].code, "test_code")
        mock_get_user_info.assert_called_once_with(mock_token_response.data)
        
    def test_auth_request_builder(self):
        """
        测试AuthRequestBuilder
        """
        # 创建认证请求
        auth_request = AuthRequestBuilder.builder() \
            .source("github") \
            .auth_config(self.auth_config) \
            .build()
            
        # 验证结果
        self.assertIsInstance(auth_request, AuthRequest)
        self.assertIsInstance(auth_request.auth_source, AuthGithubSource)
        
    def test_dynamic_auth_config(self):
        """
        测试动态认证配置
        """
        # 创建认证配置函数
        def get_config(source):
            return AuthConfig(
                client_id=f"{source}_client_id",
                client_secret=f"{source}_client_secret",
                redirect_uri=f"http://localhost:8000/{source}/callback"
            )
            
        # 创建认证请求
        auth_request = AuthRequestBuilder.builder() \
            .source("github") \
            .auth_config_function(get_config) \
            .build()
            
        # 验证结果
        self.assertIsInstance(auth_request, AuthRequest)
        self.assertIsInstance(auth_request.auth_source, AuthGithubSource)
        self.assertEqual(auth_request.auth_source.config.client_id, "github_client_id")
        self.assertEqual(auth_request.auth_source.config.client_secret, "github_client_secret")
        self.assertEqual(auth_request.auth_source.config.redirect_uri, "http://localhost:8000/github/callback")
        
    @patch('senweaver_oauth.source.base_auth_source.BaseAuthSource.get_authorize_params')
    def test_authorize_method(self, mock_get_authorize_params):
        """
        测试authorize方法
        """
        # 创建模拟对象
        mock_get_authorize_params.return_value = {
            "response_type": "code",
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8000/callback",
            "state": "test_state",
            "scope": "user"
        }
        
        # 创建认证请求
        auth_request = AuthRequest.build(AuthGithubSource, self.auth_config)
        
        # 生成授权URL
        authorize_url = auth_request.authorize("test_state")
        
        # 验证授权URL
        expected_url = "https://github.com/login/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http://localhost:8000/callback&state=test_state&scope=user"
        self.assertEqual(authorize_url, expected_url)
        
        # 验证模拟对象的调用
        mock_get_authorize_params.assert_called_once_with("test_state")


if __name__ == "__main__":
    unittest.main() 