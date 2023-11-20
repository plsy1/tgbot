import fnmatch
import re
from PyCookieCloud import PyCookieCloud
from app.utils.config import conf
from app.utils.sign_in_utils import make_request
from app.utils.sign_in_utils import is_sign_in_ok

class Sites:
    def __init__(self, host, uuid, password):
        self.cookie_cloud = PyCookieCloud(host, uuid, password)
        self.SITECOOKIES = {}
        self.cookies_updated = False

    def update_cookies(self):
        if not self.cookies_updated:
            the_key = self.cookie_cloud.get_the_key()
            if not the_key:
                print('Failed to get the key')
                return
            encrypted_data = self.cookie_cloud.get_encrypted_data()
            if not encrypted_data:
                print('Failed to get encrypted data')
                return
            decrypted_data = self.cookie_cloud.get_decrypted_data()
            if not decrypted_data:
                print('Failed to get decrypted data')
                return

            for site, cookies in decrypted_data.items():
                cookie_string = ";".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                sign_in_url = self.get_sign_in_url(site)
                self.SITECOOKIES[site] = {'cookies': cookie_string, 'sign_in_url': sign_in_url}

            self.cookies_updated = True

    def get_cookie(self):
        self.update_cookies()

        for site, data in self.SITECOOKIES.items():
            print(f"Site: {site}")
            print(f"    Cookies: {data['cookies']}")
            print(f"    Sign In URL: {data['sign_in_url']}")
            print("-" * 20)

    def get_sign_in_url(self, site):
        patterns = {
            "*.m-team.io": "https://{}/index.php",
            "pt.btschool.club": "https://{}/index.php?action=addbonus",
            "www.haidan.video": "https://www.haidannn.video/signin.php",
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
    
    def sigin_in(self):
        res = '*【签到通知】*\n'
        for host, data in self.SITECOOKIES.items():
            cookies = data['cookies']
            sign_in_url = data['sign_in_url']
            
            if host == "totheglory.im":
                response = make_request(host, cookies, 'https://totheglory.im/index.php', headers=None, data=None, method='GET')
                pattern = r'signed_timestamp:\s*"(\d+)",\s*signed_token:\s*"([a-f0-9]+)"'
                match = re.search(pattern, response.text)
                if match:
                    timestamp, token = match.groups()
                    data = {"signed_timestamp": timestamp,"signed_token": token,}
                response = make_request(host, cookies, sign_in_url, headers=None, data=data, method='POST')
                res += is_sign_in_ok(host,response)
                
            elif host == "u2.dmhy.org":
                response = make_request(host, cookies, 'https://u2.dmhy.org/showup.php', headers=None, data=None, method='GET')
                match = re.search(r'<input type="hidden" name="req" value="([^"]+)" />\s*<input type="hidden" name="hash" value="([^"]+)" />\s*<input type="hidden" name="form" value="([^"]+)" />', response.text)
                if match:
                    req_value, hash_value, form_value = match.groups()
                matches = re.findall(r'<input type="submit" name="([^"]+)" value="([^"]+)"', response.text)
                submit_values = [{"name": match[0], "value": match[1]} for match in matches]
                data = {
                    "message": "签到咧签到咧", 
                    "req": req_value,
                    "hash": hash_value,
                    "form": form_value,
                    submit_values[0]['name']: submit_values[0]['value']
                }
                response = make_request(host, cookies, sign_in_url, headers=None, data=data, method='POST')
                res += is_sign_in_ok(host,response)
            
            else:
                response = make_request(host, cookies, sign_in_url, headers=None, data=None, method='GET')
                res += is_sign_in_ok(host,response)
        return res
                

    
sites = Sites(conf.cookiecloud_host, conf.cookiecloud_uuid, conf.cookiecloud_password)
sites.get_cookie()
