"""
授权来源枚举
"""
from typing import Optional, List


class AuthSource:
    """
    授权平台基类
    """
    def __init__(self, name: str, authorize_url: str, access_token_url: str, 
                 user_info_url: str, revoke_token_url: Optional[str] = None,
                 refresh_token_url: Optional[str] = None, scope_delimiter: str = ' '):
        """
        初始化
        
        Args:
            name: 平台名称
            authorize_url: 授权URL
            access_token_url: 获取token的URL
            user_info_url: 获取用户信息的URL
            revoke_token_url: 撤销token的URL
            refresh_token_url: 刷新token的URL
            scope_delimiter: scope分隔符
        """
        self.name = name
        self.authorize_url = authorize_url
        self.access_token_url = access_token_url
        self.user_info_url = user_info_url
        self.revoke_token_url = revoke_token_url
        self.refresh_token_url = refresh_token_url
        self.scope_delimiter = scope_delimiter
        
    def __str__(self) -> str:
        return self.name
        
    def __repr__(self) -> str:
        return f"AuthSource(name={self.name})"


class AuthDefaultSource:
    """
    默认支持的平台
    """
    GITHUB = AuthSource(
        name="github",
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        user_info_url="https://api.github.com/user",
        scope_delimiter=" "
    )
    
    GITEE = AuthSource(
        name="gitee",
        authorize_url="https://gitee.com/oauth/authorize",
        access_token_url="https://gitee.com/oauth/token",
        user_info_url="https://gitee.com/api/v5/user",
        refresh_token_url="https://gitee.com/oauth/token",
        scope_delimiter=","
    )
    
    WEIBO = AuthSource(
        name="weibo",
        authorize_url="https://api.weibo.com/oauth2/authorize",
        access_token_url="https://api.weibo.com/oauth2/access_token",
        user_info_url="https://api.weibo.com/2/users/show.json",
        revoke_token_url="https://api.weibo.com/oauth2/revokeoauth2",
        scope_delimiter=","
    )
    
    DINGTALK = AuthSource(
        name="dingtalk",
        authorize_url="https://oapi.dingtalk.com/connect/qrconnect",
        access_token_url="https://oapi.dingtalk.com/gettoken",
        user_info_url="https://oapi.dingtalk.com/user/get",
        scope_delimiter=" "
    )
    
    BAIDU = AuthSource(
        name="baidu",
        authorize_url="https://openapi.baidu.com/oauth/2.0/authorize",
        access_token_url="https://openapi.baidu.com/oauth/2.0/token",
        user_info_url="https://openapi.baidu.com/rest/2.0/passport/users/getInfo",
        refresh_token_url="https://openapi.baidu.com/oauth/2.0/token",
        revoke_token_url="https://openapi.baidu.com/rest/2.0/passport/auth/revokeAuthorization",
        scope_delimiter=" "
    )
    
    CODING = AuthSource(
        name="coding",
        authorize_url="https://coding.net/oauth_authorize.html",
        access_token_url="https://coding.net/api/oauth/access_token",
        user_info_url="https://coding.net/api/current_user",
        scope_delimiter=" "
    )
    
    TENCENT_CLOUD = AuthSource(
        name="tencent_cloud",
        authorize_url="https://cloud.tencent.com/open/authorize",
        access_token_url="https://cloud.tencent.com/open/access_token",
        user_info_url="https://cloud.tencent.com/open/info",
        scope_delimiter=","
    )
    
    OSCHINA = AuthSource(
        name="oschina",
        authorize_url="https://www.oschina.net/action/oauth2/authorize",
        access_token_url="https://www.oschina.net/action/openapi/token",
        user_info_url="https://www.oschina.net/action/openapi/user",
        scope_delimiter=","
    )
    
    ALIPAY = AuthSource(
        name="alipay",
        authorize_url="https://openauth.alipay.com/oauth2/publicAppAuthorize.htm",
        access_token_url="https://openapi.alipay.com/gateway.do",
        user_info_url="https://openapi.alipay.com/gateway.do",
        scope_delimiter=","
    )
    
    QQ = AuthSource(
        name="qq",
        authorize_url="https://graph.qq.com/oauth2.0/authorize",
        access_token_url="https://graph.qq.com/oauth2.0/token",
        user_info_url="https://graph.qq.com/user/get_user_info",
        scope_delimiter=","
    )
    
    WECHAT = AuthSource(
        name="wechat",
        authorize_url="https://open.weixin.qq.com/connect/oauth2/authorize",
        access_token_url="https://api.weixin.qq.com/sns/oauth2/access_token",
        user_info_url="https://api.weixin.qq.com/sns/userinfo",
        refresh_token_url="https://api.weixin.qq.com/sns/oauth2/refresh_token",
        scope_delimiter=","
    )
    
    WECHAT_OPEN = AuthSource(
        name="wechat_open",
        authorize_url="https://open.weixin.qq.com/connect/qrconnect",
        access_token_url="https://api.weixin.qq.com/sns/oauth2/access_token",
        user_info_url="https://api.weixin.qq.com/sns/userinfo",
        refresh_token_url="https://api.weixin.qq.com/sns/oauth2/refresh_token",
        scope_delimiter=","
    )
    
    WECHAT_ENTERPRISE = AuthSource(
        name="wechat_enterprise",
        authorize_url="https://open.work.weixin.qq.com/wwopen/sso/qrConnect",
        access_token_url="https://qyapi.weixin.qq.com/cgi-bin/gettoken",
        user_info_url="https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo",
        scope_delimiter=","
    )
    
    WECHAT_MINI = AuthSource(
        name="wechat_mini",
        authorize_url="",  # 小程序没有授权URL，直接在小程序端调用wx.login获取code
        access_token_url="https://api.weixin.qq.com/sns/jscode2session",
        user_info_url="",  # 小程序用户信息需要通过小程序端调用wx.getUserInfo获取
        scope_delimiter=","
    )
    
    TAOBAO = AuthSource(
        name="taobao",
        authorize_url="https://oauth.taobao.com/authorize",
        access_token_url="https://oauth.taobao.com/token",
        user_info_url="https://gw.api.taobao.com/router/rest",
        scope_delimiter=","
    )
    
    GOOGLE = AuthSource(
        name="google",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        access_token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v3/userinfo",
        scope_delimiter=" "
    )
    
    FACEBOOK = AuthSource(
        name="facebook",
        authorize_url="https://www.facebook.com/v9.0/dialog/oauth",
        access_token_url="https://graph.facebook.com/v9.0/oauth/access_token",
        user_info_url="https://graph.facebook.com/v9.0/me",
        scope_delimiter=","
    )
    
    DOUYIN = AuthSource(
        name="douyin",
        authorize_url="https://open.douyin.com/platform/oauth/connect",
        access_token_url="https://open.douyin.com/oauth/access_token/",
        user_info_url="https://open.douyin.com/oauth/userinfo/",
        refresh_token_url="https://open.douyin.com/oauth/refresh_token/",
        scope_delimiter=","
    )
    
    LINKEDIN = AuthSource(
        name="linkedin",
        authorize_url="https://www.linkedin.com/oauth/v2/authorization",
        access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
        user_info_url="https://api.linkedin.com/v2/me",
        refresh_token_url="https://www.linkedin.com/oauth/v2/accessToken",
        scope_delimiter=" "
    )
    
    XIAOMI = AuthSource(
        name="xiaomi",
        authorize_url="https://account.xiaomi.com/oauth2/authorize",
        access_token_url="https://account.xiaomi.com/oauth2/token",
        user_info_url="https://open.account.xiaomi.com/user/profile",
        refresh_token_url="https://account.xiaomi.com/oauth2/token",
        scope_delimiter=","
    )
    
    MICROSOFT = AuthSource(
        name="microsoft",
        authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        user_info_url="https://graph.microsoft.com/v1.0/me",
        refresh_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        scope_delimiter=" "
    )
    
    TOUTIAO = AuthSource(
        name="toutiao",
        authorize_url="https://open.snssdk.com/oauth/authorize",
        access_token_url="https://open.snssdk.com/oauth/access_token/",
        user_info_url="https://open.snssdk.com/oauth/userinfo/",
        refresh_token_url="https://open.snssdk.com/oauth/refresh_token/",
        scope_delimiter=","
    )
    
    TEAMBITION = AuthSource(
        name="teambition",
        authorize_url="https://account.teambition.com/oauth2/authorize",
        access_token_url="https://account.teambition.com/oauth2/access_token",
        user_info_url="https://api.teambition.com/users/me",
        refresh_token_url="https://account.teambition.com/oauth2/refresh_token",
        scope_delimiter=","
    )
    
    STACK_OVERFLOW = AuthSource(
        name="stack_overflow",
        authorize_url="https://stackoverflow.com/oauth",
        access_token_url="https://stackoverflow.com/oauth/access_token",
        user_info_url="https://api.stackexchange.com/2.2/me",
        scope_delimiter=","
    )
    
    PINTEREST = AuthSource(
        name="pinterest",
        authorize_url="https://api.pinterest.com/oauth",
        access_token_url="https://api.pinterest.com/v5/oauth/token",
        user_info_url="https://api.pinterest.com/v5/user_account",
        scope_delimiter=","
    )
    
    RENREN = AuthSource(
        name="renren",
        authorize_url="https://graph.renren.com/oauth/authorize",
        access_token_url="https://graph.renren.com/oauth/token",
        user_info_url="https://api.renren.com/v2/user/login/get",
        scope_delimiter=","
    )
    
    HUAWEI = AuthSource(
        name="huawei",
        authorize_url="https://oauth-login.cloud.huawei.com/oauth2/v2/authorize",
        access_token_url="https://oauth-login.cloud.huawei.com/oauth2/v2/token",
        user_info_url="https://api.vmall.com/rest.php",
        scope_delimiter=" "
    )
    
    KUJIALE = AuthSource(
        name="kujiale",
        authorize_url="https://oauth.kujiale.com/oauth2/show",
        access_token_url="https://oauth.kujiale.com/oauth2/auth/token",
        user_info_url="https://oauth.kujiale.com/oauth2/openapi/user",
        refresh_token_url="https://oauth.kujiale.com/oauth2/auth/token/refresh",
        scope_delimiter=","
    )
    
    GITLAB = AuthSource(
        name="gitlab",
        authorize_url="https://gitlab.com/oauth/authorize",
        access_token_url="https://gitlab.com/oauth/token",
        user_info_url="https://gitlab.com/api/v4/user",
        refresh_token_url="https://gitlab.com/oauth/token",
        scope_delimiter=" "
    )
    
    MEITUAN = AuthSource(
        name="meituan",
        authorize_url="https://openapi.waimai.meituan.com/oauth/authorize",
        access_token_url="https://openapi.waimai.meituan.com/oauth/access_token",
        user_info_url="https://openapi.waimai.meituan.com/oauth/userinfo",
        scope_delimiter=","
    )
    
    ELEME = AuthSource(
        name="eleme",
        authorize_url="https://open-api.shop.ele.me/authorize",
        access_token_url="https://open-api.shop.ele.me/token",
        user_info_url="https://open-api.shop.ele.me/api/v1/user",
        refresh_token_url="https://open-api.shop.ele.me/token",
        scope_delimiter=","
    )
    
    TWITTER = AuthSource(
        name="twitter",
        authorize_url="https://api.twitter.com/oauth/authenticate",
        access_token_url="https://api.twitter.com/oauth/access_token",
        user_info_url="https://api.twitter.com/1.1/account/verify_credentials.json",
        scope_delimiter=","
    )
    
    FEISHU = AuthSource(
        name="feishu",
        authorize_url="https://open.feishu.cn/open-apis/authen/v1/index",
        access_token_url="https://open.feishu.cn/open-apis/authen/v1/access_token",
        user_info_url="https://open.feishu.cn/open-apis/authen/v1/user_info",
        refresh_token_url="https://open.feishu.cn/open-apis/authen/v1/refresh_access_token",
        scope_delimiter=","
    )
    
    JD = AuthSource(
        name="jd",
        authorize_url="https://open-oauth.jd.com/oauth2/to_login",
        access_token_url="https://open-oauth.jd.com/oauth2/access_token",
        user_info_url="https://api.jd.com/routerjson",
        refresh_token_url="https://open-oauth.jd.com/oauth2/refresh_token",
        scope_delimiter=","
    )
    
    ALIYUN = AuthSource(
        name="aliyun",
        authorize_url="https://signin.aliyun.com/oauth2/v1/auth",
        access_token_url="https://oauth.aliyun.com/v1/token",
        user_info_url="https://oauth.aliyun.com/v1/userinfo",
        refresh_token_url="https://oauth.aliyun.com/v1/token",
        scope_delimiter=" "
    )
    
    XMLY = AuthSource(
        name="xmly",
        authorize_url="https://api.ximalaya.com/oauth2/js/authorize",
        access_token_url="https://api.ximalaya.com/oauth2/v2/access_token",
        user_info_url="https://api.ximalaya.com/profile/user_info",
        refresh_token_url="https://api.ximalaya.com/oauth2/v2/refresh_token",
        scope_delimiter=","
    )
    
    AMAZON = AuthSource(
        name="amazon",
        authorize_url="https://www.amazon.com/ap/oa",
        access_token_url="https://api.amazon.com/auth/o2/token",
        user_info_url="https://api.amazon.com/user/profile",
        refresh_token_url="https://api.amazon.com/auth/o2/token",
        scope_delimiter=" "
    )
    
    SLACK = AuthSource(
        name="slack",
        authorize_url="https://slack.com/oauth/v2/authorize",
        access_token_url="https://slack.com/api/oauth.v2.access",
        user_info_url="https://slack.com/api/users.info",
        scope_delimiter=","
    )
    
    LINE = AuthSource(
        name="line",
        authorize_url="https://access.line.me/oauth2/v2.1/authorize",
        access_token_url="https://api.line.me/oauth2/v2.1/token",
        user_info_url="https://api.line.me/v2/profile",
        refresh_token_url="https://api.line.me/oauth2/v2.1/token",
        scope_delimiter=" "
    )
    
    @classmethod
    def get_source(cls, source_name: str) -> Optional[AuthSource]:
        """
        获取授权平台
        
        Args:
            source_name: 平台名称
            
        Returns:
            授权平台对象，如果不存在则返回None
        """
        source_name = source_name.upper()
        try:
            return getattr(cls, source_name)
        except (AttributeError, KeyError):
            return None
            
    @classmethod
    def values(cls) -> List[AuthSource]:
        """
        获取所有支持的平台
        
        Returns:
            所有支持的平台列表
        """
        return [getattr(cls, attr) for attr in dir(cls) 
                if not attr.startswith('_') and isinstance(getattr(cls, attr), AuthSource)]
                
    @classmethod
    def names(cls) -> List[str]:
        """
        获取所有支持的平台名称
        
        Returns:
            所有支持的平台名称列表
        """
        return [source.name for source in cls.values()] 