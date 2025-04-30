# SenWeaver OAuth FastAPI 示例

这是一个使用 FastAPI 和 SenWeaver OAuth 库构建的示例应用，演示了如何集成多个第三方 OAuth 平台进行用户认证。

## 功能特性

- 支持多个 OAuth 平台的集成（GitHub, Gitee, 微信, QQ, Google, 微博, 钉钉, Facebook等）
- 简洁美观的登录界面
- 用户信息展示

## 安装与配置

1. 克隆仓库并进入项目目录
2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 创建 `.env` 文件（可以从 `.env.example` 复制）:

```bash
cp .env.example .env
```

4. 编辑 `.env` 文件，填入您的 OAuth 应用的配置信息:

```
# 例如，GitHub OAuth配置
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/callback/github

# 其他平台类似...
```

## 获取平台 OAuth 应用配置

### GitHub
1. 访问 https://github.com/settings/developers
2. 创建一个新的 OAuth 应用，设置回调 URL 为 `http://localhost:8000/callback/github`

### Gitee
1. 访问 https://gitee.com/oauth/applications
2. 创建应用，设置回调 URL 为 `http://localhost:8000/callback/gitee`

### 微信开放平台
1. 访问 https://open.weixin.qq.com/
2. 创建应用并设置回调 URL 为 `http://localhost:8000/callback/wechat_open`

### 更多平台...
请参考各平台官方文档获取 OAuth 应用配置的详细步骤。

## 运行示例

启动 FastAPI 应用:

```bash
uvicorn app:app --reload
```

然后访问 http://localhost:8000 开始使用。

## 项目结构

- `app.py`: 主应用程序文件
- `templates/`: 包含 HTML 模板
  - `index.html`: 登录页面
  - `profile.html`: 用户信息页面
- `.env.example`: 环境变量示例文件

## 使用说明

1. 访问首页，选择要登录的平台
2. 点击相应平台的图标，跳转到授权页面
3. 授权成功后，会回调到应用并显示用户信息

## 注意事项

- 本示例仅用于演示目的，生产环境中需要添加适当的安全措施
- 某些平台（如微信）可能需要配置公网可访问的回调地址
- 建议使用 HTTPS 进行安全通信 