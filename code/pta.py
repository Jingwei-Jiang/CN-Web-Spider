# -*- encoding: utf-8 -*-
'''
@文件       :pta.py
@Description:Crawler experiment of computer network      
@Date       :2021/12/28 15:21:07
@Author     :frank
@version    :1.0
'''

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import requests
import time
import numpy
import cv2
import pandas as pd
import os
import sys

def cracking_captcha():
    # bg背景图片
    bg_img_src = web.find_element(By.XPATH,
        '/html/body/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[1]').get_attribute('src')
    # front可拖动图片
    front_img_src = web.find_element(By.XPATH,
        '/html/body/div[3]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[2]').get_attribute('src')
    # 保存图片
    with open("bg.jpg", mode="wb") as f:
        f.write(requests.get(bg_img_src).content)
    with open("front.jpg", mode="wb") as f:
        f.write(requests.get(front_img_src).content)
    # 将图片加载至内存
    bg = cv2.imread("bg.jpg")
    front = cv2.imread("front.jpg")
    # 将背景图片转化为灰度图片
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    # 将可滑动图片转化为灰度图片
    front = cv2.cvtColor(front, cv2.COLOR_BGR2GRAY)
    front = front[front.any(1)]
    # 用cv匹配精度最高的xy值
    result = cv2.matchTemplate(bg, front, cv2.TM_CCOEFF_NORMED)
    x, y = numpy.unravel_index(numpy.argmax(result), result.shape)
    # 找到可拖动区域
    div = web.find_element( By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]/div/div[2]/div[2]')
    ActionChains(web).drag_and_drop_by_offset(div, xoffset=y // 0.946, yoffset=0).perform()
    
def login_PTA(my_account, my_password):
    # 输入账号密码并点击登录
    account = web.find_element( By.XPATH,
        '/html/body/div[1]/div[2]/div/div[2]/form/div[1]/div/div/div[1]/div/div/div/input')
    password = web.find_element( By.XPATH,
        '/html/body/div[1]/div[2]/div/div[2]/form/div[1]/div/div/div[2]/div/div/div/input')
    account.send_keys(my_account)
    password.send_keys(my_password)
    web.find_element( By.XPATH,
        '/html/body/div[1]/div[2]/div/div[2]/form/div[2]/button').click()  # 找到登录按钮并点击
    web.find_element( By.XPATH,
        '/html/body/div[1]/div[2]/div/div[2]/form/div[2]/button/div/div').click()
    #多次尝试 
    for i in range(5):
        time.sleep(3)
        # 判断是否登录成功
        if web.current_url != login_url:
            print("login to PTA")
            break
        cracking_captcha()

def open_web(login_url):
    web = webdriver.Chrome(service=Service(r'chromedriver.exe'))
    web.implicitly_wait(5)
    # 调用WebDriver
    web.get(login_url)
    return web

def data_get():
    my_time = 2
    PTA_set = {}
    #获取题目集以及网址
    A_s = web.find_elements( By.CLASS_NAME, 'name_QIjv7' )
    urls = []
    for a in A_s:
        urls.append(a.get_attribute('href'))
    urls = urls[0:2] #前两个题目集的网址
    for url in urls:
        time.sleep(my_time)
        web.get(url)
        #题目集的名字
        list_name = web.find_element( By.XPATH,
                    '//*[@id="sparkling-daydream"]/div[2]/div[1]/div/div[1]/div/div').text
        #获取题目集内所有题目类型
        questions_type_list = web.find_element( By.CSS_SELECTOR,
                    "[class='pc-h container_3U5RB pc-gap-default']").find_elements( By.CSS_SELECTOR, "a")
        problem_set = {}
        questions_type_name = [] #题目类型
        url_type = []   #题目类型对应的链接
        #读取题目类型以及相应的链接
        for t in questions_type_list:
            questions_type_name.append( t.find_element( By.CSS_SELECTOR,
                    "[class='pc-text-raw']").text )
            url_type.append( t.get_attribute('href') )
        #遍历所有题目类型
        for i in range(len(questions_type_name)):
            time.sleep(my_time)
            web.get(url_type[i])
            trp_problems = web.find_elements( By.XPATH,
                    '//*[@id="sparkling-daydream"]/div[2]/div[1]/div/div[4]/div[2]/div/div[1]/table/tbody/tr')
            problems = []
            #获取题目类型下所有题目的名字，提交通过率以及链接
            #problem=[题目名字，提交通过率，链接]
            for tr in trp_problems:
                problem=[]
                problem.append(tr.find_element( By.XPATH, 'td[3]').text )  #题目的名字
                problem.append(tr.find_element( By.XPATH, 'td[5]').text )  #题目的通过率
                problem.append(tr.find_element( By.XPATH, 'td[3]/a').get_attribute('href') ) #题目的链接
                problems.append(problem)
            pta = []
            #获取具体题目描述
            for problem in problems:
                time.sleep(my_time)
                web.get(problem[2])
                problem_content = web.find_element( By.XPATH,
                    '//*[@id="sparkling-daydream"]/div[2]/div[1]/div/div[4]/div[1]/div[2]/div[1]/div/div/div/div').text
                problem.append(problem_content)  #problem的格式为[题目名字，提交通过率，链接,具体描述]
                pta.append(problem) #每道题的具体描述
            problem_set[questions_type_name[i]] = pta
            print("{}的{}已获取。".format(list_name,questions_type_name[i]))
        PTA_set[list_name] = problem_set
    return PTA_set

def write_to_txt( PTA_set ):
    for problem_set in PTA_set:
        with open( problem_set + ".txt","w") as f:
            set = PTA_set[problem_set]
            for p in set:
                f.write( p+':\n' )
                for l in set[p]:
                    f.write("题目: {}\n提交通过率: {}\n题目描述: {}\n链接: {}\n\n".format(l[0],l[1],l[3],l[2]))

def bubble_sort( question ):
    count = len(question)
    for i in range(1,count):
        for j in range(0,count-i):
            if question[j][0] > question[j+1][0]:
                question[j],question[j+1] = question[j+1],question[j]
    return question 

def print_PTA( PTA_set ):  
    question = []
    for problem_set in PTA_set:
        set = PTA_set[problem_set]
        for p in set:
            for l in set[p]:
                str=l[1].split('(')
                str1=str[1].split('%')
                problem = []
                problem.append(float(str1[0])*0.01) #题目通过率
                problem.append(l[0]) #题目名字
                problem.append(problem_set)  #题目集名称
                problem.append(p)    #题目类型
                problem.append(l[2]) #题目链接
                question.append(problem) #所有的题目放到question里

    bubble_sort(question) #所有题目按通过率升序
    #输出题目名字、题目集名称、题目类型、通过率和链接

    filepath = "E:\\vscode\\python\\pa"
    filename = "pta.txt"
    fullname = filepath + "\\" + filename
    standard_output = sys.stdout
    sys.stdout = open(fullname, "w+", encoding='utf-8')
    question_name=[]
    set_name=[]
    question_type=[]
    question_rate=[]
    question_url=[]
    for problem in question:
        question_name.append(problem[1])
        set_name.append(problem[2])
        question_type.append(problem[3])
        question_rate.append(problem[0])
        question_url.append(problem[4])
    data={
        "题目名字":question_name,
        "题目集名称":set_name,
        "题目类型":question_type,
        "通过率":question_rate,
        "链接":question_url
    }
    pd.set_option('display.max_rows',1000)
    pd.set_option('display.max_columns',1000)
    pd.set_option('display.width',1000)
    df=pd.DataFrame(data)
    print(df)
    sys.stdout.flush()
    sys.stdout.close()
    sys.stdout = standard_output

if __name__ == '__main__':
    login_url = 'https://pintia.cn/auth/login'
    web = open_web(login_url)
    my_account = '1121488332@qq.com'
    my_password = 'gcx889291'
    login_PTA(my_account, my_password)
    PTA_set  = data_get()
    write_to_txt(PTA_set)
    print_PTA(PTA_set)
