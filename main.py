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
    headers = {"User-Agent": user_agent.chrome}

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

    # 最后对验证时间的类型该一下，改成datetime
    ip_data_df["最后验证时间"] = pd.to_datetime(ip_data_df["最后验证时间"])
    return ip_data_df


def save_ip_data_from_kuaidaili_old(ip_type, num_page, output_folder, sleep_time=2):
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


def save_ip_data_from_kuaidaili(ip_type, output_folder, max_page_num=10, sleep_time=2):
    # 设置保存的路径
    file_name = "ip_" + ip_type + "_dataset.csv"
    output_path = os.path.join(output_folder, file_name)

    # 打开之前保存的文件，打开看最新的时间，用变量存下来
    # 如果是没有文件，那就设一个flag说没文件
    output_exist_flag = os.path.exists(output_path)
    if output_exist_flag is True:
        old_ip_data_df = pd.read_csv(output_path)
        last_time = pd.to_datetime(old_ip_data_df.loc[0, "最后验证时间"])
    
    # 新建一个df用来存新的ip信息
    data_title_list = ["IP", "PORT", "匿名度", "类型", "位置", "最后验证时间"]
    ip_data_df = pd.DataFrame(columns=data_title_list)

    # 根据需求设置好需要进行爬虫的url
    if ip_type == "open":
        url = "https://www.kuaidaili.com/free/inha/"
    elif ip_type == "anonymous":
        url = "https://www.kuaidaili.com/free/intr/"
    else:
        url = ""
        print("Warring: ip_type is wrong!")

    page_num = 1
    stop_flag = False
    # 先打开第一页，获取tr列表，然后遍历列表
    # 当遇到的ip时间小于保存的最新时间，就停止
    # 然后遍历结束就翻页
    # 如果一直没有遇到（或者flag说没文件），但是翻页已经超过一定页数了，也停止
    while (stop_flag is False) and (page_num <= max_page_num):
        url_page = url + str(page_num) + "/"
        page_ip_data_df = get_ip_data_df_from_url(url_page)

        # 我有个想法，我可以获取page的df之后，先看时间有没有小于last_time的
        # 如果没有，就将整个df用concat加到总的df里
        # 如果发现有，就将之前的那些concat到总的df里
        for idx in page_ip_data_df.index:
            if (output_exist_flag is True) and (page_ip_data_df.loc[idx, "最后验证时间"] < last_time):
                # 这里有个问题，就是假如idx为0，则idx-1就变为-1了
                # 但是由于index里没有-1这一项，所有0:-1会啥都选不中
                # 这正是程序所想要的，要是page的第一个ip就已经是不需要的了，那啥都选不中就会把page的df设为一个空的df
                # 而concat一个空的df是不会报错的，所以没啥问题
                page_ip_data_df = page_ip_data_df.loc[0:idx-1, :]
                stop_flag = True
                break
        
        ip_data_df = pd.concat([ip_data_df, page_ip_data_df], axis=0)
        page_num += 1

        # 设置每次翻页的间隔时间防止被发现
        time.sleep(sleep_time)

    # 获取整个新df后，加一个新列用来表示ip是否可用
    # 先默认新的所有都可以用，所以设为1
    ip_data_df["valid_flag"] = 1
    # 如果之前已经有文件了，那就需要再把之前的数据加在新数据的后面
    if output_exist_flag is True:
        ip_data_df = pd.concat([ip_data_df, old_ip_data_df], axis=0)
    
    # 然后保存文件
    ip_data_df.to_csv(output_path, index=False, encoding="utf_8_sig")
    

if __name__ == "__main__":
    print(time.asctime())
    output_folder = "/root/myData/"
    save_ip_data_from_kuaidaili("open", output_folder)
    save_ip_data_from_kuaidaili("anonymous", output_folder)







