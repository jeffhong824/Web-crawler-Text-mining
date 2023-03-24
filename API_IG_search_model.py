from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command
import time 
import threading
import http.client
import socket

class Google_map():
    
    def __init__(self, head='--headless'): #--headless
        time_start = time.time() #開始計時
        print('create Google driver')
        chrome_options = Options()
        chrome_options = chrome_options
        chrome_options.add_argument(head)
        self.driver_map = webdriver.Chrome(options=chrome_options)
        time_end = time.time()    #結束計時
        time_c= time_end - time_start   #執行所花時間
        print('time cost', time_c, 's')
        
    def return_driver(self):
        return self.driver_map
    
    def search_loc(self,driver_map,spot_name):
        time_start = time.time() #開始計時
        driver_map.get("https://www.google.com.tw/maps/place/"+spot_name+"/")
        current_spot_loc = ''
        while current_spot_loc.find('@') == -1 :
            current_spot_loc = str(driver_map.current_url)

        start = current_spot_loc.find('@')+1
        end = current_spot_loc[start:].replace(',',' ',1).find(',')+start
        print(current_spot_loc[start:end],end = ' ')
        time_end = time.time()    #結束計時
        time_c= time_end - time_start   #執行所花時間
        print('time cost', time_c, 's')
        
        return current_spot_loc[start:end].split(',')

print('============= Create "Google map" class =============')
    
class IG_hot_hasgtag(): # headless

    def __init__(self, head='--head',account_number="forin.range.ig@gmail.com",password="forin.range.ig2022"): #--headless
        
        self.time_sleep = 2
        
        print('create IG driver & login')
        
        time_start = time.time() #開始計時
        def login(driver,account_number="forin.range.ig@gmail.com",password="forin.range.ig2022"):
            wait_login_success = False

            try:
                driver.get('https://www.instagram.com/accounts/login/')
                time.sleep(self.time_sleep)
                driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(account_number)
                driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
                driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[3]/button/div').click()
                try:
                    driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[3]/button/div').click()
                    wait_login_success = False
                except:
                    wait_login_success = True
            except:
                wait_login_success = False
                
            return wait_login_success
        
        # driver setting 
        chrome_options = Options()
        if head == '--headless' :
            chrome_options.add_argument(head)
        self.__chrome_options = chrome_options

        # web activate

        def open_driver(driver,account_number="forin.range.ig@gmail.com",password="forin.range.ig2022"):
            wait_login_success = False
            while wait_login_success == False :
                driver = webdriver.Chrome(options=self.__chrome_options)
                time.sleep(self.time_sleep)
                wait_login_success = login(driver,account_number,password)
                if wait_login_success == False :
                    driver.quit()
            return driver
                
        self.driver_search_hashtag = 0
        self.driver_search_hashtag = open_driver(self.driver_search_hashtag,account_number,password) # SightsinSight1@gmail.com # forin.range.ig@gmail.com
        time_end = time.time()    #結束計時
        time_c= time_end - time_start   #執行所花時間
        print('time cost', time_c, 's')
        
    def return_driver(self):
        return self.driver_search_hashtag

    def search_sight(self,driver,sight="#台北景點",stop_threshold = 100):
        
        driver.get('https://www.instagram.com/accounts/onetap/?next=%2F')
        wait_search_success = True
        already_run_times = 0
        success = False
        while wait_search_success :
            try:
                # type sight in input_bar
                driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input').send_keys(sight)
                time.sleep(3) # need upgrade
                driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input').send_keys(Keys.DOWN)
                # compare url
                login_url = driver.current_url
                now_url = driver.current_url
                while login_url==now_url :
                    driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input').send_keys(Keys.ENTER)
                    now_url = driver.current_url
                success = True
                wait_search_success = False
            except:
                already_run_times += 1
                if already_run_times <= stop_threshold :
                    success = False
                    wait_search_success = True
                else :
                    success = False
                    wait_search_success = False 
        return success
             
    def find_IG_link_info(self,driver):
        
        ## Running 
        # loop for get links
        wait_getlinks_success = True
        while wait_getlinks_success :
            try:
                href_list = driver.find_elements_by_css_selector("a")
                href_list_get = []
                if href_list != []:
                    link_check = True
                    for each_href in href_list[:9]:
                        href = each_href.get_attribute('href')
                        if str(href).find('/p/')!= -1 :
                            href_list_get.append(href)
                            print(href)
                        else:
                            link_check = False
                    if link_check!=True :
                        href_list_get = ["https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo"]
                    wait_getlinks_success = False
            except:
                wait_getlinks_success = True
        
        
        return href_list_get

    def search_Hot_hashtag(self,sight="#台北景點",show=False):
        time_start = time.time() #開始計時
        # setting
        self.__show = show
        # search sight
        success = self.search_sight(self.driver_search_hashtag,sight=sight,stop_threshold = 100)
        if success :
            Hot_hrefs = self.find_IG_link_info(self.driver_search_hashtag)
            time_end = time.time()    #結束計時
            time_c= time_end - time_start   #執行所花時間
            print('time cost', time_c, 's')
            return Hot_hrefs
        
    def search_hashtag_loaction_info(self,driver2,target_link):
        time_start = time.time() #開始計時
        self.__show = True
        driver2.get(target_link)

        # wait for page
        wait_web_success = True
        stop_threshold = 1000
        already_running_web = 0
        location = ''
        while wait_web_success:
            try:
                location = driver2.find_element_by_css_selector('[class="_aaqm"]').text # maintain-parameters
                if location != '':
                    wait_web_success = False
                else:
                    already_running_web += 1
                    wait_web_success = True
                    if already_running_web >= stop_threshold :
                        wait_web_success = False
            except:
                already_running_web += 1
                wait_web_success = True
                if already_running_web >= stop_threshold :
                    wait_web_success = False

#         # Location
#         try: 
#             location = driver2.find_element_by_css_selector('[class="_aaqm"]').text
#             if self.__show :
#                 print(location)
#         except:
#             location = ''

#         # Hasgtag
#         hashtags = []
#         try:
#             hashtag_list = driver2.find_elements_by_css_selector('[class=" xil3i"]')
#             for each_hashtag in hashtag_list :
#                 hashtag = each_hashtag.text
#                 hashtags.append(hashtag)
#                 if self.__show :
#                     print(hashtag,end=' ')
#         except:
#             hashtags = []

#         # IG
#         IGs = []
#         try:
#             IG_list = driver2.find_elements_by_css_selector('[class="notranslate"]')

#             for each_IG in IG_list :
#                 IG = each_IG.text
#                 IGs.append(IG)
#                 if self.__show :
#                     print(IG)
#         except:
#             IGs = []
   
        time_end = time.time()    #結束計時
        time_c= time_end - time_start   #執行所花時間
        print('time cost', time_c, 's')
        return location #,IGs # ,All_text,hashtags

print('============= Create "IG search" class =============')
    
