# 🚀 Heroku部署详细指南

本指南将帮助您通过GitHub将Telegram机器人部署到Heroku。

## 📋 前提条件

- [x] Heroku账号 (需要验证信用卡，即使使用免费额度)
- [x] GitHub账号和代码仓库
- [x] 从[@BotFather](https://t.me/botfather)获取的Telegram Bot Token

## 🎯 部署步骤

### 第1步: 创建Heroku应用

1. 登录 [Heroku Dashboard](https://dashboard.heroku.com)
2. 点击右上角 **"New"** → **"Create new app"**
3. 填写应用信息：
   - **App name**: 输入应用名称 (例如: `my-telegram-bot-123`)
   - **Choose a region**: 选择 `United States` 或 `Europe`
4. 点击 **"Create app"**

### 第2步: 连接GitHub仓库

1. 在新创建的应用页面，点击 **"Deploy"** 标签页
2. 在 **Deployment method** 部分选择 **"GitHub"**
3. 点击 **"Connect to GitHub"** 并授权Heroku访问
4. 在 **"repo-name"** 输入框中搜索 `heroku-telegram-bot`
5. 找到你的仓库后，点击 **"Connect"**

### 第3步: 配置环境变量

1. 点击 **"Settings"** 标签页
2. 在 **Config Vars** 部分点击 **"Reveal Config Vars"**
3. 添加以下环境变量：
   - **KEY**: `TELEGRAM_TOKEN`
   - **VALUE**: `你从@BotFather获取的机器人token`
4. 点击 **"Add"**

### 第4步: 添加Redis插件 (可选但推荐)

1. 点击 **"Resources"** 标签页
2. 在 **Add-ons** 搜索框中输入 `redis`
3. 选择 **"Heroku Redis"**
4. 选择计划：
   - **Mini ($3/月)**: 适合生产环境
   - 或搜索免费替代方案
5. 点击 **"Submit Order Form"**

> ⚠️ **注意**: Heroku Redis需要付费。如果不想付费，机器人仍可正常工作，只是不会保存用户统计数据。

### 第5步: 部署应用

1. 返回 **"Deploy"** 标签页
2. 滚动到 **Manual deploy** 部分
3. 确保选择了 `master` 或 `main` 分支
4. 点击 **"Deploy Branch"**
5. 等待部署完成（显示绿色的 "Your app was successfully deployed"）

### 第6步: 启动机器人

1. 在 **"Resources"** 标签页找到 **Free Dynos** 部分
2. 找到 `bot python bot.py` 这一行
3. 点击右侧的编辑按钮（铅笔图标）
4. 将滑块移动到右侧（ON位置）
5. 点击 **"Confirm"**

### 第7步: 验证部署

1. 点击 **"More"** → **"View logs"** 查看日志
2. 或者在 **"Activity"** 标签页查看部署历史
3. 在Telegram中搜索你的机器人并发送 `/start` 测试

## 🔧 配置自动部署 (可选)

1. 在 **"Deploy"** 标签页的 **Automatic deploys** 部分
2. 选择要部署的分支（通常是 `master` 或 `main`）
3. 可选择 **"Wait for CI to pass before deploy"**
4. 点击 **"Enable Automatic Deploys"**

现在每次推送代码到GitHub时，Heroku会自动重新部署！

## 📊 监控和管理

### 查看日志
```bash
# 通过Heroku CLI (如果已安装)
heroku logs --tail -a your-app-name
```

或在Dashboard的 **"More"** → **"View logs"**

### 重启应用
在 **"More"** → **"Restart all dynos"**

### 停止机器人
在 **"Resources"** 标签页将 `bot` dyno的滑块移到左侧（OFF）

## 💰 费用说明

- **应用托管**: 免费（有使用时间限制）
- **Heroku Redis**: $3/月起
- **自定义域名**: 免费
- **SSL证书**: 免费

## 🔍 故障排除

### 常见问题

1. **机器人没有响应**
   - 检查Config Vars中的TELEGRAM_TOKEN是否正确
   - 确认bot dyno已启动
   - 查看日志是否有错误

2. **部署失败**
   - 检查requirements.txt是否正确
   - 确认runtime.txt中的Python版本受支持
   - 查看Activity标签页的构建日志

3. **Redis连接失败**
   - 确认已添加Heroku Redis插件
   - 检查Config Vars中是否有REDIS_URL

### 有用的命令

```bash
# 查看应用信息
heroku apps:info -a your-app-name

# 查看配置变量
heroku config -a your-app-name

# 重启应用
heroku ps:restart -a your-app-name

# 查看插件
heroku addons -a your-app-name
```

## 🎉 完成！

恭喜！你的Telegram机器人现在已经在Heroku上运行了。机器人将24/7在线，除非你停止dyno或超出免费额度。

有任何问题，可以查看Heroku的官方文档或在GitHub Issues中提问。