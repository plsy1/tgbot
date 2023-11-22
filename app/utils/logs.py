import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os, sys

log_dir = 'logs'

if getattr(sys, 'frozen', False):  # 检查是否是打包后的运行环境
    
    project_root = os.path.dirname(sys.argv[0])
    print(f"Running in frozen environment. Config file path: {project_root}")

else:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
log_dir_path = os.path.join(project_root, log_dir)

if not os.path.exists(log_dir_path):
    os.makedirs(log_dir_path)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 主日志文件
# log_file = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
log_file = os.path.join(log_dir_path, f'{datetime.datetime.now().strftime("%Y-%m-%d")}.log')

file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8')
file_handler.setFormatter(log_formatter)

# 错误日志文件
# error_log_file = f'logs/error_{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
error_log_file = os.path.join(log_dir_path, f'error_{datetime.datetime.now().strftime("%Y-%m-%d")}.log')

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
