# SenWeaver-OAuth

💫 强大、灵活且易用的OAuth授权集成组件 - Python版。提供统一便捷的第三方登录解决方案，已集成40+主流平台，包括Github、Gitee、微博、钉钉、百度、QQ、微信、Google、Facebook、抖音、领英、微软、飞书、京东、支付宝等国内外知名平台的OAuth授权。


## 特性

- 丰富的OAuth平台: 支持国内外数十家知名的第三方平台的OAuth登录
- 自定义state: 支持自定义State和缓存方式，开发者可根据实际情况选择任意缓存插件
- 自定义OAuth: 提供统一接口，支持接入任意OAuth网站，快速实现OAuth登录功能
- 自定义Http接口: 提供统一的HTTP工具接口，开发者可以根据自己项目的实际情况选择相对应的HTTP工具
- 自定义Scope: 支持自定义scope，以适配更多的业务场景，而不仅仅是为了登录
- 多种缓存实现: 支持内存缓存和Redis缓存，满足单实例和分布式应用的需求
- 代码规范·简单: 代码结构清晰、逻辑简单，遵循Python编码规范

## 快速开始

### 安装

```bash
pip install senweaver-oauth
```

### 使用示例

```python
from senweaver_oauth import AuthRequest, AuthConfig
from senweaver_oauth.source import AuthGiteeSource

# 创建授权request
auth_config = AuthConfig(
    client_id="clientId",
    client_secret="clientSecret",
    redirect_uri="redirectUri"
)
auth_request = AuthRequest.build(AuthGiteeSource, auth_config)

# 生成授权页面
auth_url = auth_request.authorize("state")
print(auth_url)

# 授权登录
callback = {
    "code": "授权码",
    "state": "state"
}
auth_response = auth_request.login(callback)
print(auth_response)
```

或者使用Builder模式:

```python
from senweaver_oauth import AuthRequestBuilder
from senweaver_oauth import AuthConfig

# 方式一：静态配置AuthConfig
auth_request = AuthRequestBuilder.builder() \
    .source("gitee") \
    .auth_config(AuthConfig(
        client_id="clientId",
        client_secret="clientSecret",
        redirect_uri="redirectUri"
    )) \
    .build()

# 生成授权页面
auth_url = auth_request.authorize("state")
print(auth_url)

# 方式二：动态获取并配置AuthConfig
def get_config(source):
    # 通过source动态获取AuthConfig
    # 此处可以灵活的从数据库或配置文件中获取配置
    return AuthConfig(
        client_id="clientId",
        client_secret="clientSecret",
        redirect_uri="redirectUri"
    )

auth_request = AuthRequestBuilder.builder() \
    .source("gitee") \
    .auth_config_function(get_config) \
    .build()

# 自定义平台
auth_request = AuthRequestBuilder.builder() \
    .extend_source(CustomAuthSource) \
    .source("custom") \
    .auth_config(AuthConfig(
        client_id="clientId",
        client_secret="clientSecret",
        redirect_uri="redirectUri"
    )) \
    .build()
```

### 使用Redis缓存

默认情况下，SenWeaver OAuth使用内存缓存存储OAuth状态和令牌信息。对于分布式应用，可以使用Redis缓存：

```python
import redis
from senweaver_oauth.cache import RedisCacheStore, DefaultCacheStore

# 创建Redis客户端
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password=None
)

# 创建Redis缓存存储
redis_cache = RedisCacheStore(
    redis_client=redis_client,
    prefix="senweaver_oauth:",  # 缓存键前缀
    ttl=300  # 默认过期时间（秒）
)

# 设置为默认缓存实例
DefaultCacheStore.set_instance(redis_cache)
```

更多缓存配置请参考[缓存存储文档](docs/cache_stores.md)。

## 已实现的平台

SenWeaver OAuth目前已集成以下40+平台的授权登录：

| 平台 | 授权方式 | 平台 | 授权方式 | 平台 | 授权方式 |
|-----|--------|-----|--------|-----|--------|
| Github | OAuth 2.0 | Gitee | OAuth 2.0 | 微博 | OAuth 2.0 |
| 钉钉 | OAuth 2.0 | 百度 | OAuth 2.0 | QQ | OAuth 2.0 |
| 微信 | OAuth 2.0 | 微信开放平台 | OAuth 2.0 | 微信小程序 | OAuth 2.0 |
| 微信企业版 | OAuth 2.0 | Google | OAuth 2.0 | Facebook | OAuth 2.0 |
| 抖音 | OAuth 2.0 | 领英 | OAuth 2.0 | 微软 | OAuth 2.0 |
| 飞书 | OAuth 2.0 | 淘宝 | OAuth 2.0 | 京东 | OAuth 2.0 |
| 支付宝 | OAuth 2.0 | 推特 | OAuth 1.0a | 小米 | OAuth 2.0 |
| 华为 | OAuth 2.0 | 企业微信 | OAuth 2.0 | 酷家乐 | OAuth 2.0 |
| Gitlab | OAuth 2.0 | 美团 | OAuth 2.0 | 饿了么 | OAuth 2.0 |
| 阿里云 | OAuth 2.0 | 今日头条 | OAuth 2.0 | Teambition | OAuth 2.0 |
| StackOverflow | OAuth 2.0 | Pinterest | OAuth 2.0 | 人人网 | OAuth 2.0 |
| 腾讯云开发平台 | OAuth 2.0 | OSChina | OAuth 2.0 | Coding | OAuth 2.0 |
| Amazon | OAuth 2.0 | Slack | OAuth 2.0 | Line | OAuth 2.0 |
| 喜马拉雅 | OAuth 2.0 | 学科网 | OAuth 2.0 |  |  |

更多平台正在持续添加中...

## 示例项目

- [FastAPI示例](examples/fastapi_example): 使用FastAPI实现的OAuth登录示例
- [Redis缓存示例](examples/redis_cache_example.py): 使用Redis缓存存储OAuth状态的示例

## 贡献

欢迎贡献代码，提交问题和建议！

## 开源协议

[MIT](LICENSE) 