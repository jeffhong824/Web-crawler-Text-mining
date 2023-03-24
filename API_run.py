from flask import Flask , request , jsonify
from flask_cors import CORS # 可以設定只從哪個網域
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command
import time 
import threading
import http.client
import socket
from API_IG_search_model import IG_hot_hasgtag,Google_map

def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return "Alive"
    except (socket.error, http.client.CannotSendRequest):
        return "Dead"

def check_driver(driver_id = 0): # 檢查是否已有
    
    status = True
    
    try:
        # Google class ver
        #driver_list[driver_id][0]
        #driver_list[driver_id][2]
        #each_driver_status1 = get_status(driver_list[driver_id][1])
        #each_driver_status2 = get_status(driver_list[driver_id][3])
        
        driver_list[driver_id][0]
        each_driver_status1 = get_status(driver_list[driver_id][1])
        if each_driver_status1=='Alive' :
            print('driver'+str(driver_id+1)+'Alive')
        else:
            print('driver'+str(driver_id+1)+'Dead')
            status = False
        driver_list[driver_id][1].window_handles
    except:
        print('driver'+str(driver_id+1)+'Dead')
        status = False
        
    return status        

def user(could_run_position,sight,IG_running_class,IG_driver): # ,Google_running_class,Google_driver
    # 快速提供前端 9篇網址 呈現視覺圖片
    Hot_hrefs = IG_running_class.search_Hot_hashtag(sight=sight)
    driver_return_list[could_run_position][0] = Hot_hrefs
    #yield jsonify({'Hot_hrefs': Hot_hrefs })
    All_position_info = []
    All_position_info_loc = []
    if Hot_hrefs != ["https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo"] :
        # 依序提供景點資訊 --> 匹配的到資料庫地點的 (可點選資訊、加到我的最愛)
        for list_id,each_href in enumerate(Hot_hrefs):
            print(each_href)
            Position_info = IG_running_class.search_hashtag_loaction_info(IG_driver,each_href)
            print(Position_info)
            All_position_info.append(Position_info)
            '''
            try: 
                if Position_info != '':
                    Spot_position = Spots.index(Position_info)
                    print('--> Exact match',Spot_position)
                    driver_return_list[could_run_position][list_id+1] = [Position_info,'Exact match',Spot_position]
                    #yield jsonify({'each_href': each_href,'Position_info': Position_info,'match': 'Exact match','Spot_position': str(Spot_position) })
                    All_position_info_loc.append([1,Spot_position])
                else:
                    print('--> Mismatch')
                    driver_return_list[could_run_position][list_id+1] = [Position_info,'Mismatch',-1]
            except:
                print('--> Mismatch')
                driver_return_list[could_run_position][list_id+1] = [Position_info,'Mismatch',-1]
                #yield jsonify({'each_href': each_href,'Position_info': Position_info,'match': 'Mismatch','Spot_position': '-1' })
                # google map loc
                #current_spot_loc = Google_running_class.search_loc(Google_driver,Position_info)
                #All_position_info_loc.append([0,current_spot_loc])
            '''
            driver_return_list[could_run_position][list_id+1] = Position_info
            print('================================')
        
    return Hot_hrefs,All_position_info,All_position_info_loc

def user_API(user_id,user_input_from_web,driver_status):
    CD = 2 # maintain-parameters
    user_input = str(user_input_from_web)
    if user_input[0]!= "#" :
        user_input = '#'+user_input

    try:
        could_run_position = driver_status.index(0)
        print('driver'+str(could_run_position+1))
        driver_status[could_run_position] = 1
        driver_request_id[could_run_position] = user_id
        driver_request_time.append(user_id)
        driver_request_time_success.append(True)
        driver_request_time_success_which.append('driver'+str(could_run_position+1))
        Hot_hrefs,All_position_info,All_position_info_loc = user(could_run_position,user_input,driver_list[could_run_position][0],driver_list[could_run_position][1]) # ,driver_list[could_run_position][2],driver_list[could_run_position][3]
        time.sleep(CD)
        driver_return_list[could_run_position][0] = -1
        driver_return_list[could_run_position][1:] = [-1 for each_info in range(9)]
        driver_status[could_run_position] = 0
    except:
        print('伺服器繁忙中 請燒等')
        driver_request_time.append(user_id)
        driver_request_time_success.append(False)
        driver_request_time_success_which.append('driver'+str(0))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app) 

@app.route('/restart')
def create_check_driver_status():
    driver_search_number = 2 

    # driver status
    try:
        print('driver原已存在',driver_status)
    except:
        #driver_status = [-1 , -1, -1, -1, -1] # maintain-driver-quantity\
        #driver_status = [-1 , -1]
        driver_status = [-1 for adding in range(driver_search_number) ]

    # maintain-driver-quantity
    for driver_id in range(driver_search_number):
        locals()['driver_status'+str(driver_id+1)] = check_driver(driver_id = driver_id)
        if locals()['driver_status'+str(driver_id+1)] == False:
            # 搭配動畫過程 登入driver
            locals()['IG_running_class'+str(driver_id+1)]  = IG_hot_hasgtag(account_number=account_numbers[driver_id],password=password[driver_id])
            locals()['IG_driver'+str(driver_id+1)]  = locals()['IG_running_class'+str(driver_id+1)].return_driver()
            driver_status[driver_id] = 0
    '''
    driver_status1 = check_driver(driver_id = 0)
    if driver_status1 == False:
        # 搭配動畫過程 登入driver
        IG_running_class1 = IG_hot_hasgtag(account_number="forin.range2022",password="forin.range.ig2022") # forin.range.ig@gmail.com
        IG_driver1 = IG_running_class1.return_driver()
        #Google_running_class1 = Google_map()
        #Google_driver1 = Google_running_class1.return_driver()
        driver_status[0] = 0

    driver_status2 = check_driver(driver_id = 1)   
    if driver_status2 == False:
        IG_running_class2 = IG_hot_hasgtag(account_number="sightsinsight1",password="forin.range.ig2022") # SightsinSight1@gmail.com
        IG_driver2 = IG_running_class2.return_driver()
        #Google_running_class2 = Google_map()
        #Google_driver2 = Google_running_class2.return_driver()
        driver_status[1] = 0
    ''' 
    '''
    driver_status3 = check_driver(driver_id = 2)   
    if driver_status3 == False:
        IG_running_class3 = IG_hot_hasgtag(account_number="sightsinsight2",password="forin.range.ig2022") # jeffhong8244@gmail.com
        IG_driver3 = IG_running_class3.return_driver()
        #Google_running_class3 = Google_map()
        #Google_driver3 = Google_running_class3.return_driver()
        driver_status[2] = 0
        
    driver_status4 = check_driver(driver_id = 3)   
    if driver_status4 == False:
        IG_running_class4 = IG_hot_hasgtag(account_number="sightsinsight3",password="forin.range.ig2022") # jeffhong824444@gmail.com
        IG_driver4 = IG_running_class4.return_driver()
        #Google_running_class4 = Google_map()
        #Google_driver4 = Google_running_class4.return_driver()
        driver_status[3] = 0
        
    driver_status5 = check_driver(driver_id = 4)   
    if driver_status5 == False:
        IG_running_class5 = IG_hot_hasgtag(account_number="sightsinsight4",password="forin.range.ig2022") # tingchun.tc.hung@gmail.com
        IG_driver5 = IG_running_class5.return_driver()
        #Google_running_class5 = Google_map()
        #Google_driver5 = Google_running_class5.return_driver()
        driver_status[4] = 0

    '''
    # driver status
    #driver_list = [ [IG_running_class1,IG_driver1,Google_running_class1,Google_driver1],[IG_running_class2,IG_driver2,Google_running_class2,Google_driver2] ]
    #driver_list = [ [IG_running_class1,IG_driver1],[IG_running_class2,IG_driver2],[IG_running_class3,IG_driver3],[IG_running_class4,IG_driver4],[IG_running_class5,IG_driver5] ]
    driver_list = [ [IG_running_class1,IG_driver1],[IG_running_class2,IG_driver2] ]

    print('Driver 都建立完成 可以開始搜尋')
    return 'reBuild'

# maintain-driver-quantity
@app.route('/health',methods=['GET'])
def return_server_status():

    return "OK"
    
# maintain-driver-quantity
@app.route('/driver_health',methods=['GET'])
def return_driver_status():
    driver_search_number = 2
    driver_health = []
    for driver_id in range(driver_search_number):
        driver_health.append(check_driver(driver_id))
    return jsonify({'driver_health': driver_health})

# maintain-driver-quantity
@app.route('/driver_status',methods=['GET'])
def return_status():

    return jsonify({'driver_status': driver_status,'driver_request_from':driver_request_id})

@app.route('/driver1',methods=['GET'])
def return_driver1_status():
    try:
        return jsonify({'driver_status': driver_status[0],'driver_request_from':driver_request_id[0],'driver_links':driver_return_list[0][0],'driver_position':driver_return_list[0][1:]})
    except:
        return jsonify({'driver_status': 'Not activation'})
@app.route('/driver2',methods=['GET'])
def return_driver2_status():
    try:
        return jsonify({'driver_status': driver_status[1],'driver_request_from':driver_request_id[1],'driver_links':driver_return_list[1][0],'driver_position':driver_return_list[1][1:]})
    except:
        return jsonify({'driver_status': 'Not activation'})

@app.route('/driver3',methods=['GET'])
def return_driver3_status():
    try:
        return jsonify({'driver_status': driver_status[2],'driver_request_from':driver_request_id[2],'driver_links':driver_return_list[2][0],'driver_position':driver_return_list[2][1:]})
    except:
        return jsonify({'driver_status': 'Not activation'})

@app.route('/driver4',methods=['GET'])
def return_driver4_status():
    try:
        return jsonify({'driver_status': driver_status[3],'driver_request_from':driver_request_id[3],'driver_links':driver_return_list[3][0],'driver_position':driver_return_list[3][1:]})
    except:
        return jsonify({'driver_status': 'Not activation'})
@app.route('/driver5',methods=['GET'])
def return_driver5_status():
    try:
        return jsonify({'driver_status': driver_status[4],'driver_request_from':driver_request_id[4],'driver_links':driver_return_list[4][0],'driver_position':driver_return_list[4][1:]})
    except:
        return jsonify({'driver_status': 'Not activation'})

@app.route('/igsearch',methods=['GET'])
def hashtagInput():
    insertValues = request.get_json()
    user_input_from_web = insertValues['user_input_from_web']
    user_id = int(insertValues['user_id'])
    #user_input_from_web = '#台北景點'
    #user_id = 1
    
    locals()['searching'+str(user_id)] = threading.Thread(target=user_API,args=(user_id,user_input_from_web,driver_status)) 
    locals()['searching'+str(user_id)].start()

    finding_id = True
    while finding_id :
        try:
            the_request_position = driver_request_time.index(user_id)
            feedback = driver_request_time_success[the_request_position]
            feedback_driver = driver_request_time_success_which[the_request_position]
            finding_id = False
        except:
            finding_id = True
    return jsonify({'user_input_from_web': user_input_from_web, 'user_id': user_id, 'request': feedback,'feedback_driver':feedback_driver,'driver_status': driver_status })

if __name__ == '__main__':

    driver_search_number = 2
    account_numbers = ["forin.range2022","sightsinsight1","sightsinsight2","sightsinsight3","sightsinsight4"]
    passwords = ["forin.range.ig2022","forin.range.ig2022","forin.range.ig2022","forin.range.ig2022","forin.range.ig2022"]

    print('''
    
<Maintain>
# maintain-parameters
-- CD = 10 # 進CD 10秒冷卻
-- _aaqm location = driver2.find_element_by_css_selector('[class="_aaqm"]').text
# maintain-driver-quantity
# need upgrade

<IG>
forin.range2022 forin.range.ig@gmail.com forin.range.ig2022
sightsinsight1 SightsinSight1@gmail.com forin.range.ig2022
sightsinsight2 jeffhong8244@gmail.com forin.range.ig2022
sightsinsight3 jeffhong824444@gmail.com forin.range.ig2022
sightsinsight4 tingchun.tc.hung@gmail.com forin.range.ig2022

<API>
http://127.0.0.1:3000/driver_status
http://127.0.0.1:3000/driver1
http://127.0.0.1:3000/driver2
http://127.0.0.1:3000/driver3
http://127.0.0.1:3000/driver4
http://127.0.0.1:3000/driver5
http://127.0.0.1:3000/igsearch
{
    "user_input_from_web":"#內湖景點",
    "user_id":"1"
}

<API return>
"driver_links": 搜尋出貼文網址 E.g. "https://www.instagram.com/p/CB2-WZ0n_SG/"
"driver_position": 熱門貼文景點地點 E.g.    
        [
            "白石湖吊橋",
            "Exact match",
            2666
        ],
 <API return-防呆>       
"driver_links": ["https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo","https://www.instagram.com/p/Ceh6Un7vBIo"]  
"driver_position": -1

''')


    # setting
    '''
    with open('D:/Record/團隊/團隊發展/Jason Team - 團隊名聲 & 新創產品/2022_06_01/NameList.txt','r',encoding='utf-8') as file :
        Spots = file.read().split('\n')
    print('============= load "Spots name" database =============')
    '''
       
    # driver status
    try:
        print('driver原已存在',driver_status)
    except:
        #driver_status = [-1 , -1, -1, -1, -1] # maintain-driver-quantity
        #driver_status = [-1 , -1] # maintain-driver-quantity
        driver_status = [-1 for adding in range(driver_search_number) ] 

    # maintain-driver-quantity
    for driver_id in range(driver_search_number):
        locals()['driver_status'+str(driver_id+1)] = check_driver(driver_id = driver_id)
        if locals()['driver_status'+str(driver_id+1)] == False:
            # 搭配動畫過程 登入driver
            locals()['IG_running_class'+str(driver_id+1)]  = IG_hot_hasgtag(account_number=account_numbers[driver_id],password=passwords[driver_id])
            locals()['IG_driver'+str(driver_id+1)]  = locals()['IG_running_class'+str(driver_id+1)].return_driver()
            driver_status[driver_id] = 0

    '''
    driver_status1 = check_driver(driver_id = 0)
    if driver_status1 == False:
        # 搭配動畫過程 登入driver
        IG_running_class1 = IG_hot_hasgtag(account_number="forin.range2022",password="forin.range.ig2022") # forin.range.ig@gmail.com
        IG_driver1 = IG_running_class1.return_driver()
        #Google_running_class1 = Google_map()
        #Google_driver1 = Google_running_class1.return_driver()
        driver_status[0] = 0

    driver_status2 = check_driver(driver_id = 1)   
    if driver_status2 == False:
        IG_running_class2 = IG_hot_hasgtag(account_number="sightsinsight1",password="forin.range.ig2022") # SightsinSight1@gmail.com
        IG_driver2 = IG_running_class2.return_driver()
        #Google_running_class2 = Google_map()
        #Google_driver2 = Google_running_class2.return_driver()
        driver_status[1] = 0
    '''
    '''
    driver_status3 = check_driver(driver_id = 2)   
    if driver_status3 == False:
        IG_running_class3 = IG_hot_hasgtag(account_number="sightsinsight2",password="forin.range.ig2022") # jeffhong8244@gmail.com
        IG_driver3 = IG_running_class3.return_driver()
        #Google_running_class3 = Google_map()
        #Google_driver3 = Google_running_class3.return_driver()
        driver_status[2] = 0
        
    driver_status4 = check_driver(driver_id = 3)   
    if driver_status4 == False:
        IG_running_class4 = IG_hot_hasgtag(account_number="sightsinsight3",password="forin.range.ig2022") # jeffhong824444@gmail.com
        IG_driver4 = IG_running_class4.return_driver()
        #Google_running_class4 = Google_map()
        #Google_driver4 = Google_running_class4.return_driver()
        driver_status[3] = 0
        
    driver_status5 = check_driver(driver_id = 4)   
    if driver_status5 == False:
        IG_running_class5 = IG_hot_hasgtag(account_number="sightsinsight4",password="forin.range.ig2022") # tingchun.tc.hung@gmail.com
        IG_driver5 = IG_running_class5.return_driver()
        #Google_running_class5 = Google_map()
        #Google_driver5 = Google_running_class5.return_driver()
        driver_status[4] = 0
    '''
    # driver status
    #driver_list = [ [IG_running_class1,IG_driver1,Google_running_class1,Google_driver1],[IG_running_class2,IG_driver2,Google_running_class2,Google_driver2] ] # maintain-driver-quantity
    #driver_list = [ [IG_running_class1,IG_driver1],[IG_running_class2,IG_driver2],[IG_running_class3,IG_driver3],[IG_running_class4,IG_driver4],[IG_running_class5,IG_driver5] ] # maintain-driver-quantity
    #driver_list = [ [IG_running_class1,IG_driver1],[IG_running_class2,IG_driver2] ]
    driver_list = []
    for adding in range(driver_search_number):
        list_mix = []
        list_mix.append(locals()['IG_running_class'+str(adding+1)])
        list_mix.append(locals()['IG_driver'+str(adding+1)])
        driver_list.append(list_mix)
    #driver_list = [ [locals()['IG_running_class'+str(adding+1)],locals()['IG_driver'+str(adding+1)]] for adding in range(driver_search_number) ] # maintain-driver-quantity

    driver_request_time = []
    driver_request_time_success = []
    driver_request_time_success_which = []
    #driver_request_id = [-1,-1,-1,-1,-1] # maintain-driver-quantity
    #driver_request_id = [-1,-1] # maintain-driver-quantity
    driver_request_id = [-1 for adding in range(driver_search_number)]
    
    #driver_return_list = [ [-1 for each_info in range(10)],[-1 for each_info in range(10)],[-1 for each_info in range(10)],[-1 for each_info in range(10)],[-1 for each_info in range(10)] ] # maintain-driver-quantity
    #driver_return_list = [ [-1 for each_info in range(10)],[-1 for each_info in range(10)] ] # maintain-driver-quantity
    driver_return_list = [ [-1 for each_info in range(10)] for adding in range(driver_search_number) ] # maintain-driver-quantity
    
    
    
    
    print('============= Driver 都建立完成 可以開始搜尋 =============')
    
    # run
    app.run(port=3000 ) # host='0.0.0.0' ,  , debug=True
