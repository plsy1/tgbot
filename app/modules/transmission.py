from transmission_rpc import Client as TRClient
from app.utils.config import conf
from app.utils.logs import log_error_info

class TransmissionManager:
    def __init__(self):
        self.tr = TRClient(host=conf.transmission_host, port=conf.transmission_port, username=conf.transmission_username, password=conf.transmission_password)

    def _handle_connection_error(self, e):
        log_error_info("Transmission connection error", e)

    def speed_of_tr(self):
        try:
            session_stats = self.tr.session_stats()

            total_upload_speed = self.format_speed(session_stats.upload_speed)
            total_download_speed = self.format_speed(session_stats.download_speed)

            result = f"\nTotal 上传速度: {total_upload_speed}\nTotal 下载速度: {total_download_speed}"
            return result
        except Exception as e:
            self._handle_connection_error(e)

    def pause_all_tr(self):
        try:
            torrents = self.tr.get_torrents()
            torrent_ids = [torrent.id for torrent in torrents]
            self.tr.stop_torrent(torrent_ids)
            return "Transmission 任务暂停完成"
        except Exception as e:
            self._handle_connection_error(e)

    def resume_all_tr(self):
        try:
            self.tr.start_all()
            return "Transmission 任务恢复完成"
        except Exception as e:
            self._handle_connection_error(e)

    @staticmethod
    def format_speed(speed):
        if speed >= 1024 * 1024:
            return f"{speed / (1024 * 1024):.2f} MB/s"
        else:
            return f"{speed / 1024:.2f} KB/s"
        
tr = TransmissionManager()                