# 这个脚本打算爬一些代理IP保存给自己用
# 目前的打算是从快代理这个网站里边整一些给自己用

import os
import time
import requests
import pandas as pd
from fake_useragent import UserAgent
from lxml import etree


def get_ip_data_df_from_url(url):
    # 设置headers
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.chrome}

    # 申请网页响应，先默认肯定能接通
    respone = requests.get(url, headers=headers)
    print(url + "  State_Code:", respone.status_code)

    # 从响应里获取html源码
    html = etree.HTML(respone.text)
    tr_list = html.xpath('//table[@class="table table-b table-bordered table-striped"]/tbody/tr')
    data_title_list = ["IP", "PORT", "匿名度", "类型", "位置", "最后验证时间"]

    # 获取从源码里获取特定的数据，存入df并返回
    num_ip = len(tr_list)
    ip_data_df = pd.DataFrame(index=range(0, num_ip), columns=data_title_list)
    for i in range(0, num_ip):
        tr = tr_list[i]
        for data_title in data_title_list:
            xpath_cmd = './td[@data-title="{0}"]'.format(data_title)
            ip_data_df.loc[i, data_title] = tr.xpath(xpath_cmd)[0].text

    return ip_data_df


def save_ip_data_from_kuaidaili(ip_type, num_page, output_folder, sleep_time=2):
    # 根据需求设置好需要进行爬虫的url以及爬取的页数
    if ip_type == "open":
        url = "https://www.kuaidaili.com/free/inha/"
    elif ip_type == "anonymous":
        url = "https://www.kuaidaili.com/free/intr/"
    else:
        url = ""
        print("Warring: ip_type is wrong!")

    # 准备一个df来存储数据
    ip_data_df = pd.DataFrame()
    for i in range(1, num_page + 1):
        # 获取ip数据df
        url_page_i = url + str(i) + "/"
        ip_data_df_page_i = get_ip_data_df_from_url(url_page_i)

        # 与之前获得的数据合并
        # 如果现在是获取的第一个数据，也就是idx数量为0的话，就用其直接替换总的df
        # 否则就concat两个df
        if ip_data_df.shape[0] == 0:
            ip_data_df = ip_data_df_page_i
        else:
            ip_data_df = pd.concat([ip_data_df, ip_data_df_page_i], axis=0)

        # 设置每次翻页的间隔时间防止被发现
        time.sleep(sleep_time)

    # 组合文件夹名和文件名，这里不加一个str的话pycharm会警告，不知道为啥
    file_name = "ip_" + ip_type + "_dataset.csv"
    output_path = str(os.path.join(output_folder, file_name))

    # 如果文件不存在，则保存个新的
    # 如果已存在文件，则已文件的形式一行一行写进去
    ip_data_df.to_csv(output_path, index=False, encoding="utf_8_sig")


if __name__ == "__main__":
    print(time.asctime())
    output_folder = "/root/MyData/"
    save_ip_data_from_kuaidaili("open", 2, output_folder)
    save_ip_data_from_kuaidaili("anonymous", 2, output_folder)







