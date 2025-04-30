"""
AuthRequestBuilder测试用例
"""
import unittest
import pytest
from unittest.mock import MagicMock, patch

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.request import AuthRequest
from senweaver_oauth.builder import AuthRequestBuilder
from senweaver_oauth.enums.auth_source import AuthSource


class TestAuthRequestBuilder(unittest.TestCase):
    """
    AuthRequestBuilder测试用例
    """
    
    def test_builder_method(self):
        """
        测试builder方法
        """
        builder = AuthRequestBuilder.builder()
        self.assertIsInstance(builder, AuthRequestBuilder)
        
    def test_source_method(self):
        """
        测试source方法
        """
        builder = AuthRequestBuilder.builder()
        result = builder.source("github")
        self.assertEqual(builder._source, "github")
        self.assertIs(result, builder)  # 测试链式调用
        
    def test_auth_config_method(self):
        """
        测试auth_config方法
        """
        builder = AuthRequestBuilder.builder()
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        result = builder.auth_config(auth_config)
        self.assertIs(builder._auth_config, auth_config)
        self.assertIs(result, builder)  # 测试链式调用
        
    def test_auth_config_function_method(self):
        """
        测试auth_config_function方法
        """
        builder = AuthRequestBuilder.builder()
        
        def get_config(source):
            return AuthConfig(
                client_id=f"{source}_client_id",
                client_secret=f"{source}_client_secret",
                redirect_uri=f"http://localhost:8000/{source}/callback"
            )
            
        result = builder.auth_config_function(get_config)
        self.assertEqual(builder._auth_config_function, get_config)
        self.assertIs(result, builder)  # 测试链式调用
        
    def test_extend_source_method(self):
        """
        测试extend_source方法
        """
        builder = AuthRequestBuilder.builder()
        
        class CustomAuthSource:
            CUSTOM = AuthSource(
                name="custom",
                authorize_url="https://custom.com/oauth/authorize",
                access_token_url="https://custom.com/oauth/token",
                user_info_url="https://custom.com/api/user",
                scope_delimiter=" "
            )
            
        result = builder.extend_source([CustomAuthSource])
        self.assertEqual(builder._extend_sources, [CustomAuthSource])
        self.assertIs(result, builder)  # 测试链式调用
        
    @patch('senweaver_oauth.builder.AuthDefaultSource.get_source')
    @patch('senweaver_oauth.builder.AuthRequestBuilder._get_auth_source_class')
    def test_build_method(self, mock_get_auth_source_class, mock_get_source):
        """
        测试build方法
        """
        # 创建模拟对象
        mock_source = MagicMock()
        mock_source.name = "github"
        
        mock_auth_source_class = MagicMock()
        mock_auth_source_instance = MagicMock()
        mock_auth_source_class.return_value = mock_auth_source_instance
        
        # 设置模拟对象的返回值
        mock_get_source.return_value = mock_source
        mock_get_auth_source_class.return_value = mock_auth_source_class
        
        # 创建测试对象
        builder = AuthRequestBuilder.builder()
        builder.source("github")
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        builder.auth_config(auth_config)
        
        # 执行测试
        result = builder.build()
        
        # 验证结果
        self.assertIsInstance(result, AuthRequest)
        self.assertEqual(result.auth_source, mock_auth_source_instance)
        
        # 验证模拟对象的调用
        mock_get_source.assert_called_once_with("github")
        mock_get_auth_source_class.assert_called_once()
        mock_auth_source_class.assert_called_once_with(auth_config)
        
    def test_build_method_with_missing_source(self):
        """
        测试build方法，缺少source参数
        """
        builder = AuthRequestBuilder.builder()
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        builder.auth_config(auth_config)
        
        with self.assertRaises(ValueError) as context:
            builder.build()
            
        self.assertIn("认证源不能为空", str(context.exception))
        
    def test_build_method_with_missing_auth_config(self):
        """
        测试build方法，缺少auth_config参数
        """
        builder = AuthRequestBuilder.builder()
        builder.source("github")
        
        with self.assertRaises(ValueError) as context:
            builder.build()
            
        self.assertIn("认证配置不能为空", str(context.exception))
        
    def test_get_auth_config_with_static_config(self):
        """
        测试_get_auth_config方法，使用静态配置
        """
        builder = AuthRequestBuilder.builder()
        auth_config = AuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        builder.auth_config(auth_config)
        
        result = builder._get_auth_config()
        self.assertIs(result, auth_config)
        
    def test_get_auth_config_with_function(self):
        """
        测试_get_auth_config方法，使用函数配置
        """
        builder = AuthRequestBuilder.builder()
        builder.source("github")
        
        def get_config(source):
            return AuthConfig(
                client_id=f"{source}_client_id",
                client_secret=f"{source}_client_secret",
                redirect_uri=f"http://localhost:8000/{source}/callback"
            )
            
        builder.auth_config_function(get_config)
        
        result = builder._get_auth_config()
        self.assertEqual(result.client_id, "github_client_id")
        self.assertEqual(result.client_secret, "github_client_secret")
        self.assertEqual(result.redirect_uri, "http://localhost:8000/github/callback")


if __name__ == "__main__":
    unittest.main() 