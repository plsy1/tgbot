import xml.etree.ElementTree as ET
from app.utils.config import conf as config
from urllib.parse import quote
import os, time
from app.plugins.audiobooksfeed.metadata import *
import sqlite3
from email.utils import formatdate


def generate_item_element(host,bookdir, file_name,reader,time_diff_hours):
    
    
    encoded_file_name = quote(file_name, safe="")
    
    base_name, file_extension = os.path.splitext(file_name)
    
    # 创建 <item> 元素
    item = ET.Element("item")

    # 添加 <title> 元素到订阅项，使用文件名
    item_title = ET.SubElement(item, "title")
    item_title.text = base_name
    
    # 计算时间差
    current_time = time.time()
    pub_date_time = current_time + (time_diff_hours * 3600)  # 将小时转换为秒

    # 添加 <pubDate> 元素到订阅项
    item_pub_date = ET.SubElement(item, "pubDate")
    item_pub_date.text = formatdate(timeval=pub_date_time, localtime=True)
    
    
    item_author = ET.SubElement(item, "itunes:author")
    item_author.text = reader if reader else "Default Author Name"
    
    # 添加 <enclosure> 元素到订阅项
    enclosure = ET.SubElement(item, "enclosure", attrib={
        "url": f"{host}/{bookdir}/{encoded_file_name}",
        "type": ("audio/x-m4a")
    })


    return item


def generate_podcast_feed(metadata, reader,desc,episode_list,book_dir,timestamp):
    
    encoded_book_dir = quote(book_dir, safe="")
    
    # 创建根元素 <rss>
    rss = ET.Element("rss", version="2.0", attrib={
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })

    # 创建子元素 <channel>
    channel = ET.SubElement(rss, "channel")

    # 添加 <title> 元素
    title = ET.SubElement(channel, "title")
    title.text = metadata.get("title", "Your Podcast Title")

    # 添加 <link> 元素
    link = ET.SubElement(channel, "link")
    link.text = metadata.get("website", "http://www.yourpodcastwebsite.com")

    # 添加 <language> 元素
    language = ET.SubElement(channel, "language")
    language.text = metadata.get("language", "en-us")

    # 添加 <itunes:author> 元素
    author = ET.SubElement(channel, "itunes:author")
    author.text = reader if reader else "Default Author Name"

    # 添加 <itunes:summary> 元素
    itunes_summary = ET.SubElement(channel, "itunes:summary")
    itunes_summary.text = desc if desc else "Your podcast description."

    # 添加 <description> 元素
    description = ET.SubElement(channel, "description")
    description.text = desc if desc else "Your podcast description."


    # 添加 <itunes:owner> 元素
    itunes_owner = ET.SubElement(channel, "itunes:owner")
    itunes_owner_name = ET.SubElement(itunes_owner, "itunes:name")
    itunes_owner_name.text = metadata.get("owner_name", "Your Name")
    itunes_owner_email = ET.SubElement(itunes_owner, "itunes:email")
    itunes_owner_email.text = metadata.get("owner_email", "your@email.com")

    # 添加 <itunes:image> 元素
    dir = f'{config.root_folder}/{book_dir}'
    cover = get_cover(dir)
    itunes_image = ET.SubElement(channel, "itunes:image", attrib={"href": metadata.get("cover_image", f'http://{config.server_host}:{config.server_port}/{encoded_book_dir}/{cover[0]}')})

    time_diff_hours = 0

    for file_name in episode_list:
        item = generate_item_element(f'http://{config.server_host}:{config.server_port}',encoded_book_dir,file_name,reader,time_diff_hours)
        channel.append(item)
        time_diff_hours += 1


    # 将 XML 树转换为字符串
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="utf-8").decode()

    # 将生成的 XML 字符串写入文件
    # filename = sanitize_filename(metadata["title"])
    with open(f"{config.root_folder}/{book_dir}.xml", "w") as xml_file:
        xml_file.write(xml_string)

    print(f"{book_dir} Podcast feed with metadata generated successfully!")
    #output_path = f"rss_{timestamp}.txt"  # 文件名加上时间戳
    #with open(output_path, "a") as output_file:
        
        #output_file.write(f'文件目录名：{book_dir}\n')
    rss_link = f'http://{config.server_host}:{config.server_port}/xml/{encoded_book_dir}.xml\n\n'
        #output_file.write('RSS链接： ' + rss_link)
        
    #return f"{book_dir}\n{rss_link}"
    return rss_link


def generate_rss_file(audio_books):
    
    timestamp = int(time.time())
    links = ''
    
    for book_dir in audio_books:
        current_dir = f'{config.root_folder}/{book_dir}'
        episode_files_name = get_file_names(current_dir, config.audio_extensions)
        
        metadata_path = current_dir + "/metadata.abs"
        metadata = get_metadata(metadata_path)
        
        reader_path = current_dir + "/reader.txt"
        reader = get_reader(reader_path)
        
        desc_path = current_dir + "/desc.txt"
        desc = get_desc(desc_path)
        
        
        rss_link = generate_podcast_feed(metadata,reader,desc,episode_files_name,book_dir,timestamp)
        
        
        ##打入数据库
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT folder FROM AudioBooks WHERE folder = ?', (book_dir,))
            existing_folder = cursor.fetchone()

            if existing_folder:
                cursor.execute('UPDATE AudioBooks SET rss_url = ? WHERE folder = ?', (rss_link, book_dir))
                conn.commit()
        
        except Exception as e:
            print(f"Error: {str(e)}")

        finally:
            conn.close()
        links += f"{book_dir}\n{rss_link}"
        
    return links
        
def init_rss_file():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    try:
        # 获取文件夹信息
        folders = get_all_folders(config.root_folder)

        # 将文件夹信息插入数据库
        for folder in folders:
            cursor.execute('INSERT INTO AudioBooks (folder) VALUES (?)', (folder,))

        conn.commit()
        print("Folders initialized in the database.")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        conn.close()
            
def find_new_folder():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT folder FROM AudioBooks')
        old_data = set(row[0] for row in cursor.fetchall())

        # 获取新的文件夹数据
        new_data = set(get_all_folders(config.root_folder))
        
        # 计算新增的文件夹
        new_folders = new_data - old_data


        # 将新增的文件夹插入到数据库
        if new_folders:
            for folder in new_folders:
                cursor.execute('INSERT INTO AudioBooks (folder) VALUES (?)', (folder,))
                
            conn.commit()
            print(f"New folders added: {new_folders}")
            
            return list(new_folders)
        
    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        conn.close()
        
    return None;

def gen_new_audio_rss():
    new_folders = find_new_folder()
    if new_folders:
        return f"新有声书入库，RSS地址生成如下：\n\n{generate_rss_file(new_folders)}"
    return '未检测到有声书入库。'

