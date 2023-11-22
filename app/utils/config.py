import configparser
import os,sys

class ConfigManager:
    def __init__(self, config_file_path=None):
        if config_file_path is None:
            
            if config_file_path is None:
                if getattr(sys, 'frozen', False):  # 检查是否是打包后的运行环境
                    binary_dir = os.path.dirname(sys.argv[0])
                    config_file_path = os.path.join(binary_dir, 'config.ini')
                else:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    config_file_path = os.path.join(current_dir, '../../conf/config.ini')

        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

        # 获取Telegram部分的配置
        self.telegram_token = self.config['Telegram']['TOKEN']
        self.chat_id = self.config['Telegram']['CHAT_ID']

        # 获取qBittorrent部分的配置
        self.qbittorrent_host = self.config['qBittorrent']['HOST']
        self.qbittorrent_port = self.config['qBittorrent']['PORT']
        self.qbittorrent_username = self.config['qBittorrent']['USERNAME']
        self.qbittorrent_password = self.config['qBittorrent']['PASSWORD']

        # 获取Transmission部分的配置
        self.transmission_host = self.config['Transmission']['HOST']
        self.transmission_port = self.config['Transmission']['PORT']
        self.transmission_username = self.config['Transmission']['USERNAME']
        self.transmission_password = self.config['Transmission']['PASSWORD']

        # 获取CookieCloud部分的配置
        self.cookiecloud_host = self.config['CookieCloud']['COOKIECLOUD_HOST']
        self.cookiecloud_uuid = self.config['CookieCloud']['COOKIECLOUD_UUID']
        self.cookiecloud_password = self.config['CookieCloud']['COOKIECLOUD_PASSWORD']
        self.cookiecloud_interval = self.config['CookieCloud']['COOKIECLOUD_INTERVAL']
        
        # 获取站点相关设置
        self.auto_signin_interval = self.config['Schedule']['AUTO_SIGININ_TIME']


conf = ConfigManager()

