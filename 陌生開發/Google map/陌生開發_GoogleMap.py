# from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common import keys
from bs4 import BeautifulSoup
import pandas as pd
import threading
import http.client
import socket
import time
from time import sleep
from math import radians, cos, sin, asin, sqrt
import os
from tqdm import tqdm


path = 'D:/Record/Other/google_cold_email/'

'''
Readme

1. 開啟Google地圖 https://www.google.com/maps/place/
2. 輸入座標 25.0342883,121.5673522
3. 再搜尋 Key word
4. 不斷按下一面/下滑
5. 不知道獲取上限與距離 --> 需再後製算

P.S. 翻頁20面時最需注意! --> 上下滑動
P.S. 連星星數都沒有 --> 暫停營業

<<user_info>>
24 path = 'C:/Users/user/Desktop/AutoGoogle/'
319 ,executable_path=r"C:/Users/user/Desktop/AutoSW/chromedriver.exe"
321 ,executable_path=r"C:/Users/user/Desktop/AutoSW/chromedriver.exe"
'''

## ------------------ 控制Google map ------------------

def search_location(driver_map):
    searchbox = driver_map.find_element_by_xpath('//*[@id="searchboxinput"]')
    searchbox.send_keys(str(lat)+', '+str(lng))
    searchbox.send_keys(Keys.ENTER)
    
def loc_location(driver_map):
    lock = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[3]/button/span')
    lock.click()
    
def search_Keyword(driver_map):
    searchbox = driver_map.find_element_by_xpath('//*[@id="searchboxinput"]')
    searchbox.send_keys(keyword)
    searchbox.send_keys(Keys.ENTER)
    
def get_info(driver_map):
    All_a = driver_map.find_elements_by_tag_name("div")
    #print(All_a[2].text,flush=True)
    
def next_pag(driver_map):
    WebDriverWait(driver_map, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]/img'))).click()
    
## ------------------ 資料清洗 ------------------

def check_number(num):
    num = num.replace(' ','').replace('-','')
    success = False
    if 8<=len(num) and len(num)<=10 and num.isdigit() :
        success = True
    
    return success

def check_tw_web(web):
    success = False
    if web.find('.com')!= -1 or web.find('.tw')!= -1 :
        success = True
    
    return success

def collect_3_type(info):
    address = ''
    phone_number = ''
    web = ''

    info_list = info.split('\n')
    for id_,each in enumerate(info_list) :

        if id_ == 0 : # 預設第一個應該都是地址
            address = each
        else: # 後面順序可能不同
            Right_num = check_number(each) # 電話
            if Right_num :
                phone_number = each
            else :
                Right_web = check_tw_web(each) # 網站 --> 不見得有
                if Right_web :
                    web = each
                    
    return address,phone_number,web

## ------------------ 找Email ------------------

def find_email(text,path='./'):
    
    maybe_email_list = []
    maybe_email_position = text.find('@')
    stop_threshold = 120
    
    running_time2 = []
    while maybe_email_position!= -1 :
        
        time_start = time.time() #開始計時 
        running_time2.append(time_start)
        if running_time2[-1] - running_time2[0] >= stop_threshold :
            break

        maybe_email = ''
        closest_position1 = 0
        for searing_close_split_position in [' ',',','\n','\t',':','"','<','>',"/",'\\n','%','©','(',')','[',']','\xa0','$']:
            split_position = text[:maybe_email_position].rfind(searing_close_split_position)
            if split_position!= -1:
                if closest_position1 < split_position :
                    closest_position1 = split_position

        closest_position2 = 1000000
        for searing_close_split_position in [' ',',','\n','\t',':','"','<','>',"/",'\\n','%','©','(',')','[',']','\xa0','$']:
            split_position = text[maybe_email_position:].find(searing_close_split_position) 
            if split_position!= -1:
                if closest_position2 > split_position :
                    closest_position2 = split_position

        # 確認有一段string
        if closest_position1!=0 and closest_position2!=1000000 and (closest_position1+1 < closest_position2+maybe_email_position) and (closest_position1+1!=maybe_email_position and closest_position2!=maybe_email_position) :
            maybe_email = text[closest_position1+1:closest_position2+ maybe_email_position]
            

            # ======== 修改開頭與結尾位置 ========
            new_maybe_email = ''
            Start_position = False
            for each_string in maybe_email :
                if each_string.isdigit() == False and each_string not in ['-']:
                    Start_position = True
                if Start_position :
                    new_maybe_email += each_string

            if new_maybe_email.count('.com') == 1 :
                stop_position1 = new_maybe_email.find('.com')+4
                behind = new_maybe_email[ stop_position1: ]
                if behind.count('.') == 1 and len(behind)==3 :
                    new_maybe_email = new_maybe_email
                else :
                    new_maybe_email = new_maybe_email[:stop_position1]

                maybe_email = new_maybe_email    
                
            # 檢查是不是email格式
            email_only_one = []
            email_no_more_than2 = []
            with open(path+'email_must_one.txt','r') as file_email :
                for line in file_email:
                    email = line.replace('\n','')
                    email_only_one.append(email)
            with open(path+'email_no_more_than2.txt','r') as file_email :
                for line in file_email:
                    email = line.replace('\n','')
                    email_no_more_than2.append(email)
                    
            feet_email = True
            if maybe_email[0].isdigit()!= True and maybe_email.count('@')==1 and maybe_email.find('.png')==-1 and maybe_email.find('@media')==-1 :
                for each_check in email_only_one :
                    if maybe_email.count(each_check)!=1 :
                        feet_email = False
                for each_check in email_no_more_than2 :
                    if maybe_email.count(each_check)>1 :
                        feet_email = False
            else:
                feet_email = False
            if  feet_email :    
                maybe_email_list.append(maybe_email)
            
        text = text[maybe_email_position+1:]
        maybe_email_position = text.find('@')
        
        
        time_end = time.time()    #結束計時

        time_c= time_end - time_start   #執行所花時間
        #print('time cost', time_c, 's')        
    return maybe_email_list

def check_web_email(driver_web,web,check_all=True,email_top_x=10):
    
    Email_results_all = []
    result = []
    if web[0:4]!='http' :
        web = "https://" + web
    if web != "https://facebook.com" :
        #print(web,flush=True)

        driver_web.get(web)
        sleep(2)

        soup = BeautifulSoup(driver_web.page_source, 'html.parser')
        #Text = str(soup)
        #Text = soup.text
        Text = ''
        allnode_of_a = soup.find_all("a")
        for _ in allnode_of_a :
            try:
                Text += _.text +'\n'
                inside_web = _.get("href")
                if inside_web[0:4]!='http' :
                    inside_web = web+'/'+inside_web
                result.append(inside_web)
            except:
                continue
        #result = [ for _ in allnode_of_a]
        #print('---------------- web ----------------',flush=True)
        #print(result,flush=True)
        Email_results = find_email(Text,path=path)
        Email_results_all.extend(Email_results)
        if check_all :
            for each_web in result[:email_top_x]:
                try:
                    driver_web.get(each_web)
                    soup = BeautifulSoup(driver_web.page_source, 'html.parser')
                    #Text = str(soup)
                    Text = soup.text
                    Text = ''
                    allnode_of_a = soup.find_all("a")
                    for _ in allnode_of_a :
                        try:
                            Text += _.text +'\n'
                        except:
                            continue
                    Email_results = find_email(Text,path=path)
                    Email_results_all.extend(Email_results)
                except:
                    next_page = True
        #print('---------------- email ----------------',flush=True)
        #print(Email_results_all,flush=True)

    #else:
        #print('FB please',flush=True)
        
    return Email_results_all

def search_fb(driver_map,driver_web):

    web = ""
    info_dataframe_advanced = []

    handle = driver_map.window_handles

    all_fb_links = driver_map.find_elements_by_link_text("facebook.com")
    for each_fb in all_fb_links : 
        each_fb.click()
        sleep(2)

    handles = driver_map.window_handles
    for each_page in handles[1:] :
        if each_page!=handle :
            driver_map.switch_to.window(each_page)
            sleep(2)
            web = driver_map.current_url

            Email_results = check_web_email(driver_web,web,check_all=False,email_top_x=10)
            Email_results_list = set(Email_results)
            Email_results_list = list(Email_results_list)

            info_dataframe_advanced.extend(Email_results_list)

            driver_map.close()

    driver_map.switch_to.window(handles[0])

    return info_dataframe_advanced,web,handle

## ------------------ distance ------------------

def haversine(lon1, lat1, lon2, lat2):
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c= 2 * asin(sqrt(a))
    r = 6371
    return c * r * 1000
    
input_para = []
with open(path+'input.txt','r',encoding="utf-8") as file :
    for id_,line in enumerate(file) :
        if id_ != 2 :
            para = line.split("=")[1].replace(' ','').replace('\n','')
        else:
            para = line.split("=")[1].replace('\n','')
        input_para.append(para)

lat = str(input_para[0])
lng = str(input_para[1])
keyword = str(input_para[2])
company_limit = int(input_para[3])
email_top_x = int(input_para[4])
save_path = path+"output/"

if not os.path.isdir(save_path):
    os.mkdir(save_path) 

if __name__ == "__main__" :
    ## open web
    chrome_options = Options()
    chrome_options = chrome_options
    # chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})
    chrome_options.add_argument('log-level=3')
    driver_map = webdriver.Chrome(options=chrome_options) # ,executable_path=r"C:/Users/user/Desktop/AutoSW/chromedriver.exe"
    driver_map.get("https://www.google.com.tw/maps/place/"+lat+'+'+lng)
    driver_web = webdriver.Chrome(options=chrome_options) # ,executable_path=r"C:/Users/user/Desktop/AutoSW/chromedriver.exe"

    ## search location
    #search_location(driver_map)
    sleep(5)
    loc_location(driver_map)
    sleep(5)

    ## search keyword
    search_Keyword(driver_map)
    sleep(5)

    ## setting 
    page_now = 1
    info_dataframe = []
    long_email = 0

    ## running 
    for page_top in tqdm(range(1,company_limit)):

        page = page_top*2 + 1
        
        #print('==================== page'+str(page_now)+' ====================',flush=True)
        
        Fail_time = 0
        Fail = True
        stop_threshold = 300
        running_time1 = []
        while Fail :
            try:
                time_start = time.time() #開始計時 
                running_time1.append(time_start)
                if running_time1[-1] - running_time1[0] >= stop_threshold :
                    break
                
                #print('Fail_time: '+str(Fail_time))
                This_collect_success = False
                driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page)+']/div/a').click()
                sleep(5)

                Already_collect = []

                name = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/div[1]/h1/span[1]').text
                #print(name,flush=True)
                Already_collect.append(name)
                
                try:
                    star = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span/span/span[1]').text
                    #print(star,flush=True)
                    google_info = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]').text
                    comment = google_info.split('\n')[2].replace(' 則評論','').replace(',','').replace('·','').replace('$','')
                    type_ = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button').text
                    #print(comment,flush=True)
                    
                except:
                    #print('Maybe Suspend business',flush=True)
                    Fail = False
                    break
                    
                Already_collect.append(type_)
                Already_collect.append(star)
                Already_collect.append(comment)
                Already_collect.append(google_info)
                
                
                google_map_link = driver_map.current_url
                start_loc_position = google_map_link.find("@")+1
                google_map_link_split = google_map_link[start_loc_position:].split(",")
                company_lat = google_map_link_split[0]
                company_lng = google_map_link_split[1]
                
                distance_m = haversine(float(lng[:-1]), float(lat[:-1]), float(company_lng), float(company_lat))
                
                #print(company_lat,flush=True)
                #print(company_lng,flush=True)
                #print(distance_m,flush=True)
                #print(google_map_link,flush=True)
                Already_collect.extend([company_lat,company_lng,distance_m,google_map_link])


                #print('--------- info ---------',flush=True)

                work_time = True
                try:
                    driver_map.find_element_by_class_name("OdW2qd").click()
                except:
                    work_time = False
                
                
                info = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]').text
                if info=='' or info=='提出修改建議':
                    info = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]').text
                    if info=='' or info=='提出修改建議':
                        info = driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[11]').text 
                if info=='' or info=='提出修改建議':
                    info = '提出修改建議'

#                 print(info,flush=True)
                #print('--------- info ---------',flush=True)
                address,phone_number,web = collect_3_type(info)
                
                
                start_position = info.find("星期")
                end_position = info.find("提供營業時間修改建議")
                if start_position!=-1 and end_position!=-1:
                    work_time = info[start_position:end_position]
                else:
                    work_time = ''
                

                ## Email
                Already_collect_email = []

                # Email - FB
                try:
                    Email_results1,web_fb,handle = search_fb(driver_map,driver_web)
                    #print("Email_results1: ",Email_results1,flush=True)
                    Already_collect_email.extend(Email_results1)
                except:
                    #print("Email_results1: None",flush=True)
                    Already_collect_email.extend([])

                # Email - web
                try:
                    Email_results2 = check_web_email(driver_web,web,check_all=False,email_top_x=email_top_x)
                    #print("Email_results2: ",Email_results2,flush=True)
                    Already_collect_email.extend(Email_results2)
                except:
                    #print("Email_results2: None",flush=True)
                    Already_collect_email.extend([])
                    
                if web=="facebook.com" and web_fb!="":
                    Already_collect.extend([info,address,phone_number,work_time,web_fb])
                else:
                    Already_collect.extend([info,address,phone_number,work_time,web])


                info_dataframe_advanced_list = set(Already_collect_email)
                info_dataframe_advanced_list = list(info_dataframe_advanced_list)
                #Already_collect.append(info_dataframe_advanced_list)
                if long_email < len(info_dataframe_advanced_list) :
                    long_email = len(info_dataframe_advanced_list)
                
                Already_collect.extend(info_dataframe_advanced_list)
                This_collect_success = True
                Fail_time = 0
                break
            except:
                #print('Fail_time: '+str(Fail_time))
                #print("Can't find",flush=True)
                #driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-4)+']/div/a').click()
                #driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').click()
                try:
                    if Fail_time%2 == 0 :
                        sleep(1)
                        #print('--down',flush=True)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                        sleep(2)

                    if Fail_time%3 == 0 :
                        sleep(1)
                        #print('--up',flush=True)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.UP)
                        driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.UP)
                        sleep(2)

                    #driver_map.execute_script("window.scrollBy(0, 1000);")
                    sleep(1)
                    Fail_time += 1    
                except:
                    try:
                        handles = driver_map.window_handles
                        for each_page in handles[1:] :
                            driver_map.switch_to.window(each_page)
                            driver_map.close()
                        driver_map.switch_to.window(handles[0])

                        if Fail_time%10 == 0 :
                            sleep(1)
                            #print('--down',flush=True)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.DOWN)
                            sleep(2)

                        if Fail_time%20 == 0 :
                            sleep(1)
                            #print('--up',flush=True)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.UP)
                            driver_map.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div['+str(page-2)+']/div/a').send_keys(keys.Keys.UP)
                            sleep(2)

                        #driver_map.execute_script("window.scrollBy(0, 1000);")
                        sleep(1)
                        Fail_time += 1
                    except:
                        break
                    
                #print('('+str(Fail_time)+')',end= ' ',flush=True)
                
            if Fail_time >= 100 :
                Fail = False
                
        if Fail_time >= 1000 :
            break
                
        page_now += 1
        
        if This_collect_success :
            info_dataframe.append(Already_collect)
            
        columns=["Company","Type","Star","Comment","Google_comment","Longitude(經度)","Latitude(緯度)","Distance(直線距離/公尺)","Google_map","Information","Address","Phone_number","Business_hours","Web_address"]    
        email_columns = ['Email'+str(name) for name in range(1,long_email+1)]
        columns.extend(email_columns)

        info_dataframe_running = pd.DataFrame(info_dataframe,columns=columns)
        try:
            info_dataframe_running.to_excel(save_path+keyword+'_'+str(lng)+'_'+str(lat)+'_running.xlsx')
        except:
            info_dataframe_running.to_excel(save_path+keyword+'_'+str(lng)+'_'+str(lat)+'_running2.xlsx')
        
    columns=["Company","Type","Star","Comment","Google_comment","Longitude(經度)","Latitude(緯度)","Distance(直線距離/公尺)","Google_map","Information","Address","Phone_number","Business_hours","Web_address"]    
    email_columns = ['Email'+str(name) for name in range(1,long_email+1)]
    columns.extend(email_columns)

    info_dataframe = pd.DataFrame(info_dataframe,columns=columns)
    info_dataframe_running.to_excel(save_path+keyword+'_'+str(lng)+'_'+str(lat)+'.xlsx')
    driver_map.quit()
    driver_web.quit()
    #print("========================== Finish ==========================",flush=True)
