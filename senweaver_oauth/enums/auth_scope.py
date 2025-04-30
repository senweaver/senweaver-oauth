"""
授权作用域枚举
"""
from enum import Enum
from typing import List


class AuthScope(Enum):
    """
    授权作用域枚举
    定义了各平台默认的scope
    """
    # Github 默认scope
    GITHUB = ['user']
    
    # Gitee 默认scope
    GITEE = ['user_info']
    
    # 微博 默认scope
    WEIBO = ['email']
    
    # 钉钉 默认scope
    DINGTALK = ['openid', 'corpid']
    
    # 百度 默认scope
    BAIDU = ['basic', 'netdisk']
    
    # Coding 默认scope
    CODING = ['user', 'email']
    
    # 腾讯云开发者平台 默认scope
    TENCENT_CLOUD = ['user']
    
    # OSChina 默认scope
    OSCHINA = ['user']
    
    # 支付宝 默认scope
    ALIPAY = ['auth_user']
    
    # QQ 默认scope
    QQ = ['get_user_info']
    
    # 微信 默认scope
    WECHAT = ['snsapi_userinfo']
    
    # 微信开放平台 默认scope
    WECHAT_OPEN = ['snsapi_login']
    
    # 企业微信 默认scope
    WECHAT_ENTERPRISE = ['snsapi_base']
    
    # 微信小程序 默认scope
    WECHAT_MINI = ['snsapi_base']
    
    # 淘宝 默认scope
    TAOBAO = ['user_info']
    
    # Google 默认scope
    GOOGLE = ['profile', 'email']
    
    # Facebook 默认scope
    FACEBOOK = ['public_profile', 'email']
    
    # 抖音 默认scope
    DOUYIN = ['user_info']
    
    # 领英 默认scope
    LINKEDIN = ['r_liteprofile', 'r_emailaddress']
    
    # 小米 默认scope
    XIAOMI = ['user']
    
    # 微软 默认scope
    MICROSOFT = ['User.Read']
    
    # 今日头条 默认scope
    TOUTIAO = ['user_info']
    
    # Teambition 默认scope
    TEAMBITION = ['user']
    
    # StackOverflow 默认scope
    STACK_OVERFLOW = ['read_user']
    
    # Pinterest 默认scope
    PINTEREST = ['user_accounts:read']
    
    # 人人 默认scope
    RENREN = ['read_user_info']
    
    # 华为 默认scope
    HUAWEI = ['profile']
    
    # 酷家乐 默认scope
    KUJIALE = ['user_info']
    
    # Gitlab 默认scope
    GITLAB = ['read_user']
    
    # 美团 默认scope
    MEITUAN = ['user_info']
    
    # 饿了么 默认scope
    ELEME = ['user_info']
    
    # 推特 默认scope
    TWITTER = ['read:user']
    
    # 飞书 默认scope
    FEISHU = ['user_info']
    
    # 京东 默认scope
    JD = ['snsapi_base']
    
    # 阿里云 默认scope
    ALIYUN = ['user']
    
    # 喜马拉雅 默认scope
    XMLY = ['user_info']
    
    # Amazon 默认scope
    AMAZON = ['profile']
    
    # Slack 默认scope
    SLACK = ['users:read']
    
    # Line 默认scope
    LINE = ['profile']

    @classmethod
    def get_scope(cls, source_name: str) -> List[str]:
        """
        获取指定平台的默认scope
        
        Args:
            source_name: 平台名称
            
        Returns:
            平台默认scope列表
        """
        try:
            return getattr(cls, source_name.upper()).value
        except (AttributeError, KeyError):
            return []
            
    @classmethod
    def get_scope_str(cls, source_name: str, delimiter: str = ' ') -> str:
        """
        获取指定平台的默认scope字符串
        
        Args:
            source_name: 平台名称
            delimiter: 分隔符，默认为空格
            
        Returns:
            平台默认scope字符串
        """
        scope_list = cls.get_scope(source_name)
        if not scope_list:
            return ''
        return delimiter.join(scope_list) 