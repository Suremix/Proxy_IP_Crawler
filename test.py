import requests
import pandas as pd
from fake_useragent import UserAgent

user_agent = UserAgent()
headers = {
    "User-Agent": user_agent.chrome,
    "Connection": "close",
}

ip_data_df = pd.read_csv("/root/myData/good_ip_open_dataset.csv", dtype={"PORT": str})
ip = ip_data_df.loc[1, "IP"]
port = ip_data_df.loc[1, "PORT"]
proxies = {
    "http":"http://" + ip + ":" + port,
    "https":"http://" + ip + ":" + port,
}

# url = "http://ip111.cn"
url = "http://www.baidu.com"
error_tuple = (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout)

try:
    respone = requests.get(url, headers=headers, timeout=5)
except error_tuple as e:
    print("异常IP: " + ip + ":" + port)
    print("异常信息: ", e)
else:
    print(respone.status_code)
    print(respone.status_code == 200)

