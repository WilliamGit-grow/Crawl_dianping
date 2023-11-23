from datetime import datetime
# import pandas
import pandas as pd
import requests
from lxml import etree
from fake_useragent import UserAgent
import time
import random
import urllib.request
import zlib
import config
import os

cookies_l = config.cookie_list
print(str(UserAgent().random))

# 检验ip是否可用——pin baidu
def check_ip(ip_pool):
    headers = {
        'User-Agent': str(UserAgent().random)
    }

    can_use = []
    for ip in ip_pool:
        proxies = {'http': 'http://' + ip}
        try:
            response = requests.get('https://www.baidu.com/', headers=headers, proxies=proxies, timeout=0.1)
            if response.status_code == 200:
                can_use.append(ip)


        except Exception as e:
            print(e)

    return can_use

# 每一个页面的数据链接获取
def hg_page(rep):
    time.sleep(2)
    dp_url_list = []
    et = etree.HTML(rep.text)
    li_list = et.xpath("//div[@id='shop-all-list']/ul/li")
    # print(len(li_list))
    # 拿取店铺信息
    for li in li_list:
        # dp_name = li.xpath("./div[@class='txt']/div[@class='tit']/a/h4/text()")
        dp_url = li.xpath("./div[@class='txt']/div[@class='tit']/a/@href")
        # print(dp_name)
        # print(dp_url[0])
        dp_url_list.append(dp_url[0])
        # detail_page(dp_url[0])
        # 请求评论详情首页
    return dp_url_list

# 获取ip池
def get_ip_pool():
    api_url = config.api_u


    headers = {"Accept-Encoding": "Gzip"}  # 使用gzip压缩传输数据让访问更快

    req = urllib.request.Request(url=api_url, headers=headers)

    # 请求api链接
    res = urllib.request.urlopen(req)

    # print(res.code)  # 获取Reponse的返回码

    # ip_pool_row = []
    content_encoding = res.headers.get('Content-Encoding')
    if content_encoding and "gzip" in content_encoding:
        str_ip=zlib.decompress(res.read(), 16 + zlib.MAX_WBITS).decode('utf-8')  # 获取页面内容

    else:
        str_ip=res.read().decode('utf-8')  #获取页面内容

    # print(ip_pool_row)
    ip_pool_row = str_ip.split('\r\n')

    with open("log.txt","a",encoding='utf-8') as f:
        f.write(str(ip_pool_row))

    # print(ip_pool_row)
    return ip_pool_row

# 具体店铺数据获取
def detail_page(detail_url,cookies_l):
    print(f"{detail_url}/review_all")

    """ 设置好代理池
        就快成功了！！！"""
    #
    # print(proxies)
    # time.sleep(5)
    dic = {}
    # 创建天津站待写入的excel
    # new_station_excel()

    station_excel=pd.ExcelWriter(config.path_excel, engine="openpyxl")

    # 设置代理池
    ip_pool_raw = get_ip_pool()
    ip_pool_use = check_ip(ip_pool_raw)

    # 向更多评论页面发送请求
    for i in range(config.start_page, config.end_page+1):
        ck = random.choice(cookies_l)
        # 设置随机head
        headers = {
            "Cookie": ck,
            "User-Agent": str(UserAgent().random)
        }
        print(headers)
        print(config.browser[ck])
        dic_i = {}

        ip = random.choice(ip_pool_use)
        # ip = "221.229.212.171:25380"

        proxies = {
            "http": 'http://' + ip
            # "https": 'https//' + ip

        }

        """    todo 设置好代理池
            就快成功了！！！"""

        print(proxies)
        time.sleep(5)
        rep_datail = requests.get(f"{detail_url}/review_all/p{i}", proxies=proxies, headers=headers)

        # 解析详情页面
        et_detail = etree.HTML(rep_datail.text)
        if et_detail is None:
            with open(f"{config.folder}\\CHECK.txt","a") as f:
                f.write("!!! "+f"page:{i} "+config.browser[ck]+" seems Error !!!")
                f.write("\n")
            continue
        else:
            with open(f"{config.folder}\\CHECK.txt","a") as f:
                f.write(f"page:{i} "+config.browser[ck])
                f.write("\n")

        # 获取评论列表
        comment_list_i = []
        datail_li_list = et_detail.xpath("//div[@class='reviews-items']/ul/li")
        # 提取评论数据
        for datail_li in datail_li_list:
            dic_comment = {}
            # 用户名
            user_name = ''.join(datail_li.xpath("./div[@class='main-review']/div[@class='dper-info']//text()")).strip()
            # 用户评分
            comment_score = ''.join((datail_li.xpath(
                "./div[@class='main-review']/div[@class='review-rank']/span/@class"))).split()
            score_temp=''
            for stri in comment_score:
                for chi in stri:
                    if chi<="9" and chi>="0":
                        score_temp=score_temp+chi

            # 用户评论

            user_comment = ''.join(
            datail_li.xpath("./div[@class='main-review']/div[@class='review-words Hide']/text()")).strip()
            print("cm1:"+user_comment)
            if user_comment == '':
                print("continue:")
                user_comment = ''.join(
                datail_li.xpath("./div[@class='main-review']/div[@class='review-words']/text()")).strip()
                print("cm2:"+user_comment)

            # 用户评论时间
            user_comment_time = ''.join(
                datail_li.xpath("./div[@class='main-review']//span[@class='time']/text()")).strip()

            dic_comment["user_name"] = user_name
            dic_comment["user_comment"] = user_comment
            dic_comment["comment_star"] = score_temp
            dic_comment["comment_time"] = user_comment_time

            comment_list_i.append(dic_comment)
            
        # print(comment_list_i)
        # dic_i["dp_name"] = dp_name
        # dic_i["dp_address"] = dp_address
        # dic_i["comment_list_i"] = comment_list_i
        # dic_i["user_name","user_comment","comment_time"]=dic_comment["user_name","user_comment","comment_time"]
        df_i=pd.DataFrame(comment_list_i)
        if df_i.empty == True:
            with open(f"{config.folder}\\CHECK.txt","a") as f:
                f.write(config.browser[ck])
                f.write("\n")
            continue
        """origin"""
        # path="D:\\Files_n_Data\\大创2023\\dianping_success\\test.xlsx"

        df_i.to_excel(station_excel,sheet_name=f"Sheet{i}")
        # station_excel.close()

        # with pd.ExcelWriter(config.path_excel, engine="openpyxl", mode='a') as writer:
        #     df_i.to_excel(writer,sheet_name=f'Sheet{i}')


        # write_data(df_i)
        print(f"当前爬取第{i}页")
        print(f"还剩下{config.length+config.start_page-i}页")
        print(df_i)
    try:
        station_excel.close()
    except Exception as e:
        print("excel未正常关闭")
    return


def create_folder(folder_name):
    path="D:\Files_n_Data\大创2023\dianping_success\\"+folder_name
    if not os.path.exists(path):
        print(f"创建文件夹{folder_name}...")
        os.makedirs(path)


if __name__ == "__main__":

    time_start = time.time()

    total_url = []
    # try:
    #     os.remove(f"{config.folder}\\CHECK.txt")
    #     print("CHECK.txt deleted successfully!")
    # except FileNotFoundError:
    #     print("File not FOUND")

    target_url = config.url
    total_url.append(target_url)
    # total_url = config.
    # 请求每个详情页
    for url in total_url:
        create_folder(config.folder)
        detail_page(url,cookies_l)
        # print(dp_name)
    print(total_url)

    time_end = time.time()
    run_time = time_end-time_start
    print("程序运行时间",run_time)
    print(datetime.now().strftime("%Y-%m-%d %H:%M"))

    # os.system("shutdown -s -t 100")