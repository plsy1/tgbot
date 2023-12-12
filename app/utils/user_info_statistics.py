from app.utils.logs import log_background_info, log_error_info
import requests,fnmatch
import re
from bs4 import BeautifulSoup
from app.utils.unittools import convert_large_size, convert_to_gb

def get_user_level(host,cookies,user_id,flag = None):
    
    ##For NexusPHP Websites
    if flag == 'totheglory.im':
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
            with open('output.txt', 'w', encoding='utf-8') as file:
                file.write(response.text)
            
        except requests.exceptions.RequestException as e:
            log_error_info("请求异常: ", e)
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        ##简繁英匹配
        user_level_td = soup.find('td', text=re.compile(r'ç­çº§'))

        if user_level_td:
            user_level = user_level_td.find_next('td').get_text(strip=True)
            return user_level
       
        return
    else:
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
            with open('output.txt', 'w', encoding='utf-8') as file:
                file.write(response.text)
            
        except requests.exceptions.RequestException as e:
            log_error_info("请求异常: ", e)
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        ##简繁英匹配
        user_level_td = soup.find('td', text=re.compile(r'等级|等級|Class'))

        if user_level_td:
            user_level = user_level_td.find_next('img')['alt']
            return user_level
       
        return
    
def get_user_name(text,flag = None):
    
    soup = BeautifulSoup(text, 'html.parser')
    
    if flag == 'u2.dmhy.org':
        username = soup.find('a', class_='PowerUser_Name').text.strip()
    elif flag == 'leaves.red':
        username_parent_tag = soup.find('span', class_='nowrap')
        username_tag = username_parent_tag.find('b') if username_parent_tag else None
        username = re.sub(r'[^\x00-\x7F]+', '', username_tag.text) if username_tag else None
    elif flag == 'totheglory.im':
        target_a = soup.select_one('a[href^="/userdetails.php?id="]')
        username = target_a.get_text(strip=True)    
    else:
        username_parent_tag = soup.find('span', class_='nowrap')
        username_tag = username_parent_tag.find('b') if username_parent_tag else None
        username = username_tag.text if username_tag else None
    return username
    
def get_user_id(text,flag = None):
    soup = BeautifulSoup(text, 'html.parser')
    
    if flag == 'totheglory.im':
        target_a = soup.select_one('a[href^="/userdetails.php?id="]')

        href = target_a['href']
        match = re.search(r'id=(\d+)', href)
        user_id = match.group(1)
        
        return user_id

    else:
        
        link_tag = soup.find('span', class_='nowrap').find('a') if soup.find('span', class_='nowrap') else None
        link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None
        
        if link == None:
            return None;

        uid_match = re.search(r'id=(\d+)$', link)

        if uid_match:
            user_id = uid_match.group(1)
            return user_id
        return None;
def get_share_ratio(text,flag = None):
    soup = BeautifulSoup(text, 'html.parser')
    if flag == 'u2.dmhy.org':
        share_ratio = soup.find('span', class_='color_ratio').next_sibling.strip()
    elif flag == 'totheglory.im':
        target_font = soup.find('font', string="åäº«ç :")
        next_font = target_font.find_next('font')
        if next_font:
            share_ratio = next_font.text
    else:
        share_ratio_tag = soup.find('font', class_='color_ratio')
        share_ratio = share_ratio_tag.next_sibling.strip() if share_ratio_tag else '未找到'
    return share_ratio


def get_upload_amount(text,flag = None):
    soup = BeautifulSoup(text, 'html.parser')
    if flag == 'u2.dmhy.org':
        upload_amount = soup.find('span', class_='color_uploaded').next_sibling.strip()
    elif flag == 'totheglory.im':
        target_font = soup.find('font', string="ä¸ä¼ é : ")
        next_font = target_font.find_next('font')
        upload_amount = next_font.a.get_text(strip=True)
        
    else:
        uploaded_tag = soup.find('font', class_='color_uploaded')
        upload_amount = uploaded_tag.next_sibling.strip() if uploaded_tag else '未找到'
    return upload_amount
                    
                
def get_download_amount(text,flag = None):
    soup = BeautifulSoup(text, 'html.parser')
    if flag == 'u2.dmhy.org':
        download_amount = soup.find('span', class_='color_downloaded').next_sibling.strip()
    elif flag == 'totheglory.im':
        target_font = soup.find('font', string="ä¸è½½é :")
        next_font = target_font.find_next('font')
        download_amount = next_font.a.get_text(strip=True)
    else:
        downloaded_tag = soup.find('font', class_='color_downloaded')
        download_amount = downloaded_tag.next_sibling.strip() if downloaded_tag else '未找到'
    return download_amount

def get_magic_value(text,flag = None):
    soup = BeautifulSoup(text, 'html.parser')
    if flag == 'u2.dmhy.org':
        magic_value = soup.find('span', class_='ucoin-notation').text.strip()
    elif flag == 'www.haidan.video':
        magic_num_span = soup.find('span', id='magic_num')
        if magic_num_span:
            magic_value = magic_num_span.get_text(strip=True)
    elif flag == 'zmpt.cc':
        color_bonus_font = soup.find('font', class_='color_bonus')
        if color_bonus_font:
            magic_value = color_bonus_font.find_next_sibling(string=True).strip()
        else:
            return None
    elif flag == 'leaves.red':
        magic_value_tag = soup.find('a', href='mybonus.php')

        if magic_value_tag:
            magic_value_text = magic_value_tag.get_text(strip=True)
            magic_value_match = re.search(r'\d+,\d+\.\d+', magic_value_text)
            if magic_value_match:
                magic_value = magic_value_match.group()
            else:
                return None
        else:
            return None
        
    elif flag == 'totheglory.im':
        magic_text_a = soup.find('a', href="/mybonus.php")
        magic_value = magic_text_a.get_text(strip=True)
        
        
    else:
        magic_value_tag = soup.find('font', class_='color_bonus')
        magic_value_text = magic_value_tag.find_next('a').next_sibling.strip() if magic_value_tag else '未找到'

        magic_value_match = re.search(r'\]:\s*([\d.,]+)', magic_value_text)

        if magic_value_match:
            magic_value = magic_value_match.group(1)
        else:
            return None
    return magic_value

def get_seeding_volume(text,flag = None):
    if flag == 'www.haidan.video':

        soup = BeautifulSoup(text, 'html.parser')
        total_volume_gb = 0
        rows = soup.find_all('tr')
        # 提取每个<tr>中第一个<td>标签中对应的文本部分
        for row in rows:
            # 找到第一个<td>标签中class为"rowfollow"且align为"center"的部分
            size_td = row.find('td', class_='rowfollow', align='center')

            # 输出提取的文本部分
            if size_td:
                size_text = size_td.get_text(strip=True)
                size_match = re.search(r'([\d.]+)([A-Za-z]+)', size_text)
                if size_match:
                    size_value, size_unit = size_match.groups()
                    size_value = float(size_value)
                    total_volume_gb += convert_to_gb(size_value, size_unit)
        size,unit = convert_large_size(total_volume_gb,'GB')
        seeding_volume = f'{size} {unit}'

    elif fnmatch.fnmatch(flag, '*.m-team.io'):
        soup = BeautifulSoup(text, 'html.parser')

        total_volume_gb = 0

        for tr in soup.find_all('tr'):
            size_tds = tr.find_all('td', class_='rowfollow', align='center')
            if len(size_tds) >= 3:
                size_text = size_tds[0].get_text(strip=True)
                size_match = re.search(r'([\d.]+)\s*([A-Za-z]+)', size_text)
                if size_match:
                    size_value, size_unit = size_match.groups()
                    size_value = float(size_value)
                    total_volume_gb += convert_to_gb(size_value, size_unit)

        size,unit = convert_large_size(total_volume_gb,'GB')
        seeding_volume = f'{size} {unit}'

    elif flag == 'u2.dmhy.org':
        seeding_size_match = re.search(r'大小\s*([^<]+)', text)
        if seeding_size_match:
            seeding_size_with_space = seeding_size_match.group(1).strip()
            seeding_volume = re.sub(r'&nbsp;', '', seeding_size_with_space)
        else:
            return None;
    elif flag == 'pt.btschool.club':
        match_three = re.search(r'\((\d+)个种子，共计([\d.]+\s*[A-Za-z]+)\)', text)
        if match_three:
            seeding_volume = match_three.group(2)
            print(f"Total Size: {seeding_volume}")
        else:
            return None
        
    else:
        match = re.search(r'(?:总大小：|Total:)\s*([\d.]+)\s*([A-Za-z]+)', text)
        if match:
            total_size_value = match.group(1)
            total_size_unit = match.group(2)
            seeding_volume = f'{total_size_value} {total_size_unit}'
        else:
            return 0;
    
    return seeding_volume

def get_seeding_volume_ttg(host,cookies,user_id):
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
        with open('output.txt', 'w', encoding='utf-8') as file:
            file.write(response.text)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到<tr valign='top'>
        target_tr = soup.find('tr', {'valign': 'top'})

        # 在<tr valign='top'>内部查找<td align=left>下的<div id="ka2">
        div_ka2 = target_tr.find('td', {'align': 'left'}).find('div', {'id': 'ka2'})

        # 在<div id="ka2">内部查找<table class=main>
        table_main = div_ka2.find('table', {'class': 'main'})
        total_volume_gb = 0
        if table_main:
            # 提取<table class=main>的信息
            rows = table_main.find_all('tr')[1:]  # 从第二行开始
            for row in rows:
                # 找到每行的第四个<td>并提取值
                fourth_td = row.find_all('td')[3]
                match = re.match(r'([\d.]+)\s*([a-zA-Z]+)', fourth_td.get_text(strip=True))
                if match:
                    value, unit = match.groups()
                    total_volume_gb += convert_to_gb(float(value), unit)
                else:
                    print("No <table class='main'> found.")
        
            size,unit = convert_large_size(total_volume_gb,'GB')
            seeding_volume = f'{size} {unit}'
            return seeding_volume
    
    except requests.exceptions.RequestException as e:
        log_error_info("请求异常: ", e)
        return None
    
    return None
    

