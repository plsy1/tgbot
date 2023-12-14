import feedparser

class RSSParser:
    def __init__(self):
        {}
    
    def gen_rss_url(self, host, passkey, rows, search=None):
        patterns = {
            "www.hdkyl.in": "https://{}/torrentrss.php?passkey={}&rows={}&{}paid=0&linktype=dl&ismalldescr=1",
            "hdfans.org": "https://{}/torrentrss.php?passkey={}&rows={}&{}linktype=dl&ismalldescr=1",
        }

        try:
            rss_pattern = patterns.get(host)
            search_param = f"search={search}&" if search else ""
            
            if rss_pattern:
                rss_url = rss_pattern.format(host, passkey, str(rows), search_param)
                return rss_url
            else:
                print(f"Unsupported host: {host}")

        except Exception as e:
            print(f"Error setting RSS URL: {e}")
    
    def parse_rss(self,rss_url):
        
        res = []
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                rss_title =  entry.get('title')
                rss_download_link = entry.get('links', [])[1].get('href', '')
                res.append((rss_title, rss_download_link))
            return res 

        except Exception as e:
            print("Error:", e)
            return


    def keyword_search(self,host,passkey,keyword):
        
        url = self.gen_rss_url(host,passkey,10,keyword)
        result = self.parse_rss(url)
        
        return result