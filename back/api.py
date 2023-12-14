import sqlite3
from app.modules.sites import sites
from app.modules.rss import RSSParser
from app.modules.database import get_passkey_and_host
import re


def sitesInfo():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT SiteStats.id, Sites.name, SiteStats.username, SiteStats.user_level,
            SiteStats.user_id, SiteStats.upload_amount, SiteStats.download_amount,
            SiteStats.share_ratio, SiteStats.magic_value,
            SiteStats.seeding_volume
    FROM SiteStats
    INNER JOIN Sites ON SiteStats.host = Sites.host
''')
    
    
    information = cursor.fetchall()
    conn.close()
    
    site_info_list = []
    
    for info in information:
            id, site_name, username, user_level, user_id, upload_amount, download_amount, \
            share_ratio, magic_value, seeding_volume = info

            site_info = {
            "id": id,
            "site_name": site_name,
            "username": username,
            "user_level": user_level,
            "user_id": user_id,
            "upload_amount": upload_amount,
            "download_amount": download_amount,
            "share_ratio": share_ratio,
            "magic_value": magic_value,
            "seeding_volume": seeding_volume,
            }
        
            site_info_list.append(site_info)

    return site_info_list


def rssSearch(keyword):
        rss = RSSParser()
        passkeys = get_passkey_and_host()

        all_results = []

        for passkey, host in passkeys:
                results = rss.keyword_search(host,passkey, keyword)
                if results is not None:
                        all_results.extend(results)
                        
        api_results = [{'title': result[0], 'download_link': result[1]} for result in all_results]
        return api_results


