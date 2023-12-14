from qbittorrentapi import Client
from qbittorrentapi.exceptions import NotFound404Error, APIConnectionError
from app.utils.config import conf
from app.utils.logs import log_error_info



class QBittorrentManager:
    def __init__(self):
        self.qb = Client(host=conf.qbittorrent_host, port=conf.qbittorrent_port, username=conf.qbittorrent_username, password=conf.qbittorrent_password)

    def _authenticate(self):
        self.qb.auth_log_in()

    def _logout(self):
        self.qb.auth_log_out()

    def _handle_api_errors(self, e):
        if isinstance(e, APIConnectionError):
            log_error_info("qBittorrent connection error", e)
        elif isinstance(e, NotFound404Error):
            log_error_info("qBittorrent API path not found", e)

    def speed_of_qb(self):
        try:
            self._authenticate()
            transfer_info = self.qb.transfer_info()

            total_upload_speed = self.format_speed(transfer_info['up_info_speed'])
            total_download_speed = self.format_speed(transfer_info['dl_info_speed'])

            result = f"\n上传速度: {total_upload_speed}\nTotal 下载速度: {total_download_speed}"
            return result
        except Exception as e:
            self._handle_api_errors(e)
        finally:
            self._logout()

    def pause_all_qb(self):
        try:
            self._authenticate()
            self.qb.torrents_pause("all")
            return "qBittorrent 任务暂停完成"
        except Exception as e:
            self._handle_api_errors(e)
        finally:
            self._logout()

    def resume_all_qb(self):
        try:
            self._authenticate()
            self.qb.torrents_resume("all")
            return "qBittorrent 任务恢复完成"
        except Exception as e:
            self._handle_api_errors(e)
        finally:
            self._logout()

    @staticmethod
    def format_speed(speed):
        if speed >= 1024 * 1024:
            return f"{speed / (1024 * 1024):.2f} MB/s"
        else:
            return f"{speed / 1024:.2f} KB/s"
        
        
    def add_torrent(self, download_link, save_path, category=None):
        try:
            # 构建添加种子的参数
            torrent_options = {
                'urls': download_link,
                'category': category,
                'save_path': save_path
            }

            # 发送添加种子请求
            self.qb.torrents_add(**torrent_options)

            print('Torrent added successfully!')
        except Exception as e:
            print(f'Error adding torrent: {e}')

        

qb = QBittorrentManager()