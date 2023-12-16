import requests
from app.utils.config import conf

def is_container_running(container_name):
    containers_info = requests.get(f"{conf.cadvisor_url}/api/v1.2/docker/{container_name}")
    if containers_info.status_code == 500:
        return False
    return True

def container_status_check():
    res = ''
    for container in conf.check_list:
        if not is_container_running(container):
            res += f'容器：{container} 当前未运行，请检查。\n'
    return res