"""
使用FastAPI创建的OAuth登录示例
"""
import os
from typing import Dict, Optional, List


import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
import sys
from pathlib import Path
from senweaver_oauth.builder import AuthRequestBuilder
from senweaver_oauth.enums.auth_source import AuthSource, AuthDefaultSource

import logging
# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from senweaver_oauth import AuthConfig
from senweaver_oauth.source.wechat_mini import AuthWechatMiniSource

# 加载环境变量
load_dotenv()


app = FastAPI(title="SenWeaver OAuth Example")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 配置日志

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置
OAUTH_CONFIGS = {
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/callback/github"),
    },
    "gitee": {
        "client_id": os.getenv("GITEE_CLIENT_ID", ""),
        "client_secret": os.getenv("GITEE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITEE_REDIRECT_URI", "http://localhost:8000/callback/gitee"),
    },
    "wechat_open": {
        "client_id": os.getenv("WECHAT_OPEN_CLIENT_ID", ""),
        "client_secret": os.getenv("WECHAT_OPEN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WECHAT_OPEN_REDIRECT_URI", "http://localhost:8000/callback/wechat_open"),
    },
    "qq": {
        "client_id": os.getenv("QQ_CLIENT_ID", ""),
        "client_secret": os.getenv("QQ_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("QQ_REDIRECT_URI", "http://localhost:8000/callback/qq"),
    },
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/callback/google"),
    },
    "weibo": {
        "client_id": os.getenv("WEIBO_CLIENT_ID", ""),
        "client_secret": os.getenv("WEIBO_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WEIBO_REDIRECT_URI", "http://localhost:8000/callback/weibo"),
    },
    "dingtalk": {
        "client_id": os.getenv("DINGTALK_CLIENT_ID", ""),
        "client_secret": os.getenv("DINGTALK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("DINGTALK_REDIRECT_URI", "http://localhost:8000/callback/dingtalk"),
    },
    "wechat": {
        "client_id": os.getenv("WECHAT_CLIENT_ID", ""),
        "client_secret": os.getenv("WECHAT_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WECHAT_REDIRECT_URI", "http://localhost:8000/callback/wechat"),
    },
    "wechat_mini": {
        "client_id": os.getenv("WECHAT_MINI_CLIENT_ID", ""),
        "client_secret": os.getenv("WECHAT_MINI_CLIENT_SECRET", ""),
    },
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID", ""),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/callback/facebook"),
    },
    "baidu": {
        "client_id": os.getenv("BAIDU_CLIENT_ID", ""),
        "client_secret": os.getenv("BAIDU_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("BAIDU_REDIRECT_URI", "http://localhost:8000/callback/baidu"),
    },
    "feishu": {
        "client_id": os.getenv("FEISHU_CLIENT_ID", ""),
        "client_secret": os.getenv("FEISHU_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("FEISHU_REDIRECT_URI", "http://localhost:8000/callback/feishu"),
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback/linkedin"),
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID", ""),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/callback/microsoft"),
    },
    "douyin": {
        "client_id": os.getenv("DOUYIN_CLIENT_ID", ""),
        "client_secret": os.getenv("DOUYIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("DOUYIN_REDIRECT_URI", "http://localhost:8000/callback/douyin"),
    },
    "twitter": {
        "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
        "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/callback/twitter"),
    },
    "alipay": {
        "client_id": os.getenv("ALIPAY_CLIENT_ID", ""),
        "client_secret": os.getenv("ALIPAY_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("ALIPAY_REDIRECT_URI", "http://localhost:8000/callback/alipay"),
    },
    "taobao": {
        "client_id": os.getenv("TAOBAO_CLIENT_ID", ""),
        "client_secret": os.getenv("TAOBAO_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("TAOBAO_REDIRECT_URI", "http://localhost:8000/callback/taobao"),
    },
    "jd": {
        "client_id": os.getenv("JD_CLIENT_ID", ""),
        "client_secret": os.getenv("JD_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("JD_REDIRECT_URI", "http://localhost:8000/callback/jd"),
    },
    "xiaomi": {
        "client_id": os.getenv("XIAOMI_CLIENT_ID", ""),
        "client_secret": os.getenv("XIAOMI_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("XIAOMI_REDIRECT_URI", "http://localhost:8000/callback/xiaomi"),
    },
    "zxxk":{
        "client_id": os.getenv("ZXXK_CLIENT_ID", ""),
        "client_secret": os.getenv("ZXXK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("ZXXK_REDIRECT_URI", "http://localhost:8000/callback/zxxk"),
        "extras":{
            "service": os.getenv("ZXXK_SERVICE", ""),
            "extra": os.getenv("ZXXK_EXTRA", ""),
            "open_id": os.getenv("ZXXK_OPEN_ID", ""),
            "service_args":{
                "_m": os.getenv("ZXXK_SERVICE_ARG_M", None),
                "_callbackmode": os.getenv("ZXXK_SERVICE_ARG_CALLBACKMODE", None),
                "_pmm": os.getenv("ZXXK_SERVICE_ARG_PMM", None),
            }
        }
    }
}

# 过滤掉未配置的平台
def available_platforms() -> List[AuthSource]:    
    result = []
    for platform, config in OAUTH_CONFIGS.items():
        if config["client_id"] and config["client_secret"]:
            source = AuthDefaultSource.get_source(platform)
            if source is None:
                source = AuthSource(name=platform)
            result.append(source)

    return result

# 响应模型
class OAuthResponse(BaseModel):
    code: int
    message: str
    data: Optional[Dict] = None

# 请求模型
class WechatMiniLoginRequest(BaseModel):
    code: str

class WechatMiniUserInfoRequest(BaseModel):
    session_id: str
    encrypted_data: str
    iv: str

class WechatMiniOneStepLoginRequest(BaseModel):
    code: str
    encrypted_data: str
    iv: str

# 简单会话存储
wechat_mini_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    首页
    """

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "SenWeaver OAuth示例",
            "platforms": available_platforms()
        },
    )
@app.get("/auth/{platform}")
async def auth(platform: str):
    """
    认证
    """
    if platform not in OAUTH_CONFIGS:
        raise HTTPException(status_code=404, detail=f"未支持的平台: {platform}")
    
    config = OAUTH_CONFIGS[platform]
    if not config["client_id"] or not config["client_secret"]:
        raise HTTPException(status_code=400, detail=f"平台 {platform} 未正确配置")
    
    # 创建授权请求
    try:
        auth_config = AuthConfig(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            extras=config.get("extras", {})
        )
        # 使用AuthRequestBuilder构建请求        
        auth_request = AuthRequestBuilder.builder().source(platform).auth_config(auth_config).build()
        if "source" in config:
            auth_request.auth_source.source = config["source"]
        auth_url = auth_request.authorize()

        return RedirectResponse(auth_url)
    except Exception as e:
        logger.error(f"创建授权请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建授权请求失败: {str(e)}")

@app.get("/callback/{platform}")
async def callback(platform: str, request: Request):
    """
    回调
    """
    if platform not in OAUTH_CONFIGS:
        raise HTTPException(status_code=404, detail=f"未支持的平台: {platform}")
    
    config = OAUTH_CONFIGS[platform]
    params = dict(request.query_params)
    
    try:
        auth_config = AuthConfig(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            extras=config.get("extras", {})
        )
        # 使用AuthRequestBuilder构建请求
        auth_request = AuthRequestBuilder.builder().source(platform).auth_config(auth_config).build()
        if "source" in config:
            auth_request.auth_source.source = config["source"]
        # 打印调试信息
        logger.info(f"Platform: {platform}")
        logger.info(f"Callback params: {params}")
        
        # 调用登录方法
        auth_user_response = auth_request.login(params)
        
        # 检查响应状态
        if auth_user_response.code != 200 or not auth_user_response.data:
            return {
                "platform": platform,
                "error": auth_user_response.message or "登录失败",
                "code": auth_user_response.code
            }
        if auth_user_response.data.service_url:
            # 调整到服务页面
            return RedirectResponse(auth_user_response.data.service_url)
        
        # 获取用户信息并转换为字典
        auth_user = auth_user_response.data
        user_dict = {
            "uuid": auth_user.uuid,
            "username": auth_user.username,
            "nickname": auth_user.nickname,
            "avatar": auth_user.avatar,
            "email": auth_user.email,
            "gender": auth_user.gender,
            "source": auth_user.source
        }
        
        # 返回用户信息
        return {
            "platform": platform,
            "user": user_dict,
        }
    except Exception as e:
        logger.error(f"处理回调失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"处理回调失败: {str(e)}")

@app.post("/api/login/wechat_mini", response_model=OAuthResponse)
async def wechat_mini_login(request: WechatMiniOneStepLoginRequest):
    """
    微信小程序一键登录（整合code和用户信息）
    
    将微信小程序登录和获取用户信息两步操作合并为一步，简化前端调用流程
    1. 小程序端同时获取code和加密的用户信息
    2. 前端一次性提交所有数据
    3. 后端完成登录和用户信息解密
    """
    if not OAUTH_CONFIGS["wechat_mini"]["client_id"] or not OAUTH_CONFIGS["wechat_mini"]["client_secret"]:
        return OAuthResponse(code=400, message="微信小程序未正确配置")
    
    # 创建配置
    auth_config = AuthConfig(
        client_id=OAUTH_CONFIGS["wechat_mini"]["client_id"],
        client_secret=OAUTH_CONFIGS["wechat_mini"]["client_secret"]
    )
    
    # 初始化微信小程序登录源
    auth_source = AuthWechatMiniSource(auth_config)

    params = request.model_dump()
    user_response = auth_source.login(params)
    if user_response.code != 200:
        return OAuthResponse(
            code=user_response.code,
            message=user_response.message
        )    
    # 生成会话ID
    import uuid
    session_id = str(uuid.uuid4())
    wechat_mini_sessions[session_id] = user_response.data.token

    auth_user = user_response.data
    user_dict = {
        "uuid": auth_user.uuid,
        "username": auth_user.username,
        "nickname": auth_user.nickname,
        "avatar": auth_user.avatar,
        "email": auth_user.email,
        "gender": auth_user.gender,
        "source": auth_user.source
    }
    
    # 返回用户信息和会话ID
    return OAuthResponse(
        code=200,
        message="登录成功",
        data={
            "session_id": session_id,
            "user": user_dict
        }
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 