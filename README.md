# 📱 Telegram Bot - 现代化版本

这是一个经过现代化改进的Telegram机器人项目，支持多平台部署。

## ⚠️ 重要说明

从2022年11月28日起，Heroku不再提供免费服务。本项目已更新以支持多种替代部署方案：

- 🎓 [GitHub学生开发包](https://education.github.com/pack) - 免费云服务
- � [Railway](https://railway.app) - Heroku最佳替代品  
- 🔵 [Render](https://render.com) - 免费层可用
- � [Heroku](https://heroku.com) - 付费但稳定可靠

## ✨ 功能特性

- 🤖 完整的Telegram机器人实现
- 💾 Redis数据持久化支持
- 🔧 环境变量配置
- 📝 详细日志记录  
- 🎯 多种消息处理
- 🌐 多平台云部署支持

## 🚀 快速开始

### 准备工作

1. 通过 [@BotFather](https://t.me/botfather) 创建Telegram机器人并获取token
2. Fork此项目到你的GitHub账号
3. 选择下面的部署方式之一

## 📦 部署选项

### Option 1: Railway部署 (推荐)

1. 访问 [Railway](https://railway.app)
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你fork的仓库
5. 在Variables中设置 `TELEGRAM_TOKEN=你的机器人token`
6. 自动部署完成！

### Option 2: Render部署

1. 访问 [Render](https://render.com)
2. 创建新的Web Service
3. 连接GitHub仓库
4. 在Environment Variables中设置:
   - `TELEGRAM_TOKEN=你的机器人token`
5. 点击Deploy

### Option 3: Heroku部署 (付费)

#### 方法A: GitHub自动部署 (推荐)

1. **创建Heroku应用**
   - 登录 [Heroku Dashboard](https://dashboard.heroku.com)
   - 点击 "New" → "Create new app"
   - 填写应用名称，选择区域

2. **连接GitHub仓库**
   - 在Deploy标签页选择 "GitHub"
   - 搜索并连接你的仓库
   - 可选择开启"Automatic deploys"

3. **配置环境变量**
   - 进入Settings标签页
   - 点击 "Reveal Config Vars"
   - 添加：`TELEGRAM_TOKEN` = `你的机器人token`

4. **添加Redis插件 (可选但推荐)**
   - 在Resources标签页搜索 "Heroku Redis"
   - 选择 "Heroku Redis" 并点击 "Submit Order Form"
   - Redis URL会自动添加到Config Vars中

5. **启动机器人**
   - 在Resources标签页找到 "bot" dyno
   - 点击编辑按钮，将滑块移到右侧启用
   - 点击 "Confirm"

#### 方法B: CLI部署

```bash
# 安装Heroku CLI
heroku login
heroku create your-app-name

# 添加Redis插件
heroku addons:create heroku-redis:mini -a your-app-name

# 设置环境变量
heroku config:set TELEGRAM_TOKEN=你的机器人token

# 部署
git push heroku main
heroku ps:scale bot=1

# 查看日志
heroku logs --tail
```

## 🔧 配置说明

### 云平台环境变量

#### 必需配置
- `TELEGRAM_TOKEN`: 从@BotFather获取的机器人token

#### 可选配置  
- `REDIS_URL`: Redis数据库连接URL (Heroku Redis会自动提供)

## 🤖 机器人功能

### 🔧 基础功能
- `/start` - 欢迎消息和功能介绍
- `/help` - 详细帮助信息
- `/info` - 查看机器人状态信息  
- `/echo [消息]` - 回显用户消息

### 🛠 实用工具  
- `/weather [城市]` - 查看天气信息
- `/translate [文本]` - 翻译文本(支持中英文)
- `/qr [文本]` - 生成二维码
- `/short [链接]` - 缩短URL链接

### 🎮 娱乐功能
- `/joke` - 随机程序员笑话
- `/roll` - 掷骰子(1-6)
- `/coin` - 抛硬币(正面/反面)
- `/random [数字]` - 生成随机数

### 📊 个人功能
- `/stats` - 查看个人使用统计
- `/feedback [内容]` - 发送用户反馈

### 🧠 智能对话
- **关键词识别**: 问候、感谢、告别等智能回复
- **情感支持**: 根据情绪关键词提供相应回复  
- **功能引导**: 自动推荐相关功能
- **媒体处理**: 支持图片、文档、音频、视频等文件

## 📁 项目结构

```
heroku-telegram-bot/
├── bot.py              # 主要机器人代码 (466行)
├── requirements.txt    # Python依赖包
├── runtime.txt        # Python版本指定
├── Procfile          # 进程配置文件
├── .env.example      # 环境变量模板
├── .gitignore        # Git忽略文件
├── HEROKU_DEPLOY.md  # Heroku部署详细指南
├── FEATURES.md       # 功能演示和使用说明
├── README.md         # 项目说明
└── LICENSE           # 许可证
```

## 🔒 安全提示

- ⚠️ **永远不要**在代码中硬编码机器人token
- ✅ 使用云平台的Config Vars/Environment Variables
- 🛡️ 定期更新依赖包以修复安全漏洞  
- 🔐 保护好你的机器人token，不要分享给他人

## 🤝 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📝 更新日志

### v2.0 (2024)
- 🆙 更新Python版本至3.11
- 📦 更新所有依赖包
- 🎯 完善机器人功能
- 🌐 添加多平台部署支持
- 📚 改进文档

### v1.0 (原版)
- 🤖 基础Telegram机器人模板
- 🏠 Heroku部署支持

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 获取帮助

- 📖 [Telegram Bot API文档](https://core.telegram.org/bots/api)
- 💬 [PyTelegramBotAPI文档](https://pypi.org/project/pyTelegramBotAPI/)
- 🐛 遇到问题？请提交Issue

---

**⭐ 如果这个项目对你有帮助，请给它一个star！**