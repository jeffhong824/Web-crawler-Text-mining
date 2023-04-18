from selenium.webdriver.chrome.options import Options # 爬蟲
from selenium.webdriver import Chrome # Chrome driver
from bs4 import BeautifulSoup # 解析html
import requests
import math # 無條件進位 可以不用
import pandas as pd # 輸出檔案
from time import sleep
from tqdm import tqdm
import re
import os
import warnings
warnings.filterwarnings("ignore")

def run(cate_name_eng_lv1,cate_name_eng_lv3,county_id,country_name,save_path):
    def copy_info(driver,count_time,Companys_name,Companys_link,Companys_phone): # 用來把黃頁 當面的公司資訊抓下來
        all_h3 = driver.find_elements_by_tag_name('h3') # 限縮
        for each_h3 in all_h3 :
            try:
                company_href = each_h3.find_element_by_tag_name('a').get_attribute('href')
                count_time += 1
    #             print(count_time,each_h3.text,company_href)

                company_href_end = company_href.rfind('/')+1
                if company_href_end != len(company_href) : # 代表後面極有可能跟著電話號碼
                    phone = company_href[company_href_end:]
                    if phone.find('-') != -1 :
                        phone = phone[:phone.rfind('-')]
                else:
                    phone = ''

                Companys_name.append(each_h3.text)
                Companys_link.append(company_href)
                Companys_phone.append(phone)
            except:
                break #not_a_company or not_in_search
        return driver,count_time,Companys_name,Companys_link,Companys_phone



    def extract_phone_numbers(text):
        # 電話號碼的正則表達式
    #     phone_regex = r'\d{8}|\d{9}|(?:\d{3}-)?\d{7}'
        phone_regex = r'(?:\+?886\-?)?(0\d{1,4}[\-]?\d{6,8})'

        # 搜尋字串中所有符合正則表達式的字串
        phone_numbers = re.findall(phone_regex, text)

        # 電子郵件地址的正則表達式
    #     email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # 搜尋字串中所有符合正則表達式的字串
        phone_numbers = re.findall(phone_regex, text)
    #     emails = re.findall(email_regex, text)

        # check
        phone_numbers_check = ''
        for each_phone in phone_numbers :
            phone_clear = each_phone.replace('-','').replace('+886','0').replace('+','').replace('(','').replace(')','')
            if phone_clear[0] == '0' and  len(phone_clear)<= 12 and len(phone_clear)>= 9:
                if phone_clear[:2] in ['02','03','04','05','06','07','08'] or  phone_clear[:3] in ['037','049','089','082','0826','0836']:
                    phone_numbers_check += phone_clear+','

        # 回傳擷取出的電話號碼和電子郵件地址
        return phone_numbers_check[:-1]#, emails

    def 商業司API(format_,Company_Name,Company_Status,skip,top):
        Company_Status_type = '''
        01	核准設立
        02	停業
        03	歇業／撤銷
        04	申覆（辯）期
        05	遷他縣市
        06	列入廢止中
        07	廢止
        08	破產
        09	設立無效

        '''

        r = requests.get('http://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format='+format_+'&$filter=Company_Name like '+Company_Name+' and Company_Status eq '+Company_Status+'&$skip='+skip+'&$top='+top, verify=False)
        list_of_dicts = r.json() # 可能找不到

        return list_of_dicts

    def run_商業司(driver,target): # 本系統限制使用者間隔2秒鐘才能進行下一次查詢! #此def 執行時間較久 可用確認網址不同等方式優化

        # columns = []
        columns = ['商業司爬蟲_客戶名稱','搜尋名稱','統一編號', '登記機關', '登記現況', '地址', '資料種類', ' 核准設立日期 ', '核准變更日期','登記編號','詳細資料']
#         columns = ['商業司爬蟲_客戶名稱','搜尋名稱','基本資料/商業登記基本資料']
        insides = []
        fail_target = []

        def wait(driver):
            try: # 等了2秒也失敗，再次返回
                sleep(2)
                driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table/tbody/tr/td/span/a').click()
            except:
                out_of_2sec = False
            return driver

        for each in tqdm(target):
            if len(each) >= 2 :
        #         driver.get("https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?disj=CAB03FDB1F4716D6F6B4BB9389EB9F9B&fhl=zh_TW")
        #         driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[3]').click()
        #         driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[5]').click()
        #         driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[7]').click()
        #         driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[9]').click()
                each_space = each.replace('-',' ')
                eachs = each_space.split(' ')
                if len(eachs) > 1:
                    check_company_keyword = ['公司','有限公司','工程','電器','行']
                    for each_name_in_pro in eachs :
                        found = False
                        for check_company_keyword_each in check_company_keyword :
                            if each_name_in_pro.find(check_company_keyword_each) != -1 :
                                found = True
                                break
                        if found :
                            break
                    if found :
                        each = each_name_in_pro

                try:
                    sleep(2) # 本系統限制使用者間隔2秒鐘才能進行下一次查詢!
                    driver.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul/li/a').click() # 重新查詢
                except:
                    no_need2_retrun = True

                driver = wait(driver) # 等等看

                driver.find_element_by_name('qryCond').clear()
                driver.find_element_by_name('qryCond').send_keys(each)
                driver.find_element_by_id('qryBtn').click()
                sleep(2)
                try:
                    inside = []
                    # 重新整理網頁 --> 避免搜尋過程跳出驗證碼
    #                 driver.refresh()
                    try:
                        company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text
                    except:
                        driver = wait(driver) # 等等看
                        try:
                            company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text
                        except: # 再嘗試，因經費有限，已時間&機率換取正確性
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            check_result = str(soup)
                            if check_result.find('很抱歉，我們無法找到符合條件的查詢結果。') == -1: # 有結果但被鎖 --> 再嘗試，因經費有限，已時間&機率換取正確性
                                driver.quit()
                                chrome_options = Options()
                            #     chrome_options.add_argument('--headless') # No interface operation
                                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
                                driver = Chrome(options=chrome_options) # for inner primers
                                driver.get("https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?disj=CAB03FDB1F4716D6F6B4BB9389EB9F9B&fhl=zh_TW")
                                driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[3]').click()
                                driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[5]').click()
                                driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[7]').click()
                                driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[9]').click()
                                driver.find_element_by_name('qryCond').clear()
                                driver.find_element_by_name('qryCond').send_keys(each)
                                driver.find_element_by_id('qryBtn').click()
                                sleep(2)
                                try:
                                    company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text
                                except:
                                    driver = wait(driver) # 等等看
                                    try:
                                        company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text
                                    except:
                                        driver.quit()
                                        chrome_options = Options()
                                    #     chrome_options.add_argument('--headless') # No interface operation
                                        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
                                        driver = Chrome(options=chrome_options) # for inner primers
                                        driver.get("https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?disj=CAB03FDB1F4716D6F6B4BB9389EB9F9B&fhl=zh_TW")
                                        driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[3]').click()
                                        driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[5]').click()
                                        driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[7]').click()
                                        driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[9]').click()
                                        driver.find_element_by_name('qryCond').clear()
                                        driver.find_element_by_name('qryCond').send_keys(each)
                                        driver.find_element_by_id('qryBtn').click()
                                        sleep(2)
                                        try:
                                            company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text
                                        except:
                                            driver = wait(driver) # 等等看
                                            company = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').text

                            else:
                                no_result = True

                    output = driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[2]').text

                    inside.append(company)
                    inside.append(each)
                    output_list = output.split(' , ')
                    for each_space in columns[2:-1] : # 8個資料
                        add_info = ''
                        for each in output_list : # 照順序加入inside
                            if each.split('：')[0] == each_space :
                                add_info = each.split('：')[1]
                        inside.append(add_info)

                    driver.find_element_by_xpath('//*[@id="vParagraph"]/div/div[1]/a').click() # 下一面
                    sleep(2)

                    detail_output = driver.find_element_by_class_name('table-responsive').text # 每一面檔案內容欄位名稱不同、數量不同，需要規則
                    inside.append(detail_output)

                    insides.append(inside)
                except: # 查無資料
                    fail_target.append(each)
                    insides.append(['','', '', '', '', '', '', '','','',''])
            else:
                insides.append(['','', '', '', '', '', '', '','','',''])


        Result = pd.DataFrame(insides,columns=columns)

        return Result,fail_target,driver

    def Google_find_phone(driver,each,inside):
        try:
            driver.get('https://www.google.com.tw/search?q='+each)
            sleep(2)
            try:
                Google_info = driver.find_element_by_class_name("I6TXqe").text
                if Google_info.find('電話： ') != -1 :
                    Google_info_phone_start = Google_info.find('電話： ')+len('電話： ')
                    Google_info_phone_end = Google_info[Google_info_phone_start:].find('\n') + Google_info_phone_start
                    phone_number = str(Google_info[Google_info_phone_start:Google_info_phone_end])
                else:
                    phone_number = ''
            except:
                phone_number = ''
        except:
            phone_number = ''

        inside.append(phone_number)
        return inside
    
    
    
    chrome_options = Options()
#     chrome_options.add_argument('--headless') # No interface operation
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    driver = Chrome(options=chrome_options) # for inner primers

    link = 'https://www.iyp.com.tw/showroom.php?cate_name_eng_lv1='
    print(link+cate_name_eng_lv1+'&cate_name_eng_lv3='+cate_name_eng_lv3+'&a_id='+str(county_id))

    driver.get(link+cate_name_eng_lv1+'&cate_name_eng_lv3='+cate_name_eng_lv3+'&a_id='+str(county_id))

    # ======================= info =======================
    search_solution = driver.find_element_by_id("search-title").text
    print(search_solution)
    count_start = search_solution.find('共有 ')+len('共有 ')
    count_end = search_solution.find(' 筆資料')
    target_companys = int(search_solution[count_start:count_end])
    index = [country_name + '_'+ str(country_time_id+1) for country_time_id in range(target_companys)]
    pages = math.ceil(target_companys/10) 
    click_next_page_time = int(target_companys/10) 
    print('目標: '+str(target_companys)+'筆')
    print('共有: '+str(pages)+'面')

    # ======================= step1 ======================
    Companys_name,Companys_link,Companys_phone = [],[],[]

    print('共要翻: '+str(click_next_page_time)+'次面')
    count_time = 0
    for next_page_time in tqdm(range(click_next_page_time)):
        driver,count_time,Companys_name,Companys_link,Companys_phone = copy_info(driver,count_time,Companys_name,Companys_link,Companys_phone)
#         driver.find_element_by_class_name("next").click() # 這面搜尋完了
        try:
            driver.find_element_by_class_name("next").click() # 這面搜尋完了
        except: # 碰到廣告
            driver.get(link+cate_name_eng_lv1+'&cate_name_eng_lv3='+cate_name_eng_lv3+'&a_id='+str(county_id)+'&p='+str(next_page_time+1))
    driver,count_time,Companys_name,Companys_link,Companys_phone = copy_info(driver,count_time,Companys_name,Companys_link,Companys_phone)

    Result1 = pd.DataFrame([Companys_name,Companys_link,Companys_phone],index=['黃頁_公司','網址','電話']).T

    # ======================= step1.5 ======================
    print('檢查需用外部首頁補充的公司...')
    # 補充無電話者
    outside_url = []
    
    for none_id,none in enumerate(tqdm(Result1['電話'].values)) :
        if none == '':
            try:
                driver.get(Result1['網址'].values[none_id])
                sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                company_self_page = str(soup)
                phone_numbers = extract_phone_numbers(company_self_page)
                outside_url.append(phone_numbers)
            except:
                outside_url.append('') # error
        else:
            outside_url.append('') # pass

    Result1['外部連結_電話'] = outside_url
    
    non_phone_numbers = list(Result1['電話'].values).count('')
    get_outside_phone = len(outside_url) - outside_url.count('')
    lack_phones = non_phone_numbers - get_outside_phone
    print('收集完畢,原少'+str(non_phone_numbers)+'筆'+';透過外部連結補充'+str(get_outside_phone)+'筆;剩餘'+str(lack_phones)+'筆')
#     print('缺少: '+str(non_phone_numbers))

    # ======================= step2 ======================
    print('商業司資料收集')
    target = Result1['黃頁_公司'].values

    driver.get("https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do?disj=CAB03FDB1F4716D6F6B4BB9389EB9F9B&fhl=zh_TW")
    driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[3]').click()
    driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[5]').click()
    driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[7]').click()
    driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[9]').click()

    Result2,fail_target,driver = run_商業司(driver,target)
    
    # ======================= step3 ======================
    targets = Result2['搜尋名稱'].values
    format_ = 'json'
    Company_Status = '01'
    skip = '0'
    top = '10'
    
    Business_Accounting_NOs,Company_Names,Company_Status_Descs,Capital_Stock_Amounts,Paid_In_Capital_Amounts,Responsible_Names,Register_Organizations,Register_Organization_Descs,Company_Locations,Company_Setup_Dates,Change_Of_Approval_Datas = [],[],[],[],[],[],[],[],[],[],[]
    for each in targets :
        Company_Name = each
        try:
            list_of_dicts = 商業司API(format_,Company_Name,Company_Status,skip,top)
            Business_Accounting_NO = list_of_dicts[0]['Business_Accounting_NO'] ; Business_Accounting_NOs.append(Business_Accounting_NO)
            Company_Name = list_of_dicts[0]['Company_Name'] ; Company_Names.append(Company_Name)
#             Company_Status = list_of_dicts[0]['Company_Status']
            Company_Status_Desc = list_of_dicts[0]['Company_Status_Desc'] ; Company_Status_Descs.append(Company_Status_Desc)
            Capital_Stock_Amount = list_of_dicts[0]['Capital_Stock_Amount'] ; Capital_Stock_Amounts.append(Capital_Stock_Amount)
            Paid_In_Capital_Amount = list_of_dicts[0]['Paid_In_Capital_Amount'] ; Paid_In_Capital_Amounts.append(Paid_In_Capital_Amount)
            Responsible_Name = list_of_dicts[0]['Responsible_Name'] ; Responsible_Names.append(Responsible_Name)
            Register_Organization = list_of_dicts[0]['Register_Organization'] ; Register_Organizations.append(Register_Organization)
            Register_Organization_Desc = list_of_dicts[0]['Register_Organization_Desc'] ; Register_Organization_Descs.append(Register_Organization_Desc)
            Company_Location = list_of_dicts[0]['Company_Location'] ; Company_Locations.append(Company_Location)
            Company_Setup_Date = list_of_dicts[0]['Company_Setup_Date'] ; Company_Setup_Dates.append(Company_Setup_Date)
            Change_Of_Approval_Data = list_of_dicts[0]['Change_Of_Approval_Data'] ; Change_Of_Approval_Datas.append(Change_Of_Approval_Data)
        except:
            Business_Accounting_NOs.append('')
            Company_Names.append('')
#             Company_Status = list_of_dicts[0]['Company_Status']
            Company_Status_Descs.append('')
            Capital_Stock_Amounts.append('')
            Paid_In_Capital_Amounts.append('')
            Responsible_Names.append('')
            Register_Organizations.append('')
            Register_Organization_Descs.append('')
            Company_Locations.append('')
            Company_Setup_Dates.append('')
            Change_Of_Approval_Datas.append('')            

    Result2['商業司API_Business_Accounting_NO'] = Business_Accounting_NOs
    Result2['Company_Name'] = Company_Names
    Result2['Company_Status_Desc'] = Company_Status_Descs
    Result2['Capital_Stock_Amount'] = Capital_Stock_Amounts
    Result2['Paid_In_Capital_Amount'] = Paid_In_Capital_Amounts
    Result2['Responsible_Name'] = Responsible_Names
    Result2['Register_Organization'] = Register_Organizations
    Result2['Register_Organization_Desc'] = Register_Organization_Descs
    Result2['Company_Location'] = Company_Locations
    Result2['Company_Setup_Date'] = Company_Setup_Dates
    Result2['Change_Of_Approval_Data'] = Change_Of_Approval_Datas
            
    # ======================= step4 ======================
    print('Google電話收集')
    inside_google = []
    for company_in_黃頁_id,company_in_黃頁 in enumerate(tqdm(target)) :
        inside_google = Google_find_phone(driver,company_in_黃頁,inside_google)
        
    Result2['Google_電話'] = inside_google
    
    # ======================= combine ======================
    Result_combine = Result1.merge(Result2,how='inner', left_index=True, right_index=True)
    Result_combine.index = index
    Result_combine.to_excel(save_path+country_name+'.xlsx')

    driver.quit() # again
    
    
if __name__ == '__main__' :    
    save_path = r"D:/Record/Other/團隊/case/"
    country_names = {3:'基隆市',7:'新竹縣',1:'宜蘭縣',4:'新北市',5:'桃園市',6:'台北市',8:'苗栗縣',9:'台中市',11:'彰化縣',12:'南投縣',13:'雲林縣',14:'嘉義縣',15:'台南市',18:'高雄市',21:'屏東縣',20:'花蓮縣',22:'台東縣',17:'澎湖縣'}

    dirPath_result = [f for f in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, f))]
    for county_id in list(country_names.keys()) :
        cate_name_eng_lv1 = 'appliances'
        cate_name_eng_lv3 = 'air-conditioners'
        country_name = country_names[county_id]
        if country_name+'.xlsx' in dirPath_result :
            continue
        print(country_name)
        run(cate_name_eng_lv1,cate_name_eng_lv3,county_id,country_name,save_path)
