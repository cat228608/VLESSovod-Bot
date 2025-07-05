import json
import random
from urllib.parse import urlparse
import requests
import qrcode

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def add_client(url, username, password, inbound_id, conf, number, sni='t.me', user_id='0'):
    try:
        s = requests.Session()
        r = s.post(f'{url}/login', json={'username': username, 'password': password}, verify=False)
        r.raise_for_status()
        login_data = r.json()
        if not login_data.get('success'):
            print(f"[Login Error] {login_data.get('msg')}")
            return 'error'

        urls = f'{url}/panel/api/inbounds/addClient'
        pay = {'id': inbound_id, 'settings': json.dumps({'clients': [conf]})}
        r = s.post(urls, json=pay, verify=False)
        r.raise_for_status()
        add_data = r.json()
        if not add_data.get('success'):
            print(f"[Add Client Error] {add_data.get('msg')}")
            return 'error'

        urls_list = f"{url}/panel/inbound/list"
        r = s.post(urls_list, verify=False)
        response_list = r.json()
        
        obj_found = next((obj for obj in response_list["obj"] if obj['id'] == inbound_id), None)
        if not obj_found:
            print(f"Не удалось найти inbound с id {inbound_id}")
            return 'error'

        stream_settings = json.loads(obj_found["streamSettings"])
        reality_settings = stream_settings["realitySettings"]
        public_key = reality_settings["settings"]["publicKey"]
        short_ids = reality_settings["shortIds"]
        random_short_id = random.choice(short_ids)
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        
        vless = f"vless://{number}@{host}:443?type=tcp&security=reality&pbk={public_key}&fp=chrome&sni={sni}&sid={random_short_id}&spx=%2F&flow=xtls-rprx-vision#HostBot"
        return vless
    except Exception as er:
        print(f"[add_client error] {er}")
        if 'r' in locals() and r:
             print(f"Ответ сервера: {r.text}")
        return 'error'

def check_stats(url, username, password, client_uuid):
    try:
        s = requests.Session()
        r = s.post(f'{url}/login', json={'username': username, 'password': password}, verify=False)
        r.raise_for_status()
        login_data = r.json()
        if not login_data.get('success'):
            return None

        urls = f'{url}/panel/api/inbounds/getClientTrafficsById/{client_uuid}'
        r = s.get(urls, verify=False)
        r.raise_for_status()
        data = r.json()
        if not data.get('obj'):
            return {'up': 0.0, 'down': 0.0, 'total': 0.0}

        up_bytes = data['obj'][0]['up']
        down_bytes = data['obj'][0]['down']
        total_bytes = up_bytes + down_bytes

        bytes_in_mb = 1024 * 1024
        up_mb = up_bytes / bytes_in_mb
        down_mb = down_bytes / bytes_in_mb
        total_mb = total_bytes / bytes_in_mb
        
        return {'up': up_mb, 'down': down_mb, 'total': total_mb}
    except Exception as er:
        print(f"[check_stats error] {er}")
        if 'r' in locals() and r:
             print(f"Ответ сервера: {r.text}")
        return None

def del_client(url, username, password, inbound_id, client_uuid):
    try:
        s = requests.Session()
        r = s.post(f'{url}/login', json={'username': username, 'password': password}, verify=False)
        r.raise_for_status()
        login_data = r.json()
        if not login_data.get('success'):
            return 'error'

        urls = f"{url}/panel/inbound/{inbound_id}/delClient/{client_uuid}"
        r = s.post(urls, verify=False)
        r.raise_for_status()
        response_json = r.json()
        if response_json.get('success') is True:
            return '1'
        else:
            return 'error'
    except Exception as er:
        print(f"[del_client error] {er}")
        if 'r' in locals() and r:
             print(f"Ответ сервера: {r.text}")
        return 'error'

def generate_qr_code(text, filename="qr_code.png"):
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return 'good'
    except Exception as er:
        print(f"[generate_qr_code error] {er}")
        return 'error'