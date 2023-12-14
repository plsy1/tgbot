import os, re
import netifaces
import ipaddress

def get_preferred_ip_address():
    private_networks = [
        ipaddress.IPv4Network('10.0.0.0/8'),
        ipaddress.IPv4Network('172.16.0.0/12'),
        ipaddress.IPv4Network('192.168.0.0/16')
    ]


    try:
        # 获取所有网络接口信息
        interfaces = netifaces.interfaces()

        # 遍历网络接口找到IPv4地址
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
            for addr_info in addrs:
                ip_address = addr_info['addr']

                # 检查是否是私有地址
                if any(ipaddress.ip_address(ip_address) in private_net for private_net in private_networks):
                    return ip_address

    except Exception as e:
        print(f"Error: {e}")

    return None

def get_metadata(abs_file_path):
    metadata = {}
    chapters = []

    with open(abs_file_path, "r", encoding="utf-8") as abs_file:
        # 读取前18行
        lines = [next(abs_file).strip() for _ in range(18)]

        # 处理键值对
        for line in lines:
            parts = line.split("=")
            if len(parts) == 2:
                key, value = parts
                metadata[key.strip()] = value.strip()

        # 处理章节信息
        for line in abs_file:
            if line.startswith("[CHAPTER]"):
                chapter = {}
                for _ in range(3):
                    key, value = next(abs_file).strip().split("=")
                    chapter[key.strip()] = value.strip()
                chapters.append(chapter)

    metadata["chapters"] = chapters
    return metadata
def get_reader(abs_file_path):
    reader = ''
    with open(abs_file_path, "r", encoding="utf-8") as abs_file:
        reader = abs_file.readline().strip()

    return reader

def get_desc(abs_file_path):
    desc = ''
    with open(abs_file_path, "r", encoding="utf-8") as abs_file:
        desc = abs_file.read()

    return desc


def get_file_names(directory, extensions):
    files = []
    for filename in sorted(os.listdir(directory)):
        if any(filename.endswith(ext) for ext in extensions):
            files.append(filename)
    return files

def get_cover(directory):
    files = []
    for filename in sorted(os.listdir(directory)):
        file_name_without_extension, file_extension = os.path.splitext(filename)
        if 'cover' == file_name_without_extension.lower():
            files.append(filename)
    return files

def get_all_folders(dir):
    # 获取当前工作目录


    # 使用 os.listdir 获取当前目录下的所有文件和文件夹
    all_items = os.listdir(dir)

    # 使用列表推导式筛选出文件夹
    folders = [item for item in all_items if os.path.isdir(os.path.join(dir, item))]

    return folders

def sanitize_filename(title):
    # 使用正则表达式过滤掉非字母、数字、下划线、连字符和空格的字符
    sanitized_title = re.sub(r'[^\w\s-]', '', title)
    
    # 替换空格和连字符为下划线
    sanitized_title = re.sub(r'[-\s]+', '_', sanitized_title)
    
    return sanitized_title