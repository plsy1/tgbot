import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

log_dir = 'logs'

# 获取当前项目根目录的绝对路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# 构建日志目录的绝对路径
log_dir_path = os.path.join(project_root, log_dir)

if not os.path.exists(log_dir_path):
    os.makedirs(log_dir_path)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 主日志文件
log_file = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8')
file_handler.setFormatter(log_formatter)

# 错误日志文件
error_log_file = f'logs/error_{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
error_file_handler = TimedRotatingFileHandler(error_log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8')
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(log_formatter)

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)

# Logger配置
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(error_file_handler)

def log_bot_received_message(message):
    logger.info(f"Received message from id {message.from_user.id} (username: {message.from_user.username}): {message.text}")

def log_bot_sent_message(message, send):
    logger.info(f"send message to id {message.from_user.id} (username: {message.from_user.username}): {send}")

def log_error_info(text, info):
    logger.error(f"{text}: {info}", exc_info=True)

def log_background_info(text):
    logger.info(f"Background Info: {text}")
