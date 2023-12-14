import requests, sqlite3
from requests.exceptions import Timeout
from app.utils.logs import log_error_info, log_background_info
from app.utils.user_info_statistics import get_user_level, get_user_name, get_user_id, get_share_ratio, get_upload_amount, get_download_amount, get_magic_value
from app.utils.user_info_statistics import get_seeding_volume, get_seeding_volume_ttg, get_passkey



def make_request(host, cookies, url, headers=None, data=None, method='GET'):
    # 检查是否提供了自定义headers，如果没有，则使用默认headers
    headers = headers if headers is not None else get_default_headers(host, cookies)
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=data, timeout=10)
        else:
            log_error_info("不支持的请求方法: ", method)
            return None

        response.raise_for_status()
        return response
    except Timeout:
        log_error_info("请求超时: ", url)
        return None
    except requests.exceptions.RequestException as e:
        log_error_info("请求异常: ", e)
        return None
def is_sign_in_ok(host,resnpose):
    if resnpose == None:
        return f"*{host}* 签到失败！！！\n"
    if resnpose.status_code == 200:
        return f"*{host}* 签到成功\n"
    else:
        return f"*{host}* 签到失败\n"

def get_default_headers(host, cookies, referer=None, type='default'):
    
    
    default_headers =  {
        "Host": host,
        "Cookie": cookies,
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "sec-gpc": "1",
    }
    
    if referer:
        default_headers["referer"] = referer
         
    if type == 'u2':
        # 根据 type 为 'custom' 提供的额外 headers
        custom_headers = {
                "Host": host,
                "Cookie": cookies,
                "cache-control": "max-age=0",
                "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "origin": "https://u2.dmhy.org",
                "dnt": "1",
                "upgrade-insecure-requests": "1",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "sec-fetch-dest": "document",
                "referer": "https://u2.dmhy.org/showup.php",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                "sec-gpc": "1",
        }
        default_headers.update(custom_headers)
        
    else:
        return default_headers
    
    
def set_sign_in_status(host, status):
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()

            try:
                cursor.execute('''
                    UPDATE Sites
                    SET sign_in_status = ?
                    WHERE host = ?
                ''', (int(status), host)) 

                conn.commit()
                log_background_info(f"Sign-in status set to {status} for site: {host}")

            except Exception as e:

                conn.rollback()
                print(f"Error during set_sign_in_status: {str(e)}")

            finally:
                conn.close()

        except Exception as e:
            print(f"Error during set_sign_in_status: {str(e)}")

def clear_sign_status():
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE Sites
                SET sign_in_status = 0
            ''') 

            conn.commit()
            log_background_info("Sign-in status set to False for all sites")

        except Exception as e:

            conn.rollback()
            print(f"Error during clear_sign_in_status: {str(e)}")

        finally:
            conn.close()

    except Exception as e:
        print(f"Error during clear_sign_in_status: {str(e)}")
        
def get_site_info(host,cookies):
    response = make_request(host, cookies, f'https://{host}/index.php', headers=None, data=None, method='GET')
    if response == None:
        return None
      
    # 提取魔力值
    magic_value = get_magic_value(response.text,host)
    print('魔力值:', magic_value)

    # 提取分享率
    share_ratio = get_share_ratio(response.text,host)
    print('分享率:', share_ratio)

    # 提取上传量、下载量
    uploaded_amount = get_upload_amount(response.text,host)
    downloaded_amount = get_download_amount(response.text,host)

    print('上传量:', uploaded_amount)
    print('下载量:', downloaded_amount)

                    
    # 提取用户名
    username = get_user_name(response.text,host)
    print('用户名:', username)

    # 提取uid
    user_id = get_user_id(response.text,host)
    print('用户ID:', user_id)

    # 提取做种体积
                
    if host == 'pt.btschool.club':
                            
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
        
        seeding_volume = get_seeding_volume(response.text,host)
        print(f'做种量{seeding_volume}')
        
    elif host == 'totheglory.im':
        
        seeding_volume = get_seeding_volume_ttg(host,cookies,user_id)
        print(f'做种量{seeding_volume}')
        
    else:
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
    
    
        url = f'https://{host}/getusertorrentlistajax.php?userid={user_id}&type=seeding'
        try:
            response = requests.get(url, headers=headers)
            seeding_volume = get_seeding_volume(response.text,host)
            print(f'做种量{seeding_volume}')

        except requests.exceptions.RequestException as e:
            log_error_info("请求异常: ", e)
        
  
                        
    ## 获取用户等级
    
 
    user_level = get_user_level(host,cookies,user_id,host)
    print(f'用户等级：{user_level}')
    
    
    ## 获取passkey
    
    passkey = get_passkey(host,cookies,host)
    print('Passkey',passkey)
    
    return magic_value, share_ratio, uploaded_amount, downloaded_amount, username, user_id, seeding_volume, user_level,passkey

