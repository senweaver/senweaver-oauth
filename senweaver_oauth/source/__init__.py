#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
第三方登录授权模块，各个平台的授权源
"""
from typing import List

from senweaver_oauth.source.base import BaseAuthSource
from senweaver_oauth.source.alipay import AuthAlipaySource
from senweaver_oauth.source.aliyun import AuthAliyunSource
from senweaver_oauth.source.amazon import AuthAmazonSource
from senweaver_oauth.source.baidu import AuthBaiduSource
from senweaver_oauth.source.coding import AuthCodingSource
from senweaver_oauth.source.dingtalk import AuthDingtalkSource
from senweaver_oauth.source.douyin import AuthDouyinSource
from senweaver_oauth.source.eleme import AuthElemeSource
from senweaver_oauth.source.facebook import AuthFacebookSource
from senweaver_oauth.source.feishu import AuthFeishuSource
from senweaver_oauth.source.gitee import AuthGiteeSource
from senweaver_oauth.source.github import AuthGithubSource
from senweaver_oauth.source.gitlab import AuthGitlabSource
from senweaver_oauth.source.google import AuthGoogleSource
from senweaver_oauth.source.huawei import AuthHuaweiSource
from senweaver_oauth.source.jd import AuthJdSource
from senweaver_oauth.source.kujiale import AuthKujialeSource
from senweaver_oauth.source.line import AuthLineSource
from senweaver_oauth.source.linkedin import AuthLinkedinSource
from senweaver_oauth.source.meituan import AuthMeituanSource
from senweaver_oauth.source.microsoft import AuthMicrosoftSource
from senweaver_oauth.source.xiaomi import AuthXiaomiSource
from senweaver_oauth.source.oschina import AuthOschinaSource
from senweaver_oauth.source.pinterest import AuthPinterestSource
from senweaver_oauth.source.qq import AuthQqSource
from senweaver_oauth.source.renren import AuthRenrenSource
from senweaver_oauth.source.slack import AuthSlackSource
from senweaver_oauth.source.stack_overflow import AuthStackOverflowSource
from senweaver_oauth.source.taobao import AuthTaobaoSource
from senweaver_oauth.source.tencent_cloud import AuthTencentCloudSource
from senweaver_oauth.source.toutiao import AuthToutiaoSource
from senweaver_oauth.source.twitter import AuthTwitterSource
from senweaver_oauth.source.wechat import AuthWechatSource
from senweaver_oauth.source.wechat_enterprise import AuthWechatEnterpriseSource
from senweaver_oauth.source.wechat_mini import AuthWechatMiniSource
from senweaver_oauth.source.wechat_open import AuthWechatOpenSource
from senweaver_oauth.source.weibo import AuthWeiboSource
from senweaver_oauth.source.xmly import AuthXmlySource

__all__: List[str] = [
    "BaseAuthSource",
    "AuthAlipaySource",
    "AuthAliyunSource",
    "AuthAmazonSource",
    "AuthBaiduSource",
    "AuthCodingSource",
    "AuthDingtalkSource",
    "AuthDouyinSource",
    "AuthElemeSource",
    "AuthFacebookSource",
    "AuthFeishuSource",
    "AuthGiteeSource",
    "AuthGithubSource",
    "AuthGitlabSource",
    "AuthGoogleSource",
    "AuthHuaweiSource",
    "AuthJdSource",
    "AuthKujialeSource",
    "AuthLineSource",
    "AuthLinkedinSource",
    "AuthMeituanSource",
    "AuthMicrosoftSource",
    "AuthXiaomiSource",
    "AuthOschinaSource",
    "AuthPinterestSource",
    "AuthQqSource",
    "AuthRenrenSource",
    "AuthSlackSource",
    "AuthStackOverflowSource",
    "AuthTaobaoSource",
    "AuthTencentCloudSource",
    "AuthToutiaoSource",
    "AuthTwitterSource",
    "AuthWechatSource",
    "AuthWechatEnterpriseSource",
    "AuthWechatMiniSource",
    "AuthWechatOpenSource",
    "AuthWeiboSource",
    "AuthXmlySource",
] 