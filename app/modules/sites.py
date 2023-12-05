import fnmatch
import re
import sqlite3
import random
import requests
from bs4 import BeautifulSoup
from PyCookieCloud import PyCookieCloud
from app.utils.config import conf
from app.utils.sign_in_utils import is_sign_in_ok,get_default_headers, make_request, set_sign_in_status
from app.utils.logs import log_background_info, log_error_info
from app.utils.unittools import convert_large_size, convert_to_gb


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
                response = make_request(host, cookies, f'https://{host}/index.php', headers=None, data=None, method='GET')
                
        

                # 提取魔力值
                
                if host == 'zmpt.cc':
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 查找class为color_bonus的font标签
                    color_bonus_font = soup.find('font', class_='color_bonus')

                    if color_bonus_font:
                        label = color_bonus_font.text.strip()  # 获取标签内容
                        magic_value = color_bonus_font.find_next_sibling(string=True).strip()  # 获取电力值文本

                        print(f"{label}: {magic_value}")
                    else:
                        print("未找到匹配信息")
                else:
                    html_content =response.text
                    soup = BeautifulSoup(html_content, 'html.parser')
                    magic_value_tag = soup.find('font', class_='color_bonus')
                    magic_value_text = magic_value_tag.find_next('a').next_sibling.strip() if magic_value_tag else '未找到'
                    magic_value_match = re.search(r'\]:\s*([\d.,]+)', magic_value_text)

                    if magic_value_match:
                        magic_value = magic_value_match.group(1)
                        print('魔力值:', magic_value)
                    else:
                        print('未找到魔力值')



                # 提取分享率
                share_ratio_tag = soup.find('font', class_='color_ratio')
                share_ratio = share_ratio_tag.next_sibling.strip() if share_ratio_tag else '未找到'
                print('分享率:', share_ratio)

                # 提取上传量、下载量
                uploaded_tag = soup.find('font', class_='color_uploaded')
                downloaded_tag = soup.find('font', class_='color_downloaded')

                uploaded_amount = uploaded_tag.next_sibling.strip() if uploaded_tag else '未找到'
                downloaded_amount = downloaded_tag.next_sibling.strip() if downloaded_tag else '未找到'

                print('上传量:', uploaded_amount)
                print('下载量:', downloaded_amount)

                # 提取当前活动信息
                seeding_count_tag = soup.find('img', alt='Torrents seeding')

                seeding_count = seeding_count_tag.next_sibling.strip() if seeding_count_tag else '未找到'

                print('当前做种数:', seeding_count)
                
                
                # 提取用户名
                username_parent_tag = soup.find('span', class_='nowrap')
                username_tag = username_parent_tag.find('b') if username_parent_tag else None
                username = username_tag.text if username_tag else '未找到用户名'
                print('用户名:', username)


                # 提取链接
                link_tag = soup.find('span', class_='nowrap').find('a') if soup.find('span', class_='nowrap') else None
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else '未找到链接'
                print('链接:', link)

                # 使用正则表达式提取uid
                uid_match = re.search(r'id=(\d+)$', link)

                if uid_match:
                    user_id = uid_match.group(1)
                    print('用户uid:', user_id)
                else:
                    print('未找到用户uid')
                    
                
                
                
                
                # 提取做种体积

                headers = {
                    "Host": host,
                    "Cookie": cookies,
                    "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
                    "dnt": "1",
                    "sec-ch-ua-mobile": "?0",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "sec-ch-ua-platform": "\"macOS\"",
                    "accept": "*/*",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": f'https://{host}/userdetails.php?id={user_id}',
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "sec-gpc": "1",
                }
                
                print(f'https://{host}/userdetails.php?id={user_id}')
                
                url = f'https://{host}/getusertorrentlistajax.php?userid={user_id}&type=seeding'
                try:
                    response = requests.get(url, headers=headers)
                
                except requests.exceptions.RequestException as e:
                    log_error_info("请求异常: ", e)

                
                
                if fnmatch.fnmatch(host, '*.m-team.io'):
                    soup = BeautifulSoup(response.text, 'html.parser')

                    total_volume_gb = 0

                    for tr in soup.find_all('tr'):
                        size_tds = tr.find_all('td', class_='rowfollow', align='center')

                        # 检查是否至少有三个 <td> 元素
                        if len(size_tds) >= 3:
                            size_text = size_tds[0].get_text(strip=True)
                            # 提取数字和单位
                            size_match = re.search(r'([\d.]+)\s*([A-Za-z]+)', size_text)

                            if size_match:
                                size_value, size_unit = size_match.groups()
                                size_value = float(size_value)
                                total_volume_gb += convert_to_gb(size_value, size_unit)

                    size,unit = convert_large_size(total_volume_gb,'GB')
                    seeding_volume = f'{size} {unit}'
                    print(f'做种量{seeding_volume}')
                    
                elif host == 'pt.btschool.club':
                    
                    
                    headers = {
                        "Host": host,
                        "Cookie": cookies,
                        "cache-control": "max-age=0",
                        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"macOS\"",
                        "dnt": "1",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-user": "?1",
                        "sec-fetch-dest": "document",
                        "referer": "https://pt.btschool.club/",
                        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "sec-gpc": "1"
                    }
                    try:
                        response = requests.get(f'https://pt.btschool.club/userdetails.php?id={user_id}',headers = headers)
                    except requests.exceptions.RequestException as e:
                        log_error_info("请求异常: ", e)
                    
                    match_three = re.search(r'\((\d+)个种子，共计([\d.]+\s*[A-Za-z]+)\)', response.text)
                    if match_three:
                        seeding_volume = match_three.group(2)
                        print(f"Total Size: {seeding_volume}")
                else:
                    match = re.search(r'(?:总大小：|Total:)\s*([\d.]+)\s*([A-Za-z]+)', response.text)
                    match_two = re.search(r'(No record)', response.text)
                    


                    if match:
                        total_size_value = match.group(1)
                        total_size_unit = match.group(2)
                        seeding_volume = f'{total_size_value} {total_size_unit}'
                        print(f"Total Size: {total_size_value} {total_size_unit}")
                    elif match_two:
                        seeding_volume = 0
                        print(f"Total Size: {seeding_volume}")
                
                
                
                ## 获取用户等级
                
                url = f'https://{host}/userdetails.php?id={user_id}'
                
                headers = {
                    "Host": host,
                    "Cookie": cookies,
                    "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
                    "dnt": "1",
                    "sec-ch-ua-mobile": "?0",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "sec-ch-ua-platform": "\"macOS\"",
                    "accept": "*/*",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": f'https://{host}/index.php',
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "sec-gpc": "1",
                }
                
                try:
                    response = requests.get(url,headers=headers)
                    
                except requests.exceptions.RequestException as e:
                    log_error_info("请求异常: ", e)
                
                
                html_content =response.text

                soup = BeautifulSoup(html_content, 'html.parser')
                user_level_td = soup.find('td', text=re.compile(r'等级|等級|Class'))

                # 提取用户等级文本
                
                if user_level_td:
                    user_level = user_level_td.find_next('img')['alt']
                    print(f'用户等级：{user_level}')
                else:
                    print("未找到用户等级信息")
                
                
                try:
                    cursor.execute('''
                        INSERT INTO SiteStats (host, username, user_id, upload_amount, download_amount, share_ratio, magic_value, seeding_count, user_level, seeding_volume)
                        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        WHERE NOT EXISTS (SELECT 1 FROM SiteStats WHERE host = ?)
                    ''', (host, username, user_id, uploaded_amount, downloaded_amount, share_ratio, magic_value, seeding_count, user_level, seeding_volume, host))

                     
                     
                    conn.commit()
                    log_background_info("sites statics initialized. ")
                except Exception as e:
                    log_error_info("Error during init_statics",e)  
                    conn.rollback()



                

        except Exception as e:
            print(f"Error during init_statics: {str(e)}")

        finally:
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
    
    def sign_in(self):
        res = '*【签到通知】*\n'

        conn = sqlite3.connect('bot.db')
        
        
        cursor = conn.cursor()
        cursor.execute('SELECT host, name, cookies, sign_in_url, sign_in_status FROM Sites')
        sites = cursor.fetchall()
        conn.close()

        for site_info in sites:
            host, site_alias, cookies, sign_in_url, sign_in_status = site_info
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
                
            if(response.status_code == 200):
                set_sign_in_status(host, True)

        return res

        
sites = Sites(conf.cookiecloud_host, conf.cookiecloud_uuid, conf.cookiecloud_password)
sites.init_cookies()
sites.init_statics()




