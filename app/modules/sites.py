import fnmatch
import re
import sqlite3
import random
import requests
from bs4 import BeautifulSoup
from PyCookieCloud import PyCookieCloud
from app.utils.config import conf
from app.utils.sign_in_utils import is_sign_in_ok,get_default_headers, make_request, set_sign_in_status, get_site_info
from app.utils.logs import log_background_info, log_error_info
from app.utils.unittools import convert_large_size, convert_to_gb
from app.utils.user_info_statistics import get_user_level, get_user_name, get_user_id, get_share_ratio, get_upload_amount, get_download_amount, get_magic_value
from app.utils.user_info_statistics import get_seeding_volume

class Sites:
    def __init__(self, host, uuid, password):
        self.auto_sign_is_open = False
        self.cookie_cloud = PyCookieCloud(host, uuid, password)
       
    def init_cookies(self):
        try:
            decrypted_data = self.cookie_cloud.get_decrypted_data()
        except Exception as e:
                log_error_info("Error during get cookies from CookieCloud",e)
                
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:

            #cursor.execute('DELETE FROM Sites')

            for site, cookies in decrypted_data.items():
                cookie_string = ";".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                sign_in_url = self.get_sign_in_url(site)
                site_alias = self.get_site_alias(site)
                          
                cursor.execute('''
                    INSERT INTO Sites (host, name, cookies, sign_in_url)
                    SELECT ?, ?, ?, ?
                    WHERE NOT EXISTS (SELECT 1 FROM Sites WHERE host = ?)
                ''', (site, site_alias, cookie_string, sign_in_url, site))

            conn.commit()
            log_background_info("Cookies initialized. ")
            
        except Exception as e:
            conn.rollback()
            log_error_info("Error during sites cookies initialization",e)
            
        finally:
            conn.close()
    def init_statics(self):
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT host, cookies FROM Sites')
            sites_data = cursor.fetchall()
            
            cursor.execute('SELECT host FROM SiteStats' )
            sites_stats_data = cursor.fetchall()
        
            for host, cookies in sites_data:
                if (host,) in sites_stats_data:
                    continue;
                
                site_info = get_site_info(host, cookies)
                
                if site_info is not None:
                    magic_value, share_ratio, uploaded_amount, downloaded_amount, username, user_id, seeding_volume, user_level, passkey = site_info
                else:
                    print(f"{host} 更新站点信息失败")

                try:
                    cursor.execute('''
                        INSERT INTO SiteStats (host, username, user_id, upload_amount, download_amount, share_ratio, magic_value, user_level, seeding_volume, passkey)
                        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        WHERE NOT EXISTS (SELECT 1 FROM SiteStats WHERE host = ?)
                    ''', (host, username, user_id, uploaded_amount, downloaded_amount, share_ratio, magic_value, user_level, seeding_volume, passkey, host))
            
                    conn.commit()
                    log_background_info("sites statics initialized. ")
                except Exception as e:
                    log_error_info("Error during init_statics",e)  
                    conn.rollback()



                

        except Exception as e:
            print(f"Error during init_statics: {str(e)}")

        finally:
            conn.close()
    
    
    
    def update_and_show_site_info(self,hostname):
        res = ""
        conn = sqlite3.connect('bot.db')
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cookies, name FROM Sites WHERE host = ?
            ''', (hostname,))

        sites_cookies = cursor.fetchall()
        
        for tmp in sites_cookies:
            cookies, name  = tmp
            
            site_info = get_site_info(hostname, cookies)
                
            if site_info is not None:
                magic_value, share_ratio, uploaded_amount, downloaded_amount, username, user_id, seeding_volume, user_level,passkey = site_info
                
                res += f"*{name}*\n"
                res += f"账号名：{username}\n"
                res += f"用户ID：{user_id}\n"
                res += f"用户组：{user_level}\n"
                res += f"上传量：{uploaded_amount}\n"
                res += f"下载量：{downloaded_amount}\n"
                res += f"分享率：{share_ratio}\n"
                res += f"魔力值：{magic_value}\n"
                res += f"做种量：{seeding_volume}\n"
                
                try:
                    cursor.execute('''
                UPDATE SiteStats
                SET username=?, user_id=?, upload_amount=?, download_amount=?, share_ratio=?, magic_value=?, user_level=?, seeding_volume=?, passkey=?
                WHERE host=?
            ''', (username, user_id, uploaded_amount, downloaded_amount, share_ratio, magic_value, user_level, seeding_volume, passkey, hostname))
            
                    conn.commit()
                    log_background_info(f"{name} 站点统计信息更新成功")
                except Exception as e:
                    log_error_info("Error during init_statics",e)  
                    conn.rollback()
            else:
                log_background_info(f"{name} 站点统计信息更新失败")
                
                  
        conn.close()   
         
        return res
        
        
    def update_site_info(self):
        conn = sqlite3.connect('bot.db')
        
        cursor = conn.cursor()
        cursor.execute('SELECT host, cookies, name  FROM Sites')
        sites_cookies = cursor.fetchall()
        

        for tmp in sites_cookies:
            host, cookies, name  = tmp
            
            site_info = get_site_info(host, cookies)
                
            if site_info is not None:
                magic_value, share_ratio, uploaded_amount, downloaded_amount, username, user_id, seeding_volume, user_level = site_info
                
                try:
                    cursor.execute('''
                UPDATE SiteStats
                SET username=?, user_id=?, upload_amount=?, download_amount=?, share_ratio=?, magic_value=?, user_level=?, seeding_volume=?
                WHERE host=?
            ''', (username, user_id, uploaded_amount, downloaded_amount, share_ratio, magic_value, user_level, seeding_volume, host))
            
                    conn.commit()
                    log_background_info(f"{name} 站点统计信息自动更新成功")
                except Exception as e:
                    log_error_info("Error during init_statics",e)  
                    conn.rollback()
            else:
                log_background_info(f"{name} 站点统计信息更新失败")
            
        
        conn.close()    
        
        
        
    def update_cookies(self):
        decrypted_data = self.cookie_cloud.get_decrypted_data()
        if not decrypted_data:
            print('Failed to get decrypted data')
            return
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            for site, cookies in decrypted_data.items():
                    cookie_string = ";".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                    cursor.execute('''
                        UPDATE Sites
                        SET cookies = ?
                        WHERE host = ?
                    ''', (cookie_string, site))
        except Exception as e:
            conn.rollback()
            log_error_info("Error during sites cookies update",e)   
        finally:
            conn.close()
            log_background_info("Cookies自动更新：成功")
    
    def get_site_alias(self, site):
        patterns = {
            "*.m-team.io": "M-Team",
            "pt.btschool.club": "BTSCHOOL",
            "www.haidan.video": "海胆之家",
            "totheglory.im": "ToTheGlory",
            "monikadesign.uk": "MonikaDesign",
            "jptv.club": "JPTV",
            "www.torrentleech.org": "TorrentLeech",
            "u2.dmhy.org": "U2",
            "www.hddolby.com": "HD Dolby",
            "www.srvfi.top": "SRVFI",
            "hdfans.org": "HDFans",
            "pt.soulvoice.club": "聆音Club",
            "ubits.club": "UBits",
            "hdvideo.one": "HDVideo",
            "oldtoons.world": "Old Toons World",
            "rousi.zip": "Rousi",
            "zmpt.cc": "织梦",
            "ptchina.org": "铂金学院",
            "www.hdkyl.in": "HDKylin",
            "kamept.com": "KamePT",
            "hdhome.org": "HDHome",
            "leaves.red": "红叶"
        }

        for pattern, alias in patterns.items():
            if fnmatch.fnmatch(site, pattern):
                return alias

        return site
        
    def get_sign_in_url(self, site):
        patterns = {
            "*.m-team.io": "https://{}/index.php",
            "pt.btschool.club": "https://{}/index.php?action=addbonus",
            "www.haidan.video": "https://www.haidan.video/signin.php",
            "totheglory.im": "https://{}/signed.php",
            "monikadesign.uk": "https://{}/",
            "jptv.club": "https://{}/",
            "www.torrentleech.org": "https://{}/",
            "u2.dmhy.org": "https://{}/showup.php?action=show",
        }

        for pattern, url in patterns.items():
            if fnmatch.fnmatch(site, pattern):
                return url.format(site)

        return f'https://{site}/attendance.php'
    
    def statistics(self):
        res = '*【站点数据统计】*\n'
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT SiteStats.id, Sites.name, SiteStats.username, SiteStats.user_level,
               SiteStats.user_id, SiteStats.upload_amount, SiteStats.download_amount,
               SiteStats.share_ratio, SiteStats.magic_value, SiteStats.seeding_count,
               SiteStats.seeding_volume
        FROM SiteStats
        INNER JOIN Sites ON SiteStats.host = Sites.host
    ''')
        
        
        information = cursor.fetchall()
        conn.close()
        
        for info in information:
            id, site_name, username, user_level, user_id, upload_amount, download_amount, \
            share_ratio, magic_value, seeding_count, seeding_volume = info
            
            res += f"*{site_name}*({user_level})\n"
            res += f"上传量：{upload_amount}\n"
            res += f"下载量：{download_amount}\n"
            res += f"魔力值：{magic_value}\n"
            res+="------------\n"

        return res
        
        
    def sign_in(self):
        res = '*【签到通知】*\n'

        conn = sqlite3.connect('bot.db')
        
        
        cursor = conn.cursor()
        cursor.execute('SELECT host, name, cookies, sign_in_url, sign_in_status FROM Sites')
        sites = cursor.fetchall()
        conn.close()

        for site_info in sites:
            host, site_alias, cookies, sign_in_url, sign_in_status = site_info
            if host == 'leaves.red':
                continue;
            if(sign_in_status == True):
                log_background_info(f"{site_alias} 今日已签到")
                res += f"*{site_alias}* 今日已签到\n"
                continue
                
            print('开始进行签到' + sign_in_url)
            
            if host == "totheglory.im":
                response = make_request(host, cookies, 'https://totheglory.im/index.php', headers=None, data=None, method='GET')
                pattern = r'signed_timestamp:\s*"(\d+)",\s*signed_token:\s*"([a-f0-9]+)"'
                match = re.search(pattern, response.text)
                if match:
                    timestamp, token = match.groups()
                    data = {"signed_timestamp": timestamp, "signed_token": token}
                response = make_request(host, cookies, sign_in_url, headers=None, data=data, method='POST')
                res += is_sign_in_ok(site_alias, response)

            elif host == "u2.dmhy.org":
                response = make_request(host, cookies, 'https://u2.dmhy.org/showup.php', headers=get_default_headers(host, cookies), data=None, method='GET')
                match = re.search(r'<input type="hidden" name="req" value="([^"]+)" />\s*<input type="hidden" name="hash" value="([^"]+)" />\s*<input type="hidden" name="form" value="([^"]+)" />', response.text)
                if match:
                    req_value, hash_value, form_value = match.groups()
                else:
                    res += is_sign_in_ok(site_alias, None)
                    continue
                matches = re.findall(r'<input type="submit" name="([^"]+)" value="([^"]+)"', response.text)
                submit_values = [{"name": match[0], "value": match[1]} for match in matches]
                random_submit_value = random.choice(submit_values)
                data = {
                    "message": "签到咧签到咧签到咧签到咧签到咧签到咧签到咧签到咧签到咧签到咧", 
                    "req": req_value,
                    "hash": hash_value,
                    "form": form_value,
                    random_submit_value['name']: random_submit_value['value']
                }
                response = make_request(host, cookies, sign_in_url, headers=None, data=data, method='POST')
                res += is_sign_in_ok(site_alias, response)
            else:
                response = make_request(host, cookies, sign_in_url, headers=None, data=None, method='GET')
                res += is_sign_in_ok(site_alias, response)
                
            if response and response.status_code == 200: 
                set_sign_in_status(host, True)

        return res

        
sites = Sites(conf.cookiecloud_host, conf.cookiecloud_uuid, conf.cookiecloud_password)
sites.init_cookies()
sites.init_statics()







