#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信小程序登录示例
"""
import os
from dotenv import load_dotenv

from senweaver_oauth.config import AuthConfig
from senweaver_oauth.source.wechat_mini import AuthWechatMiniSource

# 加载环境变量
load_dotenv()

def main():
    """
    微信小程序登录示例
    """
    # 初始化配置
    config = AuthConfig(
        client_id=os.getenv("WECHAT_MINI_CLIENT_ID", ""),
        client_secret=os.getenv("WECHAT_MINI_CLIENT_SECRET", ""),
    )
    
    # 初始化微信小程序登录源
    auth_source = AuthWechatMiniSource(config)
    
    # 模拟小程序端传来的code
    js_code = input("请输入微信小程序登录获取的code: ")
    
    # 使用code获取session_key和openid
    token_response = auth_source.code_to_session(js_code)
    
    if token_response.code != 200:
        print(f"获取session_key失败: {token_response.message}")
        return
    
    print(f"获取session_key成功: {token_response.data}")
    
    # 由于获取用户信息需要前端传入加密数据和iv，这里仅做演示
    print("\n要解密用户信息，需要小程序端调用 wx.getUserInfo 并传入:")
    print("- encryptedData: 加密的用户数据")
    print("- iv: 加密算法的初始向量")
    
    # 模拟解密用户信息
    # 以下代码在实际使用中需要前端传入真实的加密数据和iv
    print("\n以下是解密用户信息的示例代码:")
    print("encrypted_data = request.json.get('encryptedData')")
    print("iv = request.json.get('iv')")
    print("user_response = auth_source.decrypt_user_info(token_response.data, encrypted_data, iv)")
    print("if user_response.code == 200:")
    print("    user_info = user_response.data")
    print("    print(f'用户信息: {user_info}')")
    
   

if __name__ == "__main__":
    main() 