# -*- coding: utf-8 -*-
import redis
import os
import telebot
import logging
import time
import urllib.parse

# Load environment variables from .env file for local development (only if file exists)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in production, skip
    pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config vars - Get from environment variables
token = os.environ.get('TELEGRAM_TOKEN')
if not token:
    logger.error("TELEGRAM_TOKEN environment variable is not set!")
    exit(1)

# Redis configuration
redis_client = None
redis_available = False

try:
    redis_url = os.getenv('REDIS_URL')
    logger.info(f"Redis URL found: {'Yes' if redis_url else 'No'}")
    
    if redis_url:
        logger.info(f"Redis URL type: {'SSL' if 'rediss://' in redis_url else 'Standard'}")
        
        # For Heroku Redis, we need SSL and longer timeouts
        if 'rediss://' in redis_url:
            # Heroku Redis uses SSL
            redis_client = redis.from_url(
                redis_url, 
                decode_responses=True,
                socket_timeout=30,
                socket_connect_timeout=30,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
                retry_on_timeout=True
            )
        else:
            # Standard Redis connection
            redis_client = redis.from_url(
                redis_url, 
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=10,
                retry_on_timeout=True
            )
        
        # Test connection with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                redis_client.ping()
                redis_available = True
                logging.info(f"Redis connected successfully (attempt {attempt + 1})")
                break
            except redis.ConnectionError as e:
                logging.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    redis_client = None
                    redis_available = False
                else:
                    time.sleep(2)  # Wait before retry
        
        if redis_available:
            # Test write operation
            try:
                redis_client.set('test_connection', 'ok', ex=60)
                test_value = redis_client.get('test_connection')
                if test_value == 'ok':
                    logging.info("Redis read/write test successful")
                    # 测试基本数据操作
                    redis_client.set('bot_status', 'online', ex=3600)
                    logging.info("Redis bot status set successfully")
                else:
                    logging.warning("Redis read test failed")
            except Exception as e:
                logging.warning(f"Redis read/write test failed: {e}")
    else:
        logging.warning("REDIS_URL not found in environment variables")
        
except ImportError:
    logging.error("Redis module not found. Install with: pip install redis")
except Exception as e:
    logging.error(f"Redis connection error: {e}")
    redis_client = None
    redis_available = False

# Initialize bot
bot = telebot.TeleBot(token)

# Bot command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle /start command"""
    welcome_text = """
👋 欢迎使用我们的Telegram机器人！

🔧 基础功能:
/start - 显示此欢迎消息
/help - 获取帮助信息  
/info - 查看机器人信息
/echo [消息] - 回显你的消息

🎯 实用工具:
/weather [城市] - 查看天气信息
/translate [文本] - 翻译文本
/qr [文本] - 生成二维码
/short [链接] - 缩短URL链接

🎲 娱乐功能:
/joke - 随机笑话
/roll - 掷骰子
/coin - 抛硬币
/random [数字] - 生成随机数

📊 用户功能:
/stats - 查看个人统计
/feedback [内容] - 发送反馈

直接发送任何消息，我会智能回复你！
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Handle /help command"""
    help_text = """
🤖 机器人功能帮助

📋 基础命令:
• /start - 开始使用机器人
• /help - 显示此帮助信息
• /info - 查看机器人信息
• /echo [消息] - 回显你发送的消息

� 实用工具:
• /weather [城市名] - 查看指定城市天气
• /translate [文本] - 翻译文本(自动检测语言)
• /qr [文本] - 为文本生成二维码
• /short [URL] - 缩短长链接

🎮 娱乐功能:
• /joke - 获取随机笑话
• /roll - 掷一个六面骰子
• /coin - 抛硬币(正面/反面)
• /random [最大值] - 生成1到指定数字的随机数

📈 个人功能:
• /stats - 查看你的使用统计
• /feedback [内容] - 向开发者发送反馈

�💡 使用技巧:
- 直接发送消息进行智能对话
- 发送图片、文档等媒体文件
- 支持群组聊天和私聊
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['echo'])
def echo_message(message):
    """Handle /echo command"""
    # Extract message after /echo command
    text = message.text[6:].strip()  # Remove '/echo ' from beginning
    if text:
        bot.reply_to(message, f"🔄 你说: {text}")
    else:
        bot.reply_to(message, "请在/echo后面添加要回显的消息")

@bot.message_handler(commands=['info'])
def send_info(message):
    """Handle /info command"""
    user_count = 0
    redis_status = "❌ 未连接"
    redis_details = ""
    redis_error_info = ""
    
    # 获取环境变量状态
    redis_url = os.getenv('REDIS_URL')
    redis_url_status = "✅ 已设置" if redis_url else "❌ 未设置"
    
    if redis_url:
        redis_details += f"\n🔗 Redis URL前缀: {redis_url[:30]}..."
    
    if redis_available and redis_client:
        try:
            # 测试Redis连接
            ping_result = redis_client.ping()
            if ping_result:
                redis_status = "✅ 已连接"
                
                # 获取用户数量
                try:
                    user_count = redis_client.scard('bot_users') or 0
                    redis_client.sadd('bot_users', message.from_user.id)
                except Exception as e:
                    redis_details += f"\n⚠️ 用户数据读取错误: {str(e)[:50]}"
                
                # 获取Redis信息
                try:
                    redis_info = redis_client.info()
                    redis_version = redis_info.get('redis_version', 'unknown')
                    memory_used = redis_info.get('used_memory_human', 'unknown')
                    connected_clients = redis_info.get('connected_clients', 'unknown')
                    redis_details += f"\n📊 Redis版本: {redis_version}"
                    redis_details += f"\n💾 内存使用: {memory_used}"
                    redis_details += f"\n👥 连接数: {connected_clients}"
                except Exception as e:
                    redis_details += f"\n⚠️ Redis信息获取失败: {str(e)[:50]}"
                    
        except redis.ConnectionError as e:
            redis_status = "❌ 连接失败"
            redis_error_info = f"\n🔍 连接错误: {str(e)[:100]}"
        except redis.TimeoutError as e:
            redis_status = "❌ 连接超时"
            redis_error_info = f"\n🔍 超时错误: {str(e)[:100]}"
        except Exception as e:
            redis_status = "❌ 未知错误"
            redis_error_info = f"\n🔍 错误详情: {str(e)[:100]}"
    elif redis_url:
        redis_status = "❌ 初始化失败"
        redis_error_info = "\n🔍 Redis客户端初始化失败，检查启动日志"
    
    info_text = f"""
ℹ️ 机器人信息

• 版本: 2.0
• 运行环境: Heroku/Cloud  
• Python版本: 3.11+
• 用户数量: {user_count}
• Redis状态: {redis_status}
• 环境变量: {redis_url_status}{redis_details}{redis_error_info}

Bot ID: @{bot.get_me().username}
    """
    bot.reply_to(message, info_text)

@bot.message_handler(commands=['weather'])
def get_weather(message):
    """Handle /weather command"""
    city = message.text[9:].strip()  # Remove '/weather ' from beginning
    if city:
        # 这里可以集成真实的天气API，现在返回模拟数据
        weather_info = f"""
🌤 {city} 天气信息

🌡 温度: 22°C
💨 风速: 5 km/h
💧 湿度: 65%
☁️ 天气: 多云
🌅 日出: 06:30
🌇 日落: 18:45

💡 提示: 这是演示数据，可集成真实天气API
        """
        bot.reply_to(message, weather_info)
    else:
        bot.reply_to(message, "请输入城市名称，例如: /weather 北京")

@bot.message_handler(commands=['translate'])
def translate_text(message):
    """Handle /translate command"""
    text = message.text[11:].strip()  # Remove '/translate ' from beginning
    if text:
        # 简单的翻译演示 - 可以集成Google Translate API或其他翻译服务
        if any(ord(char) > 127 for char in text):  # 包含非ASCII字符（可能是中文）
            translated = f"English translation of '{text}' would appear here"
        else:
            translated = f"'{text}' 的中文翻译将显示在这里"
        
        result = f"""
🌐 翻译结果

原文: {text}
译文: {translated}

💡 提示: 这是演示功能，可集成真实翻译API
        """
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "请输入要翻译的文本，例如: /translate Hello World")

@bot.message_handler(commands=['qr'])
def generate_qr(message):
    """Handle /qr command"""
    text = message.text[4:].strip()  # Remove '/qr ' from beginning
    if text:
        qr_info = f"""
📱 二维码生成

内容: {text}
🔗 二维码链接: https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text.replace(' ', '%20')}

💡 提示: 点击链接查看或下载二维码图片
        """
        bot.reply_to(message, qr_info)
    else:
        bot.reply_to(message, "请输入要生成二维码的内容，例如: /qr https://example.com")

@bot.message_handler(commands=['short'])
def shorten_url(message):
    """Handle /short command"""
    url = message.text[7:].strip()  # Remove '/short ' from beginning
    if url:
        # 模拟URL缩短功能
        import hashlib
        short_code = hashlib.md5(url.encode()).hexdigest()[:8]
        short_url = f"https://short.ly/{short_code}"
        
        result = f"""
🔗 链接缩短

原链接: {url}
短链接: {short_url}

💡 提示: 这是演示功能，可集成真实短链接服务
        """
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "请输入要缩短的URL，例如: /short https://www.example.com/very/long/url")

@bot.message_handler(commands=['joke'])
def tell_joke(message):
    """Handle /joke command"""
    jokes = [
        "为什么程序员喜欢黑暗？因为光亮会产生bug！ 😄",
        "什么是程序员最喜欢的歌？Hello World！ 🎵",
        "为什么Python这么受欢迎？因为它很好养！ 🐍",
        "程序员的三大谎言：这只是临时的，明天就写注释，这个bug很容易修复。 😅",
        "什么是最短的编程笑话？Java。 ☕",
        "为什么程序员总是搞混圣诞节和万圣节？因为 Oct 31 == Dec 25！ 🎃🎄",
        "程序员去酒吧，要了1024杯啤酒。服务员问：为什么不要1000杯？程序员：我只要整数杯！ 🍺"
    ]
    
    import random
    joke = random.choice(jokes)
    bot.reply_to(message, f"😄 随机笑话\n\n{joke}")

@bot.message_handler(commands=['roll'])
def roll_dice(message):
    """Handle /roll command"""
    import random
    result = random.randint(1, 6)
    dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    
    bot.reply_to(message, f"🎲 掷骰子结果: {dice_faces[result-1]} ({result})")

@bot.message_handler(commands=['coin'])
def flip_coin(message):
    """Handle /coin command"""
    import random
    result = random.choice(["正面 🪙", "反面 🔄"])
    bot.reply_to(message, f"🪙 抛硬币结果: {result}")

@bot.message_handler(commands=['random'])
def generate_random(message):
    """Handle /random command"""
    try:
        max_num = message.text[8:].strip()  # Remove '/random ' from beginning
        if max_num and max_num.isdigit():
            import random
            result = random.randint(1, int(max_num))
            bot.reply_to(message, f"🎲 随机数结果: {result} (1-{max_num})")
        else:
            import random
            result = random.randint(1, 100)
            bot.reply_to(message, f"🎲 随机数结果: {result} (1-100)")
    except:
        bot.reply_to(message, "请输入有效数字，例如: /random 50")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Handle /stats command"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "用户"
    
    # 获取用户统计信息
    message_count = 0
    join_date = "未知"
    
    if redis_available and redis_client:
        try:
            message_count = redis_client.get(f"user:{user_id}:messages") or 0
            join_date_timestamp = redis_client.get(f"user:{user_id}:join_date")
            if not join_date_timestamp:
                # 首次使用，记录加入日期
                from datetime import datetime
                join_date = datetime.now().strftime("%Y-%m-%d")
                redis_client.set(f"user:{user_id}:join_date", join_date)
            else:
                join_date = join_date_timestamp.decode() if isinstance(join_date_timestamp, bytes) else join_date_timestamp
        except Exception as e:
            logger.warning(f"Redis stats operation failed: {e}")
    
    stats_text = f"""
📊 {user_name} 的使用统计

👤 用户ID: {user_id}
📅 加入日期: {join_date}
💬 发送消息数: {message_count}
🤖 机器人版本: 2.0

💡 继续使用来增加你的统计数据！
    """
    bot.reply_to(message, stats_text)

@bot.message_handler(commands=['feedback'])
def handle_feedback(message):
    """Handle /feedback command"""
    feedback = message.text[10:].strip()  # Remove '/feedback ' from beginning
    if feedback:
        # 这里可以将反馈保存到数据库或发送给管理员
        if redis_available and redis_client:
            try:
                import time
                feedback_key = f"feedback:{int(time.time())}:{message.from_user.id}"
                feedback_data = f"User: {message.from_user.first_name} ({message.from_user.id})\nFeedback: {feedback}"
                redis_client.set(feedback_key, feedback_data)
                logger.info(f"Feedback saved: {feedback_key}")
            except Exception as e:
                logger.warning(f"Failed to save feedback: {e}")
        
        response = """
📝 反馈已收到！

感谢您的宝贵意见和建议！
我们会认真考虑您的反馈，持续改进机器人功能。

如有紧急问题，请直接联系管理员。
        """
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "请输入您的反馈内容，例如: /feedback 建议增加更多功能")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages"""
    user_name = message.from_user.first_name or "朋友"
    
    # Store user interaction in Redis if available
    if redis_available and redis_client:
        try:
            redis_client.sadd("bot_users", message.from_user.id)
            redis_client.incr(f"user:{message.from_user.id}:messages")
        except Exception as e:
            logger.warning(f"Failed to update user stats: {e}")
    
    # Enhanced message processing based on content
    text = message.text.lower() if message.text else ""
    
    # 问候语处理
    if any(word in text for word in ['你好', 'hello', 'hi', '嗨', '早上好', '下午好', '晚上好']):
        greetings = [
            f"你好，{user_name}！很高兴见到你！ 😊",
            f"嗨，{user_name}！今天过得怎么样？ 🌟",
            f"你好呀，{user_name}！有什么我可以帮助你的吗？ 💫"
        ]
        import random
        response = random.choice(greetings)
    
    # 感谢语处理
    elif any(word in text for word in ['谢谢', 'thanks', 'thank you', '感谢']):
        thanks_replies = [
            f"不客气，{user_name}！很乐意为你服务！ 🤝",
            f"不用谢，{user_name}！这是我应该做的！ 😊",
            f"很高兴能帮到你，{user_name}！ ✨"
        ]
        import random
        response = random.choice(thanks_replies)
    
    # 告别语处理
    elif any(word in text for word in ['再见', 'bye', 'goodbye', '拜拜', '晚安']):
        farewells = [
            f"再见，{user_name}！期待下次见面！ 👋",
            f"拜拜，{user_name}！记得常来聊天哦！ 🌈",
            f"晚安，{user_name}！祝你好梦！ 🌙"
        ]
        import random
        response = random.choice(farewells)
    
    # 时间相关查询
    elif any(word in text for word in ['时间', 'time', '几点', '现在']):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weekday = datetime.now().strftime("%A")
        weekday_cn = {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三", 
                     "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"}
        response = f"⏰ 当前时间是: {current_time}\n📅 今天是{weekday_cn.get(weekday, weekday)}"
    
    # 天气相关
    elif any(word in text for word in ['天气', 'weather', '下雨', '晴天']):
        response = f"想查看天气吗，{user_name}？试试发送 /weather [城市名] 来获取天气信息！ 🌤"
    
    # 功能询问
    elif any(word in text for word in ['功能', '能做什么', '帮助', 'help', '命令']):
        response = f"我有很多功能哦，{user_name}！发送 /help 查看完整的功能列表，或者 /start 看看我能为你做什么！ 🤖"
    
    # 娱乐相关
    elif any(word in text for word in ['笑话', 'joke', '无聊', '好玩']):
        response = f"想听笑话吗，{user_name}？试试 /joke 来获取随机笑话！或者 /roll 掷个骰子玩玩！ 🎲😄"
    
    # 情感支持
    elif any(word in text for word in ['累了', '难过', '开心', '高兴', '伤心']):
        if any(word in text for word in ['累了', '难过', '伤心']):
            response = f"听起来你可能需要放松一下，{user_name}。要不要听个笑话让心情好一些？发送 /joke 试试看！ 🌈"
        else:
            response = f"很高兴听到你心情不错，{user_name}！继续保持这种积极的态度！ ✨"
    
    # 赞美机器人
    elif any(word in text for word in ['聪明', '棒', '厉害', '不错', 'good', 'great', 'awesome']):
        compliment_replies = [
            f"谢谢夸奖，{user_name}！我会继续努力的！ 😊",
            f"你的认可是我最大的动力，{user_name}！ ⭐",
            f"嘿嘿，被你这么一夸我都不好意思了，{user_name}！ 😄"
        ]
        import random
        response = random.choice(compliment_replies)
    
    # 询问机器人信息
    elif any(word in text for word in ['你是谁', '什么机器人', '介绍']):
        response = f"我是一个多功能的Telegram机器人，{user_name}！我可以聊天、提供实用工具、娱乐功能等。发送 /start 了解更多！ 🤖"
    
    # 默认随机回复
    else:
        responses = [
            f"收到你的消息了，{user_name}！ 📝",
            f"谢谢你的消息，{user_name}！💬",
            f"我听到了，{user_name}！有什么我可以帮助你的吗？ 🤔",
            f"很有趣的消息，{user_name}！ ✨",
            f"继续聊天吧，{user_name}！我很喜欢和你交流！ 💫",
            f"说得不错，{user_name}！还有什么想聊的吗？ 🌟"
        ]
        import random
        response = random.choice(responses)
    
    bot.reply_to(message, response)

# Error handler
@bot.message_handler(func=lambda message: True, content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    """Handle media messages"""
    media_types = {
        'photo': '📷 照片',
        'document': '📄 文档', 
        'audio': '🎵 音频',
        'video': '🎥 视频',
        'voice': '🎤 语音'
    }
    
    media_type = media_types.get(message.content_type, '📎 媒体文件')
    bot.reply_to(message, f"收到你发送的{media_type}！感谢分享！")

if __name__ == "__main__":
    logger.info("Starting Telegram Bot...")
    logger.info(f"Redis available: {redis_available}")
    logger.info(f"Redis URL configured: {'Yes' if os.getenv('REDIS_URL') else 'No'}")
    
    try:
        # Start polling
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
