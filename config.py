import math
import time
global start_page,end_page, length, api_u, cookie_dic, browser, url
start_page = 
end_page = 
length = end_page-start_page
api_u = 

folder = "someCity_airport_T1"
time_avoid_replace = time.time()
path_excel = f"{folder}\\{folder}_{time_avoid_replace}.xlsx"



url = ""
# url_list =[]

num=0
cookie_list = []
file = open("cookies.txt",'r',encoding="utf-8")  #打开文件
file_data = file.readlines()
for line in file_data:
    cookie_list.append(line.strip())
    num=num+1
print(f"共有{num}个cookies")

ck_name = []

browser={}
i=0
print(len(ck_name))
for cook in cookie_list:
    if i > len(ck_name)-1:
        i=0
    # print(cook)
    browser[cook] = ck_name[i]
    i = i+1

