# ----------------- 日歷 -----------------
import calendar

# ----------------- import ENG setting -----------------
from win32con import WM_INPUTLANGCHANGEREQUEST
import win32gui
import win32api

# ----------------- import text 2 voice -----------------
import pyttsx3

# ----------------- 平行處理 -----------------
from threading import Thread

# ----------------- import crawler -----------------
import pyautogui
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# ----------------- import GUI ----------------- 
import tkinter as tk
import tkinter.ttk as tt
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.filedialog import askdirectory
import keyboard

# ----------------- import Processing -----------------
from time import sleep
import pandas as pd
import difflib
import pyperclip
import os
from os import listdir,path,rename,walk,makedirs
from os.path import isfile, isdir, join

import re
import zipfile
import time
import datetime
import sys
import shutil
import re

import pathlib
from getpass import getuser

datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta

def mkdir_dir(Save_path):
    path = Save_path+'/data/'
    try:
        shutil.rmtree(path)
        path = Save_path+'/data/'
        if not os.path.isdir(path):
            os.mkdir(path)

        path = Save_path+'/data/contact/'
        if not os.path.isdir(path):
            os.mkdir(path)

    except:
        path = Save_path+'/data/'
        if not os.path.isdir(path):
            os.mkdir(path)

        path = Save_path+'/data/contact/'
        if not os.path.isdir(path):
            os.mkdir(path)
            
    path = Save_path+'/search_result/'
    if not os.path.isdir(path):
        os.mkdir(path)

class Calendar:
    def __init__(s, point = None):
        s.master = tk.Toplevel()
        s.master.geometry('1000x1000')
        s.master.withdraw()
        s.master.attributes('-topmost' ,True)
        fwday = calendar.SUNDAY
        year = datetime.now().year
        month = datetime.now().month
        locale = None
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'
        s._date = datetime(year, month, 1)        #每月第一日
        s._selection = None                       #设置为未选中日期
        s.G_Frame = ttk.Frame(s.master)
        s._cal = s.__get_calendar(locale, fwday)
        s.__setup_styles()        # 创建自定义样式
        s.__place_widgets()       # pack/grid 小部件
        s.__config_calendar()     # 调整日历列和安装标记
        # 配置画布和正确的绑定，以选择日期。
        s.__setup_selection(sel_bg, sel_fg)
        # 存储项ID，用于稍后插入。
        s._items = [s._calendar.insert('', 'end', values='') for _ in range(6)]
        # 在当前空日历中插入日期
        s._update()
        s.G_Frame.pack(expand = 1, fill = 'both')
        s.master.overrideredirect(1)
        s.master.update_idletasks()
        width, height = s.master.winfo_reqwidth(), s.master.winfo_reqheight()
        s.height=height
        if point:
            x, y = point[0], point[1]
        else: 
            x, y = (s.master.winfo_screenwidth() - width)/2, (s.master.winfo_screenheight() - height)/2
        s.master.geometry('%dx%d+%d+%d' % (width, height, x, y)) #窗口位置居中
        s.master.after(300, s._main_judge)
        s.master.deiconify()
        s.master.focus_set()
        s.master.wait_window() #这里应该使用wait_window挂起窗口，如果使用mainloop,可能会导致主程序很多错误

    def __get_calendar(s, locale, fwday):
        if locale is None:
          return calendar.TextCalendar(fwday)
        else:
          return calendar.LocaleTextCalendar(fwday, locale)

    def __setitem__(s, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            s._canvas['background'] = value
        elif item == 'selectforeground':
            s._canvas.itemconfigure(s._canvas.text, item=value)
        else:
            s.G_Frame.__setitem__(s, item, value)

    def __getitem__(s, item):
        if item in ('year', 'month'):
            return getattr(s._date, item)
        elif item == 'selectbackground':
            return s._canvas['background']
        elif item == 'selectforeground':
            return s._canvas.itemcget(s._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({
        item: ttk.Frame.__getitem__(s, item)})
        return r[item]

    def __setup_styles(s):
        # 自定义TTK风格
        style = ttk.Style(s.master)
        arrow_layout = lambda dir: (
          [('Button.focus', {
        'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(s):
        # 标头框架及其小部件
        szienumber = 1
        Input_judgment_num = s.master.register(s.Input_judgment) # 需要将函数包装一下，必要的
        hframe = ttk.Frame(s.G_Frame)
        gframe = ttk.Frame(s.G_Frame)
        bframe = ttk.Frame(s.G_Frame)
        hframe.pack(in_=s.G_Frame, side='top', pady=5, anchor='center')
        gframe.pack(in_=s.G_Frame, fill=tk.X, pady=5)
        bframe.pack(in_=s.G_Frame, side='bottom', pady=5)
        lbtn = ttk.Button(hframe, style='L.TButton', command=s._prev_month)
        lbtn.grid(in_=hframe, column=0, row=0, padx=12)
        rbtn = ttk.Button(hframe, style='R.TButton', command=s._next_month)
        rbtn.grid(in_=hframe, column=5, row=0, padx=12)
        s.CB_year = ttk.Combobox(hframe, width = 5*szienumber, values = [str(year) for year in range(datetime.now().year, datetime.now().year-11,-1)], validate = 'key', validatecommand = (Input_judgment_num, '%P'))
        s.CB_year.current(0)
        s.CB_year.grid(in_=hframe, column=1, row=0)
        s.CB_year.bind('<KeyPress>', lambda event:s._update(event, True))
        s.CB_year.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text = '年', justify = 'left').grid(in_=hframe, column=2, row=0, padx=(0,5))
        s.CB_month = ttk.Combobox(hframe, width = 3*szienumber, values = ['%02d' % month for month in range(1,13)], state = 'readonly')
        s.CB_month.current(datetime.now().month - 1*szienumber)
        s.CB_month.grid(in_=hframe, column=3, row=0)
        s.CB_month.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text = '月', justify = 'left').grid(in_=hframe, column=4, row=0)
        # 日历部件
        s._calendar = ttk.Treeview(gframe, show='', selectmode='none', height=7) 
        s._calendar.pack(expand=1, fill='both', side='bottom', padx=5)
        ttk.Button(bframe, text = "確 定", width = 6*szienumber, command = lambda: s._exit(True)).grid(row = 0, column = 0, sticky = 'ns', padx = 20)
        ttk.Button(bframe, text = "取 消", width = 6*szienumber, command = s._exit).grid(row = 0, column = 1, sticky = 'ne', padx = 20)
        tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 1, relheigh = 2/200)
        tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 198/200, relwidth = 1, relheigh = 2/200)
        tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 0, rely = 0, relwidth = 2/200, relheigh = 1)
        tk.Frame(s.G_Frame, bg = '#565656').place(x = 0, y = 0, relx = 198/200, rely = 0, relwidth = 2/200, relheigh = 1)

    def __config_calendar(s):
        # cols = s._cal.formatweekheader(3).split()
        cols = ['日','一','二','三','四','五','六']
        s._calendar['columns'] = cols
        s._calendar.tag_configure('header', background='grey90')
        s._calendar.insert('', 'end', values=cols, tag='header')
        # 调整其列宽
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
          s._calendar.column(col, width=maxwidth, minwidth=maxwidth,
            anchor='center')

    def __setup_selection(s, sel_bg, sel_fg):
        def __canvas_forget(evt):
            canvas.place_forget()
            s._selection = None

        s._font = tkFont.Font()
        s._canvas = canvas = tk.Canvas(s._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')
        canvas.bind('<Button-1>', __canvas_forget)
        s._calendar.bind('<Configure>', __canvas_forget)
        s._calendar.bind('<Button-1>', s._pressed)

    def _build_calendar(s):
        year, month = s._date.year, s._date.month
        header = s._cal.formatmonthname(year, month, 0)
        # 更新日历显示的日期
        cal = s._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(s._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            s._calendar.item(item, values=fmt_week)

    def _show_select(s, text, bbox):
        x, y, width, height = bbox
        textw = s._font.measure(text)
        canvas = s._canvas
        canvas.configure(width = width, height = height)
        canvas.coords(canvas.text, (width - textw)/2, height / 2 - 1) 
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=s._calendar, x=x, y=y)

    def _pressed(s, evt = None, item = None, column = None, widget = None):
        """在日历的某个地方点击。"""
        if not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)
        if not column or not item in s._items:
            # 在工作日行中单击或仅在列外单击。
            return
        item_values = widget.item(item)['values']
        if not len(item_values): # 这个月的行是空的。
            return
        text = item_values[int(column[1]) - 1]
        if not text: 
            return
        bbox = widget.bbox(item, column)
        if not bbox: # 日历尚不可见
            s.master.after(20, lambda : s._pressed(item = item, column = column, widget = widget))
            return
        text = '%02d' % text
        s._selection = (text, item, column)
        s._show_select(text, bbox)

    def _prev_month(s):
        """更新日历以显示前一个月。"""
        s._canvas.place_forget()
        s._selection = None
        s._date = s._date - timedelta(days=1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _next_month(s):
        """更新日历以显示下一个月。"""
        s._canvas.place_forget()
        s._selection = None

        year, month = s._date.year, s._date.month
        s._date = s._date + timedelta(
          days=calendar.monthrange(year, month)[1] + 1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _update(s, event = None, key = None):
        """刷新界面"""
        if key and event.keysym != 'Return': return
        year = int(s.CB_year.get())
        month = int(s.CB_month.get())
        if year == 0 or year > 9999: return
        s._canvas.place_forget()
        s._date = datetime(year, month, 1)
        s._build_calendar() # 重建日历
        if year == datetime.now().year and month == datetime.now().month:
            day = datetime.now().day
            for _item, day_list in enumerate(s._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day)+1)
                    s.master.after(100, lambda :s._pressed(item = item, column = column, widget = s._calendar))

    def _exit(s, confirm = False):
        if not confirm: s._selection = None
        s.master.destroy()

    def _main_judge(s):
        """判断窗口是否在最顶层"""
        try:
            if s.master.focus_displayof() == None or 'toplevel' not in str(s.master.focus_displayof()): s._exit()
            else: s.master.after(10, s._main_judge)
        except:
            s.master.after(10, s._main_judge)

    def selection(s):
        """返回表示当前选定日期的日期时间。"""
        if not s._selection: return None
        year, month = s._date.year, s._date.month
        return str(datetime(year, month, int(s._selection[0])))[:10]

    def Input_judgment(s, content):
        """输入判断"""
        if content.isdigit() or content == "":
          return True
        else:
          return False

class datepicker:
    def __init__(s,window,axes):  #窗口对象 坐标
        s.window=window
        s.frame=tk.Frame(s.window,padx=5)
        s.frame.grid(row=axes[0],column=axes[1])
        s.start_date=tk.StringVar()		#开始日期
        s.end_date=tk.StringVar()		#结束日期
        s.bt1=tk.Button(s.frame,text='開始', font=(fonttype, fontsize),command=lambda:s.getdate('start'))	#开始按钮
        s.bt1.grid(row=0,column=0)
        s.ent1=tk.Entry(s.frame,textvariable=s.start_date)	#开始输入框
        s.ent1.grid(row=0,column=1)
        s.bt2=tk.Button(s.frame,text='結束', font=(fonttype, fontsize),command=lambda:s.getdate('end'))
        s.bt2.grid(row=0,column=2)
        s.ent2=tk.Entry(s.frame,textvariable=s.end_date)
        s.ent2.grid(row=0,column=3)
    
    def getdate(s,type):	#获取选择的日期
        for date in [Calendar().selection()]:
            if date:
                if(type=='start'):	#如果是开始按钮，就赋值给开始日期
                    s.start_date.set(date)
                elif(type=='end'):
                    s.end_date.set(date)


def 爬蟲(Date,time_section,list_input1,list_input2,port_section,list_input3,port_search_section,company_threshold,web_threshold,sort_threshold,All_data_path,Save_path,Already_search_company,Recording,print_process = False):
    
    print(Date[0])
    print(Date[1])
    print(sort_threshold)
    
    download_path = Save_path.replace('/','\\') + ''
    print(download_path)
        
    Company_type = port_search_section # A純進口 B純出口
    Company_web_number = web_threshold
    
    def setting_ENG():
        # 語言程式碼
        # https://msdn.microsoft.com/en-us/library/cc233982.aspx
        LID = {0x0804: "Chinese (Simplified) (People's Republic of China)",
               0x0409: 'English (United States)'}

        # 獲取前景視窗控制代碼
        hwnd = win32gui.GetForegroundWindow()

        # 獲取前景視窗標題
        title = win32gui.GetWindowText(hwnd)
    #     print('當前視窗：' + title)

        # 獲取鍵盤佈局列表
        im_list = win32api.GetKeyboardLayoutList()
        im_list = list(map(hex, im_list))
    #     print(im_list)

        # 設定鍵盤佈局為英文
        result = win32api.SendMessage(
            hwnd,
            WM_INPUTLANGCHANGEREQUEST,
            0,
            0x0409)
        if result == 0:
            print('設定英文鍵盤成功！')    

    def move_2_top():
        js="var action=document.documentElement.scrollTop=0"  
        driver.execute_script(js)
        sleep(sleep_time)
    
    def move_2_chi(Big_x, Big_y):

        js="var action=document.documentElement.scrollTop=0"  
        driver.execute_script(js)
        sleep(sleep_time)

        move_time = '0.01'    
        # Time
        for i in range(2):
            pyautogui.moveTo(Big_x,Big_y,duration=0.1)
        pyautogui.click()
        sleep(sleep_time)

        for i in range(len(list_input1)+len(list_input2)+len(list_input3)+47):
            pyautogui.hotkey('tab')

    def check_close_running():
        if keyboard.is_pressed('b'):
            try:
                driver.quit()
            except:
                no_driver = True
            sys.exit()
    def mailProcessing(mailString):
        mail_list = []
        mistake_mail_flag = 0
        while '@' in mailString:

            beginning = mailString.split('@')[0]
            tmp = mailString.split('@')[1]
            #mail =''
            if '.com' in tmp:
                end = tmp.split('.com')[0]
                mail = beginning + '@' + end + '.com'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.edu' in tmp:
                end = tmp.split('.edu')[0]
                mail = beginning + '@' + end + '.edu'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.net' in tmp:
                end = tmp.split('.net')[0]
                mail = beginning + '@' + end + '.net'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.nl' in tmp:
                end = tmp.split('.nl')[0]
                mail = beginning + '@' + end + '.nl'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.org' in tmp:
                end = tmp.split('.org')[0]
                mail = beginning + '@' + end + '.org'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.io' in tmp:
                end = tmp.split('.io')[0]
                mail = beginning + '@' + end + '.io'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            elif '.uk' in tmp:
                end = tmp.split('.uk')[0]
                mail = beginning + '@' + end + '.uk'
                if mistake_mail_flag == 0:
                    mail_list.append(mail)
                else:
                    mistake_mail_flag = 0
            else:
                mistake_mail_flag = 1
                mail = beginning + '@'

            mailString = mailString[len(mail):]
        return mail_list

    def GetContactInformation(path): # 取得下載的聯絡資訊
        try:
            contactinformation_list = []
            df = pd.read_csv(path)
            col_list = df.columns.tolist()
            for i in range(df.shape[0]):
                dict_ = {}
                for col, value in zip(col_list, df.iloc[i].tolist()):
                    dict_[col] = value
                if isinstance(dict_['Email'], str):
                    mail_list = mailProcessing(dict_['Email'])

                    for mail in mail_list:
                        dict_['Email'] = mail
                        #print(dict_)
                        contactinformation_list.append(dict_)
                else:
                    #print(dict_)
                    contactinformation_list.append(dict_)
        except:
            contactinformation_list = []
        return contactinformation_list
    '''
    def GetCompanyInformation(path, number=5): # 取得下載的公司資訊，預設找5家公司
        df = pd.read_excel(path)
        col_list = df.iloc[6].tolist()
        df = df[7:]
        companyinformation_list = []

        for i in range(number):
            dict_ = {}
            for col, value in zip(col_list, df.iloc[i].tolist()):
                dict_[col] = value
            companyinformation_list.append(dict_)

        if number > df.shape[0]:
            number = df.shape[0]

        return  companyinformation_list[:number] 
    '''

    
    def GetStingSimilarity(str1, str2):
        seq = difflib.SequenceMatcher(None, str1.lower(), str2.lower())
        ratio = seq.ratio()

        return ratio

    def GetSearchResult(text, number=5): # 取得搜尋的公司資訊，預設找5個搜尋結果
        searchresult_list = []
        text = text.split('\n')
        search_company_name = text[5].replace('\r','')

        for i, line in enumerate(text):
            dict_ = {}
            if '国家区域:' in line:
                dict_['公司名稱'] = text[i-2].replace('\r','')
                dict_['網址'] = text[i-1].replace('\r','')
                dict_['國家區域'] = text[i+1].replace('\r','')
                searchresult_list.append(dict_)

        if number > len(searchresult_list):
            number = len(searchresult_list)

        return search_company_name, searchresult_list[:number]

    def mkdir_dir(Save_path):
        path = Save_path+'/data/'
        try:
            shutil.rmtree(path)
            path = Save_path+'/data/'
            if not os.path.isdir(path):
                os.mkdir(path)

            path = Save_path+'/data/contact/'
            if not os.path.isdir(path):
                os.mkdir(path)

        except:
            path = Save_path+'/data/'
            if not os.path.isdir(path):
                os.mkdir(path)

            path = Save_path+'/data/contact/'
            if not os.path.isdir(path):
                os.mkdir(path)

        path = Save_path+'/search_result/'
        if not os.path.isdir(path):
            os.mkdir(path)
    
    def GetCombineOutput(search_company_name, searchresult_list, Save_path, Already_search_company, ranking = '關閉自動排序'):
        output_list = [['搜尋的公司名稱', search_company_name]]
        
        #company_list = ['公司A.xls', '公司B.xls', '公司C.xls', '公司D.xls', '公司E.xls'] # 到時候預計會是讀取資料家中的檔案名稱
        company_list = os.listdir(Save_path+'/data/contact')
        company_list.sort(key=lambda fn:os.path.getmtime(Save_path+'/data/contact' + "\\" + fn))#按時間排序
        print('=====================未重新', company_list)
        if ranking == '開啟自動排序':
            similarity_dict = {}
            for company in company_list:
                similarity = GetStingSimilarity(search_company_name, company)
                similarity_dict[company] = similarity
            ranking_list = sorted(similarity_dict.items(),key = lambda item:item[1], reverse=True)
            company_list = []
            for c, _ in ranking_list:
                company_list.append(c)
                
        print('=====================重新', company_list)
        
        for searchresult, company in zip(searchresult_list, company_list):
            for _key, _value in zip(list(searchresult.keys()), list(searchresult.values())):
                tmp_list = []
                tmp_list.append(_key)
                tmp_list.append(_value)
                output_list.append(tmp_list)
            contactinformation_list = GetContactInformation(Save_path+'/data/contact/' + company)
            for i, contactinformation in enumerate(contactinformation_list):
                if i == 0:
                    output_list.append(list(contactinformation.keys()))
                output_list.append(list(contactinformation.values()))
        output = pd.DataFrame(output_list)
        search_company_name = re.sub(r"[^a-zA-Z0-9 ]","",search_company_name)
        file_name = Save_path + '/search_result/' + str(Already_search_company+1) + '_' + search_company_name + '.csv'
        output.to_csv(file_name, index=False, header=None, encoding='utf_8_sig')
         
        for company in company_list:
            os.remove(Save_path+'/data/contact/' + company)
        
        
        #time_stamp = int(time.time())
        #struct_time = time.localtime(time_stamp) # 轉成時間元組
        #timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
        #print(timeString)
        
        search_result_list = os.listdir(Save_path + '/search_result')
        search_result_df = pd.DataFrame()
        for file in search_result_list:
            df = pd.read_csv(Save_path + '/search_result/' + file, header=None)
            search_result_df = pd.concat([search_result_df, df])
        search_result_df.to_csv(Save_path + '/Result.csv', index=False, header=None, encoding='utf_8_sig')
        time_stamp = int(time.time())
        struct_time = time.localtime(time_stamp) # 轉成時間元組
        timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
        try:
            with open(Save_path + '/' +'Record_time.txt','w') as file_recording :
                file_recording.write(search_company_name+' completed in '+timeString+'\n')
        except:
            with open(Save_path + '/' +'Record_time.txt','a') as file_recording :
                file_recording.write(search_company_name+' completed in '+timeString+'\n')
        
        return output

    def newest_report(path):
        lists = os.listdir(path) #列出目錄的下所有文件和文件夾保存到lists
        lists.sort(key=lambda fn:os.path.getmtime(path + "\\" + fn))#按時間排序
        file_new = os.path.join(path, lists[-1])                     #獲取最新的文件保存到file_new

        return file_new

            
    def running_screenshot( screenshot_path,reset_x,reset_y,web_result_confidence=0, click = True  , grayscale=False):

        sleep(sleep_time)
        for i in range(2):
            pyautogui.moveTo(reset_x,reset_y,duration=0.1)

        if web_result_confidence != 0 :
            button = pyautogui.locateOnScreen(screenshot_path,confidence=web_result_confidence,grayscale=grayscale)
        else:
            button = pyautogui.locateOnScreen(screenshot_path,grayscale=grayscale)
        x, y = pyautogui.center(button)

        for i in range(2):
            pyautogui.moveTo(x,y,duration=0.1)
        if click :
            pyautogui.click()

        return x, y
    
    # ======================================================= PART 1 =======================================================
    
    # ---------------- pre-setting ---------------- 

    mkdir_dir(Save_path)
    
    search_position_confidence = float(Recording[1])
    download_confidence = float(Recording[2])
    stop_for_ctrl_confidence = float(Recording[3])
    search_start_confidence = float(Recording[4])
    search_over_confidence = float(Recording[5])
    search_over_check_confidence = float(Recording[6])
    web_result_confidence = float(Recording[7])
    stop_searching_confidence = float(Recording[8])
    search_return_confidence = float(Recording[9])
    
    # ---------------- inner setting ----------------
    reset_x = 1000
    reset_y = 10
    search_upper_limit = 180
    slip_times = 5
    next_page_sleep_time = 15
    
    # ---------------- Initialization ----------------
    setting_ENG()
    user_name = getuser()
    Records = []
    screenshot_time = -1
    rename_lists = ["search_position.png","download.png","stop_for_ctrl.png","search_start.png","search_over.png","search_over_check.png","web_result.png","stop_searching.png","search_return.png"]
    threading_time = 100
    
    # ---------------- 基本設定 ----------------
    sleep_time = 2
    move_time = '0.01'

    # ---------------- 開啟網頁設定 ----------------
    # 設定chrome_options
    chrome_options = Options()
    chrome_options.add_extension(All_data_path+'企查通.crx')
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': download_path+'\data\contact'}
    chrome_options.add_experimental_option('prefs', prefs)
    #driver = Chrome(chrome_options=chrome_options)
    # chrome_options.add_experimental_option('prefs', prefs)
    driver = Chrome(chrome_options=chrome_options)

    # ---------------- 開啟網站 並登錄帳密 ----------------
    
    driver.minimize_window() # 先最小化 
    driver.maximize_window() # 再最大化 即可彈出視窗
    driver.get("https://cn.bigtradedata.com/")
    driver.find_element_by_name("username").click()
    driver.find_element_by_name("username").clear()
    driver.find_element_by_name("username").send_keys("GT21WH03HYF31")
    driver.find_element_by_name("password").click()
    driver.find_element_by_name("password").clear()
    driver.find_element_by_name("password").send_keys("ENPAK202505")
    driver.find_element_by_xpath("//a[@id='btnLogin']/div").click()
    sleep(sleep_time)
#     check_close_running()

    # ---------------- 反覆嘗試點 全球追踪全球搜 ----------------
    try_time = 0 ; try_select = True
    while try_select == True : # 依循每次網頁開啟時間不同，彈性調整
        try:
            # 點選目標路徑
            driver.find_element_by_xpath("//div[@id='tabs']/div[2]/div/div/div/div/ul/li/div/div").click()
            driver.find_element_by_link_text(u"全球追踪全球搜").click()
            try_select = False
        except:
            try_time + 1
            sleep(1)
            try_select = True
            if try_time >= 30 :
                try_time = False
                return Already_search_company
    sleep(sleep_time)

    # ---------------- 利用 海關數據編碼 之截圖 定位&輸入探勘資訊 ----------------
    for i in range(2):
        pyautogui.moveTo(reset_x,reset_y,duration=0.1)
    pyautogui.click()
    sleep(sleep_time)
    Screenshot_locateOnScreen = True
    screenshot_time = 0
    move_2_top()
    try_time2 = 0
    while Screenshot_locateOnScreen: # 第一個一定需要定位到
        try:
            if search_position_confidence != 0 :
                button = pyautogui.locateOnScreen(All_data_path+rename_lists[screenshot_time],confidence=search_position_confidence)
            else:
                button = pyautogui.locateOnScreen(All_data_path+rename_lists[screenshot_time])
            x, y = pyautogui.center(button)
            Big_x,Big_y = x,y # 以下輸入將根據此 x, y 移動
            Screenshot_locateOnScreen = False
        except:
            try_time2 + 1
            sleep(1)
            Screenshot_locateOnScreen = True
            if try_time2 >= 30 :
                try_time2 = False
                return Already_search_company

    # ---------- 先去調整時間 ----------
    move_2_top()
    for i in range(2):
        pyautogui.moveTo(x,y,duration=0.1)
    pyautogui.click()
    for i in range(4):
        pyautogui.hotkey('shift', 'tab')
    for section in range(1+time_section) : 
        pyautogui.hotkey('down') 
    pyautogui.hotkey('enter')
    
    if Date[1] != '':
        pyautogui.hotkey('shift', 'tab')
        list_each = [ word for word in Date[1] ]
        pyautogui.typewrite(list_each,move_time)
        if Date[0] != '':
            pyautogui.hotkey('shift', 'tab')
            list_each = [ word for word in Date[0] ]
            pyautogui.typewrite(list_each,move_time)
    elif Date[0] != '':
        pyautogui.hotkey('shift', 'tab')
        pyautogui.hotkey('shift', 'tab')
        list_each = [ word for word in Date[0] ]
        pyautogui.typewrite(list_each,move_time)
        
    # ---------- Reset ----------
    if list_input1 == [''] :
        list_input1 = []
    if list_input2 == [''] :
        list_input2 = []
    if list_input3 == [''] :
        list_input3 = []
        
    # ---------- 海關數據編碼 ----------
    if list_input1 != []: # Get input
        move_2_top()
        for each_code in range(len(list_input1)) :
            for i in range(2):
                pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            list_each = [ word for word in list_input1[each_code] ]
            pyautogui.typewrite(list_each,move_time)
            pyautogui.typewrite(['tab'],move_time)
            pyautogui.hotkey('enter')

    # ---------- 產品種類 ----------
    if list_input2 != []: # Get input
        move_2_top()
        first_time = True
        for each_code in range(len(list_input2)) :
            for i in range(2):
                pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            for move_to_next in range(len(list_input1)+3):
                pyautogui.typewrite(['tab'],move_time)
            pyautogui.hotkey('down')
            if first_time == True : # 調整為「詳細品名英文」
                pyautogui.hotkey('down')
                first_time = False
            pyautogui.hotkey('enter')
            pyautogui.typewrite(['tab'],move_time)
            list_each = [ word for word in list_input2[each_code] ]
            pyautogui.typewrite(list_each,move_time)
            pyautogui.typewrite(['tab'],move_time)
            pyautogui.hotkey('enter')

    # ---------- 進出口商所在國家 ----------
    if list_input3 != []: # Get input
        move_2_top()
        first_time = True
        for each_code in range(len(list_input3)) :
            for i in range(2):
                pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            for move_to_next in range(len(list_input1)+3+len(list_input2)+18):
                pyautogui.typewrite(['tab'],move_time)

            if first_time == True : # 調整為「進口商所在國家」
                if port_search_section == 'A' :
                    section_chose = 1
                elif port_search_section == 'B' :
                    section_chose = 2
                for running_port_search_section in range(section_chose):
                    pyautogui.hotkey('down')
                first_time = False
            pyautogui.hotkey('enter')
            
            pyautogui.typewrite(['tab'],move_time)
            list_each = [ word for word in list_input3[each_code] ]
            pyautogui.typewrite(list_each,move_time)
            pyautogui.hotkey('enter')
            pyautogui.typewrite(['tab'],move_time)
            pyautogui.hotkey('enter')
    else: # no input to almost last step
        move_2_top()
        for each_code in range(1) :
            for i in range(2):
                pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            for move_to_next in range(len(list_input1)+3+len(list_input2)+20):
                pyautogui.typewrite(['tab'],move_time)

    # ------------------- 國貿4.0搜尋 -------------------
    pyautogui.typewrite(['tab'],move_time)
    pyautogui.hotkey('enter')

    # ------------------- 國貿4.0確認公司上限 -------------------
    
    try :
        Company_number = 1
        sleep(sleep_time)
        pyautogui.hotkey('ctrl', 'shift', 'i')
        sleep(sleep_time)
        pyautogui.hotkey('ctrl', 'f')
        sleep(sleep_time)
        pyperclip.copy('条结果')
        pyautogui.hotkey('ctrl', 'v')
        screenshot_time = 1 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
        x , y = running_screenshot(screenshot_path,reset_x,reset_y,download_confidence)    
        sleep(sleep_time)
        pyautogui.hotkey('up')
        sleep(sleep_time)
        pyautogui.hotkey('ctrl', 'c')
        result = pyperclip.paste()
        start = result.find('<span id="ResultCount">') + len('<span id="ResultCount">')
        end = result[start:].find('</span>') + start
        company_upper_limit = int(result[start:end])
        if print_process :
            print('-- company_upper_limit : '+str(company_upper_limit))
        sleep(sleep_time)
        pyautogui.hotkey('ctrl', 'shift', 'i')

        if int(Company_number) == 0 :
            print('此次搜尋未有結果')
            return  -1   
        if company_threshold.isdigit() == False :
            Company_number = int(company_upper_limit)
        else:
            Company_number = int(company_threshold)
        if int(company_upper_limit) < int(Company_number) : # 若超出上限 只能搜尋到最後一個
            Company_number = int(company_upper_limit)
            if print_process :
                print('-- search company change to : '+str(Company_number))
        if print_process :
            print('-- search company : '+str(Company_number))

        page = int(Company_number/20)
        last_page_companys = int(Company_number%20)
        First_page = True

        print(Company_number)
        print(Already_search_company)
        
    except:
        for quiting in range(2):
            try:
                driver.quit()
                sleep(10)
                print('error occurred')
            except:
                no_driver = True
        return Already_search_company
        
    if Company_number%20 == 0 :
        upper_page = int(Company_number/20)
    else :
        upper_page = int(Company_number/20) + 1
        
    if (Company_number > Already_search_company) and (Already_search_company >= 20) :
        print('Turn pages')
        start_Page = int(Already_search_company/20)
        First_page = True

        # ------------------ 未達到最後目標 且下個目標在下一頁 ------------------ # 翻頁制度 要注意總頁面小於5面tab數量需不同
        if Already_search_company != Company_number :
            moving_2_want_search_company = 19
            move_2_chi(Big_x, Big_y) # 上滑
#                     if Company_type == 'A': # 進口商
            move_2_company_timespany_times = 2 + moving_2_want_search_company*9 
            for i in range(move_2_company_timespany_times):
                pyautogui.hotkey('tab')
            sleep(sleep_time)

            move_2_company_timespany_times = 7 
            for i in range(move_2_company_timespany_times):
                pyautogui.hotkey('tab')
            sleep(sleep_time)    

            Next_page = 8
            if First_page :
                First_page = False
                Next_page -= 1
                
            if upper_page <= 5 :
                remove_tab_time = 6 - upper_page
                Next_page -= remove_tab_time
                
            
                
            for i in range(Next_page):
                pyautogui.hotkey('tab')
                
            sleep(sleep_time)       
            #list_each = [ str(start_Page+1) ]
            pyautogui.typewrite(str(start_Page+1),move_time)
            pyautogui.hotkey('tab')
            pyautogui.hotkey('enter')
            sleep(next_page_sleep_time) # 換頁  
    elif Already_search_company >= Company_number :
        print('Already_search_company >= Company_number')
        return -1
        
        
    # ======================================================= PART 2 =======================================================

    # ---------- Open 企查通 ------------
    if Company_number != 0 :
        each = 0
        move_2_chi(Big_x, Big_y) # 上滑
        move_2_company_timespany_times = 2 + each*9 
        for i in range(move_2_company_timespany_times):
            pyautogui.hotkey('tab')
        sleep(sleep_time)
        pyautogui.hotkey('enter')
        sleep(sleep_time)
    
    Raw_Already_search_company = Already_search_company
    print(Company_number)
    print(Already_search_company)
    # ---------- 正式搜尋 ------------
    for each in range(Already_search_company,Company_number) :
        
        print('<<Company'+str(each+1)+'>>')
        try:
            with open(Save_path + '/' +'Record_result.txt','w') as file_recording :
                file_recording.write('國貿通搜尋公司數 : '+str(Company_number))
                file_recording.write('已搜尋公司數 : '+str(Already_search_company))
                file_recording.write('已完成公司數 : '+str(len(os.listdir(Save_path+'/search_result'))))
        except:
            with open(Save_path + '/' +'Record_result.txt','a') as file_recording :
                file_recording.write('國貿通搜尋公司數 : '+str(Company_number))
                file_recording.write('已搜尋公司數 : '+str(Already_search_company))
                file_recording.write('已完成公司數 : '+str(len(os.listdir(Save_path+'/search_result'))))
                
        spcial_number = 0
        this_company_not_yet = True
        moving_2_want_search_company = int(each%20)
        move_2_chi(Big_x, Big_y) # 上滑

        if Company_type == 'A': # 進口商
            position_company_type = 2

        elif Company_type == 'B':
            position_company_type = 6

        move_2_company_timespany_times = position_company_type + moving_2_want_search_company*9 
        for i in range(move_2_company_timespany_times):
            pyautogui.hotkey('tab')
        sleep(sleep_time)

        # --------------- 點開企查通 ---------------
        pyautogui.hotkey('enter')
        sleep(sleep_time)
        sleep(sleep_time) # wait for web change to next 

        # -------- 等待搜尋 --------
        #screenshot_time = 3  ; screenshot_path = All_data_path+rename_lists[screenshot_time]
        while len(os.listdir(Save_path+'/data/contact')) != Company_web_number:
            Screenshot_locateOnScreen = True
            timethreshold3 = 0
            while Screenshot_locateOnScreen: # 兩種case (1)通常 : 找到開始搜索 (2)特例 : 直接挖掘 等太久會放棄
                try: # Case1 
                    screenshot_time = 3  ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                    x , y = running_screenshot(screenshot_path,reset_x,reset_y,click = False,web_result_confidence = search_start_confidence)
                    Screenshot_locateOnScreen = False
                except: 
                    try: # Case2 
                        screenshot_time = 5 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence)
                        print('--check button')
                        # -------------- 導出結果 ---------------
                        screenshot_time = 6 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = web_result_confidence)
                        print('-- stop')
                        screenshot_time = 7 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_searching_confidence)
                        try:
                            screenshot_time = 5 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                            x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence)
                        except:
                            need_stop = True
                        print('-- return case2')
                        screenshot_time = 8 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_return_confidence)

                        print('-- fininsh the web case2')

                        sleep(sleep_time)
                        # -------- 複製搜尋結果 --------

                        while this_company_not_yet :
                            for i in range(2):
                                pyautogui.moveTo(reset_x,reset_y,duration=0.1)
                            Screenshot_locateOnScreen_two = True
                            screenshot_time = 2  ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                            while Screenshot_locateOnScreen_two:
                                try:
                                    x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_for_ctrl_confidence)
                                    Screenshot_locateOnScreen_two = False
                                except:
                                    Screenshot_locateOnScreen_two = True
                            sleep(sleep_time)
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.hotkey('ctrl', 'c')
                            for i in range(2):
                                pyautogui.moveTo(x,y,duration=0.1)
                            pyautogui.click()

                            text = pyperclip.paste()
                            search_company_name, searchresult_list = GetSearchResult(text, web_threshold)
                            if print_process :
                                print('\n-- web info : ')
                                print(searchresult_list)  
                            this_company_not_yet = False

                        #tmp_number = 0
                        file_number = len(os.listdir(Save_path+'/data/contact'))
                        each_web = 0
                        if file_number != (each_web+1): # 沒有導出數據
                            empty_list = []
                            empty = pd.DataFrame(empty_list)
                            empty.to_csv(Save_path+'/data/contact/empty.xls', index=False, header=None)

                        file_newest = newest_report(Save_path+'/data/contact')
                        print(str(file_newest))
                        print(Save_path+'/data/contact/' + str(each_web) + '_' + searchresult_list[each_web]['公司名稱'])

                        file_name = re.sub(r"[^a-zA-Z0-9 ]","",searchresult_list[each_web]['公司名稱'])
                        file_name = Save_path+'/data/contact/' + str(each_web) + '_' + file_name + '.xls'
                        os.rename(file_newest, file_name)

                        spcial_number = 1

                        Finish_one_web = True
                        Screenshot_locateOnScreen = False


                    except: # 等待
                        sleep(1)
                        timethreshold3 += 1
                        print('['+str(timethreshold3)+']', end = ' ')
                        Screenshot_locateOnScreen = True
                        if timethreshold3 >= int(search_upper_limit/3) :
                            for quiting in range(2):
                                try:
                                    driver.quit()
                                    sleep(10)
                                    print('error occurred')
                                except:
                                    no_driver = True
                        
                            error_number = 0
                            try:
                                with open(Save_path + '/' +'Record_time.txt','r') as file_recording :
                                    for line in file_recording:
                                        if line.find('error time : ')!= -1 :
                                            error_line = line.replace('\n','').replace('error time : ','')
                                            error_number = int(error_line)
                            except:
                                error_number = 0
                                        
                            time_stamp = int(time.time())
                            struct_time = time.localtime(time_stamp) # 轉成時間元組
                            timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
                            error_number += 1
                            with open(Save_path + '/' +'Record_time.txt','w') as file_recording :
                                file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                file_recording.write('error time : '+str(error_number))

                            if error_number >=3 :
                                with open(Save_path + '/' +'Record_error.txt','a') as file_recording :
                                    file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                    file_recording.write('error time : '+str(error_number))
                                return Already_search_company+1
                            else :
                                return Already_search_company


            if print_process :
                print('\n-- get search web list')


            # -------- 嘗試搜尋 web link --------   
            this_company_not_yet = True # 不論前方是不是有特例 都一定再 ctrl c / ctrl v 一次
            for each_web in range(spcial_number, Company_web_number) :
                print('================================', each_web)
                Search_start_threshold = True
                timesthreshold1 = 0
                while Search_start_threshold : # 開始搜尋
                    try :
                        for i in range(2):
                            pyautogui.moveTo(reset_x,reset_y,duration=0.1)
                        screenshot_time = 3 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                        pre_x , pre_y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_start_confidence)

                        if print_process :
                            print('\n-- Web search start')

                        Search_over_threshold = True
                        timesthreshold2 = 0                 
                        while Search_over_threshold : # 確認搜尋狀況
                            try :
                                screenshot_time = 4 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,click=False,web_result_confidence = search_over_confidence)
                                print('--search end')
                                screenshot_time = 5 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence)
                                print('--check button')
                                # -------------- 導出結果 ---------------
                                screenshot_time = 6 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = web_result_confidence)
                                print('-- stop')
                                screenshot_time = 7 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_searching_confidence)
                                try:
                                    screenshot_time = 5 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                    x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence)
                                except:
                                    need_stop = True
                                print('-- return case1')
                                screenshot_time = 8 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_return_confidence)
                                Search_over_threshold = False
                                print('-- fininsh the web case1')
                            except:
                                sleep(1)
                                timesthreshold2 += 1
                                if timesthreshold2 >= search_upper_limit : # 可以給他搜尋最高___秒
                                    
                                    try:
                                        Search_over_threshold = False
                                        if print_process :
                                            print('Not Found web link')
                                        print('-- stop')
                                        screenshot_time = 7 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_searching_confidence)
                                        try:
                                            screenshot_time = 5 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                            x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence)
                                        except:
                                            need_stop = True
                                        print('-- return fail')
                                        screenshot_time = 8 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                        x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_return_confidence)
                                        print('-- not fininsh the web')
                                    except:
                                        cant_return_raw_page = True
                                        
                                    error_number = 0
                                    try:
                                        with open(Save_path + '/' +'Record_time.txt','r') as file_recording :
                                            for line in file_recording:
                                                if line.find('error time : ')!= -1 :
                                                    error_line = line.replace('\n','').replace('error time : ','')
                                                    error_number = int(error_line)
                                    except:
                                        error_number = 0

                                    for quiting in range(2):
                                        try:
                                            driver.quit()
                                            sleep(10)
                                            print('error occurred')
                                        except:
                                            no_driver = True
                                        
                                    time_stamp = int(time.time())
                                    struct_time = time.localtime(time_stamp) # 轉成時間元組
                                    timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
                                    error_number += 1
                                    with open(Save_path + '/' +'Record_time.txt','w') as file_recording :
                                        file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                        file_recording.write('error time : '+str(error_number))

                                    if error_number >=3 :
                                        with open(Save_path + '/' +'Record_error.txt','a') as file_recording :
                                            file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                            file_recording.write('error time : '+str(error_number))
                                        return Already_search_company+1
                                    else :
                                        return Already_search_company
                                    
                                if print_process :
                                    print('('+str(timesthreshold2)+')',end=' ')

                        # 不論是否成功 返回主搜尋欄                


                        # -------- 複製搜尋結果 --------
                        upper_limmit = 0
                        
                        while this_company_not_yet :
                            for i in range(2):
                                pyautogui.moveTo(reset_x,reset_y,duration=0.1)
                            Screenshot_locateOnScreen_two = True
                            screenshot_time = 2  ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                            while Screenshot_locateOnScreen_two:
                                try:
                                    x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_for_ctrl_confidence)
                                    Screenshot_locateOnScreen_two = False
                                except:
                                    Screenshot_locateOnScreen_two = True
                                    upper_limmit += 1
                                    if upper_limmit >= 10000 :
                                        this_company_not_yet = False
                            sleep(sleep_time)
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.hotkey('ctrl', 'c')

                            for i in range(2):
                                pyautogui.moveTo(x,y,duration=0.1)
                            pyautogui.click()

                            text = pyperclip.paste()
                            search_company_name, searchresult_list = GetSearchResult(text, web_threshold)
                            if print_process :
                                print('\n-- web info : ')
                                print(searchresult_list)      
                            this_company_not_yet = False



                        #tmp_number = 0
                        file_number = len(os.listdir(Save_path+'/data/contact'))
                        if file_number != (each_web+1): # 沒有導出數據
                            empty_list = []
                            empty = pd.DataFrame(empty_list)
                            empty.to_csv(Save_path+'/data/contact/empty.xls', index=False, header=None)

                        file_newest = newest_report(Save_path+'/data/contact')
                        print(str(file_newest))
                        print(Save_path+'/data/contact/' + str(each_web) + '_' + searchresult_list[each_web]['公司名稱'])

                        file_name = re.sub(r"[^a-zA-Z0-9 ]","",searchresult_list[each_web]['公司名稱'])
                        file_name = Save_path+'/data/contact/' + str(each_web) + '_' + file_name + '.xls'
                        os.rename(file_newest, file_name)

                        #shutil.move(file_newest, Save_path+'data/contact/' + searchresult_list[each_web]['公司名稱'] + '.xls')


                        sleep(sleep_time)      
                        Search_start_threshold = False
                        Finish_one_web = True

                    except: # 若失敗 有兩個可能 (1)搜尋有問題 (2)需要往下滑        
                        try:
#                                 for i in range(2):
#                                     pyautogui.moveTo(pre_x,pre_y,duration=0.1)
#                                 pyautogui.click()
                            if Finish_one_web :
                                screenshot_time = 3 ; screenshot_path = All_data_path+rename_lists[screenshot_time]
                                x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = search_over_check_confidence, grayscale=True) # 定位到 灰色開始搜索
                                Finish_one_web = False

                            for i in range(2):
                                pyautogui.moveTo(reset_x,reset_y,duration=0.1)
                            for i in range(1): # slip_times
                                pyautogui.hotkey('down')
                        except:
                            No_pre_x = True

                        sleep(1)
                        timesthreshold1 += 1
                        if timesthreshold1 >= search_upper_limit : # 可以給他搜尋最高___秒
                            Search_start_threshold = False
                            if print_process :
                                print('Not Found 1')
                                
                                error_number = 0
                                try:
                                    with open(Save_path + '/' +'Record_time.txt','r') as file_recording :
                                        for line in file_recording:
                                            if line.find('error time : ')!= -1 :
                                                error_line = line.replace('\n','').replace('error time : ','')
                                                error_number = int(error_line)
                                except:
                                    error_number = 0

                                for quiting in range(2):
                                    try:
                                        driver.quit()
                                        sleep(10)
                                        print('error occurred')
                                    except:
                                        no_driver = True
                                
                                time_stamp = int(time.time())
                                struct_time = time.localtime(time_stamp) # 轉成時間元組
                                timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
                                error_number += 1
                                with open(Save_path + '/' +'Record_time.txt','w') as file_recording :
                                    file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                    file_recording.write('error time : '+str(error_number))

                                if error_number >=3 :
                                    with open(Save_path + '/' +'Record_error.txt','a') as file_recording :
                                        file_recording.write(str(Already_search_company+1)+' error in '+timeString+'\n')
                                        file_recording.write('error time : '+str(error_number))
                                    return Already_search_company+1
                                else :
                                    return Already_search_company
                                
                        if print_process :
                            print('('+str(timesthreshold1)+')',end=' ') 

        # -------- 複製搜尋結果 --------
        this_company_not_yet = True # Combine前再 ctrl c v 一次
        
        upper_limmit2 = 0
        while this_company_not_yet :
            for i in range(2):
                pyautogui.moveTo(reset_x,reset_y,duration=0.1)
            Screenshot_locateOnScreen_two = True
            screenshot_time = 2  ; screenshot_path = All_data_path+rename_lists[screenshot_time]
            while Screenshot_locateOnScreen_two:
                try:
                    x , y = running_screenshot(screenshot_path,reset_x,reset_y,web_result_confidence = stop_for_ctrl_confidence)
                    Screenshot_locateOnScreen_two = False
                except:
                    Screenshot_locateOnScreen_two = True
                    upper_limmit2 += 1
                    if upper_limmit2 >= 10000 :
                        this_company_not_yet = False
            sleep(sleep_time)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')

            for i in range(2):
                pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()

            text = pyperclip.paste()
            search_company_name, searchresult_list = GetSearchResult(text, web_threshold)
            if print_process :
                print('\n-- web info : ')
                print(searchresult_list)      
            this_company_not_yet = False
                            

        if len(os.listdir(Save_path+'/data/contact')) >= Company_web_number:
            GetCombineOutput(search_company_name, searchresult_list, Save_path, Already_search_company, sort_threshold)
            Already_search_company += 1
            print('alred', Already_search_company)


        # ------------------ 未達到最後目標 且下個目標在下一頁 ------------------ # 翻頁制度 要注意小於5面tab數量需不同 要注意>=5之後 ~ <=4 之間會多一格 
        if Already_search_company < Company_number :
            if ( Already_search_company % 20 ) == 0 :
                
                now_Page = int(Already_search_company/20)
                
                moving_2_want_search_company = 19
                move_2_chi(Big_x, Big_y) # 上滑
#                     if Company_type == 'A': # 進口商
                move_2_company_timespany_times = 2 + moving_2_want_search_company*9 
                for i in range(move_2_company_timespany_times):
                    pyautogui.hotkey('tab')
                sleep(sleep_time)

                move_2_company_timespany_times = 7 
                for i in range(move_2_company_timespany_times):
                    pyautogui.hotkey('tab')
                sleep(sleep_time)    

                Next_page = 7
                if First_page :
                    First_page = False
                    Next_page -= 1
                    
                if upper_page <= 5 :
                    remove_tab_time = 6 - upper_page
                    Next_page -= remove_tab_time
                elif upper_page >5 and now_Page>=5 and (upper_page-now_Page)>= 4 :
                    Next_page += 1 
                    
                for i in range(Next_page):
                    pyautogui.hotkey('tab')
                sleep(sleep_time)        
                pyautogui.hotkey('enter')
                sleep(next_page_sleep_time) # 換頁
    
    print('Finish')
    return -100

# ------ Read setting ------    
# All_data_path = 'D:/Record/AI_Technology/Data/20220309_23_05/'
Recording = []
with open(str(pathlib.Path().absolute())+'\\'+'record.txt','r') as file :
    for line in file :
        rec = line.replace('\n','')
        Recording.append(rec)
        
All_data_path = Recording[0]

# ------ 縮放 ------
size = int(Recording[-1])

# ------ 字體字型 ------
fontsize = 8 * size
fonttype = '標楷體'

# ------ 元件位置 ------
label_x = 70 * size
inputbox_x = 350 * size
y_top = 20 * size
y_range = 30 * size

# ------ 元件大小 ------
label_width = 200 * size
label_height = 30 * size
input_width = 300 * size
input_height = 30 * size

# ------ 元件順序 ------
下拉式選單_年份 = 0 # comGrade
日期輸入1 = 1
日期輸入2 = 2
日期輸入3 = 3
輸入欄位_海關編碼 = 4 # landString
輸入欄位_產品英文全名 = 5 # goodString
輸入欄位_進口商國家 = 6 # cityString
輸入欄位_搜尋公司數 = 7 # companyString
輸入欄位_搜尋網站數 = 8 # webString
起始位置 = 9
單選圓鈕_進口 = 10 # radioValue
單選圓鈕_出口 = 11
單選圓鈕_開啟排序 = 10
單選圓鈕_關閉排序 = 11

路徑選擇 = 13
按鈕_顯示輸入 = 14
開始搜尋 = 15
執行進度 = 17

# ------ GUI大小 ------
GUI_width = str(750 * size )
GUI_height = str(600 * size )

# ------ 記憶功能 ------
try:
    with open(All_data_path+'Record_input.txt','r') as file_recording :
        for line in file_recording :
            if line.find('Timeline : ')!= -1:
                Year_record = line.replace('Timeline : ','').replace('\n','')
                if Year_record == '最近月':time_section_record = 0
                elif Year_record == '本年':time_section_record = 1
                elif Year_record == '上年':time_section_record = 2
                elif Year_record == '前2年':time_section_record = 3
                elif Year_record == '前3年':time_section_record = 4
            if line.find('Date1 : ')!= -1:
                Date1_record = line.replace('Date1 : ','').replace('\n','')
            if line.find('Date2 : ')!= -1:
                Date2_record = line.replace('Date2 : ','').replace('\n','')
            if line.find('Port : ')!= -1:
                Port_record = line.replace('Port : ','').replace('\n','')
            if line.find('Goods : ')!= -1:
                Goods_record = line.replace('Goods : ','').replace('\n','')
            if line.find('Port_country : ')!= -1:
                port_country_record = line.replace('Port_country : ','').replace('\n','')
                if port_country_record == '進口商國家':port_section_record = 0
                elif port_country_record == '出口商國家':port_section_record = 1
            if line.find('Citys : ')!= -1:
                Citys_record = line.replace('Citys : ','').replace('\n','')
            if line.find('Search : ')!= -1:
                port_search_record = line.replace('Search : ','').replace('\n','')
    Record_text = True
except:
    time_section_record = 2
    Date1_record = '2021-10-01'
    Date2_record = '2021-12-31'
    Port_record = '3924'
    Goods_record = 'plastic'
    port_section_record = 0
    Citys_record = 'United States'
    port_search_section_record ='A'
    port_search_record = '企查通搜尋進口商'
    Record_text = False
        
# ----------------- GUI ----------------- 

window = tk.Tk()
window.title('海關數據平台爬蟲軟體')
window.geometry(GUI_width+'x'+GUI_height)
window.resizable(False, False) 
window.iconbitmap(All_data_path+'logal.ico')

num1 = 單選圓鈕_進口   
num2 = 單選圓鈕_出口  
radioValue = tk.StringVar();radioValue.set(port_search_record)
rdioOne = tk.Radiobutton(window, text='企查通搜尋進口商', font=(fonttype, fontsize),variable=radioValue, value='企查通搜尋進口商',indicator = 0) 
rdioTwo = tk.Radiobutton(window, text='企查通搜尋出口商', font=(fonttype, fontsize),variable=radioValue, value='企查通搜尋出口商',indicator = 0) 
rdioOne.place(x=label_x, y=y_top+y_range*num1)
rdioTwo.place(x=label_x, y=y_top+y_range*num2)

num1_2 = 單選圓鈕_開啟排序
num2_2 = 單選圓鈕_關閉排序
radioValue2 = tk.StringVar();radioValue2.set('開啟自動排序')
rdioOne2 = tk.Radiobutton(window, text='開啟自動排序', font=(fonttype, fontsize),variable=radioValue2, value='開啟自動排序',indicator = 0) 
rdioTwo2 = tk.Radiobutton(window, text='關閉自動排序', font=(fonttype, fontsize),variable=radioValue2, value='關閉自動排序',indicator = 0) 
rdioOne2.place(x=inputbox_x, y=y_top+y_range*num1_2)
rdioTwo2.place(x=inputbox_x, y=y_top+y_range*num2_2)

num = 下拉式選單_年份
labGrade = tk.Label(window, text = '年份:', font=(fonttype, fontsize))
labGrade.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
stdGrade = ('最近月', '本年','上年','前2年','前3年','全部')
comGrade = tt.Combobox(window, values=stdGrade,font=(fonttype, fontsize))
comGrade.current(time_section_record) # 預設
comGrade.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)


num = 輸入欄位_海關編碼   
landString = tk.StringVar();landString.set(Port_record)
labelLand = tk.Label(window,text = "海關編碼", font=(fonttype, fontsize))
labelLand.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
entryLand = tk.Entry(window, textvariable=landString,font=(fonttype, fontsize))
entryLand.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)

num = 輸入欄位_產品英文全名
labelweb = tk.Label(window,text = "產品名稱", font=(fonttype, fontsize))
labelweb.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height) 
goodString = tk.StringVar();goodString.set(Goods_record) 
entrygoods = tk.Entry(window, textvariable=goodString,font=(fonttype, fontsize))
entrygoods.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)

num = 輸入欄位_進口商國家
stdGrade2 = ('進口商國家', '出口商國家')
comGrade2 = tt.Combobox(window, values=stdGrade2,font=(fonttype, fontsize))
comGrade2.current(port_section_record) # 預設
comGrade2.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
# labelCity = tk.Label(window,text = "進/出口商國家", font=(fonttype, fontsize) )
# labelCity.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height) 
cityString = tk.StringVar();cityString.set(Citys_record) 
entryCity = tk.Entry(window, textvariable=cityString ,font=(fonttype, fontsize))
entryCity.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)
    
num = 輸入欄位_搜尋公司數
labelcompany = tk.Label(window,text = "搜尋公司數", font=(fonttype, fontsize))
labelcompany.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height) 
companyString = tk.StringVar();companyString.set('Max') 
entrycompany = tk.Entry(window, textvariable=companyString ,font=(fonttype, fontsize))
entrycompany.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)

num = 輸入欄位_搜尋網站數
labelweb = tk.Label(window,text = "搜尋網站數", font=(fonttype, fontsize))
labelweb.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
webString = tk.StringVar();webString.set('3') 
entryweb = tk.Entry(window, textvariable=webString ,font=(fonttype, fontsize))
entryweb.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)   

num = 起始位置
labelcompany_number = tk.Label(window,text = "已完成公司數量", font=(fonttype, fontsize))
labelcompany_number.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
company_numberString = tk.StringVar();company_numberString.set('0') 
entrycompany_number = tk.Entry(window, textvariable=company_numberString ,font=(fonttype, fontsize))
entrycompany_number.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)  

num = 路徑選擇
save_path = tk.StringVar();save_path.set('') 
def selectPath():
    path_ = askdirectory()
    save_path.set(path_) 
    Entry_save_path.config(fg = 'black')
Button_save_path = tk.Button(window, text = "存放路徑選擇", font=(fonttype, fontsize), command = selectPath);Button_save_path.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height) 
Entry_save_path = tk.Entry(window, textvariable = save_path,font=(fonttype, fontsize));Entry_save_path.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)  


num = 按鈕_顯示輸入
def callbackFunc():
    resultString.set("{}-{}-{}-{}-{}-{}-{}".format(comGrade.get(),landString.get(),goodString.get(),cityString.get(),companyString.get(),webString.get(),radioValue.get()))
resultString=tk.StringVar();resultString.set('{}-{}-{}-{}-{}-{}-{}')
resultLabel = tk.Label(window, textvariable=resultString ,font=(fonttype, int(fontsize*0.5)))
resultLabel.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)
resultButton = tk.Button(window, text = '輸入確認', font=(fonttype, fontsize),command=callbackFunc)
resultButton.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)

num = 日期輸入1
tk.Label(window,text='日期 : ', font=(fonttype, fontsize)).place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)


def getdate(type):	#获取选择的日期
    for date in [Calendar().selection()]:
        if date:
            if(type=='start'):	#如果是开始按钮，就赋值给开始日期
                start_date.set(date)
            elif(type=='end'):
                end_date.set(date)

num = 日期輸入2
start_date=tk.StringVar();start_date.set(Date1_record)
end_date=tk.StringVar();end_date.set(Date2_record)
bt1=tk.Button(window,text='開始', font=(fonttype, fontsize),command=lambda:getdate('start'))
bt1.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
ent1=tk.Entry(window,textvariable=start_date, font=(fonttype, fontsize))
ent1.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)

num = 日期輸入3
bt2=tk.Button(window,text='結束', font=(fonttype, fontsize),command=lambda:getdate('end'))
bt2.place(x=label_x, y=y_top+y_range*num, width=label_width, height=label_height)
ent2=tk.Entry(window,textvariable=end_date, font=(fonttype, fontsize))
ent2.place(x=inputbox_x, y=y_top+y_range*num, width=input_width, height=input_height)

startstamp1=start_date.get()
endstamp1=end_date.get()

# 显示下载进度
def progress():
    # --------------- pre-processing input info --------------- 
    Year = comGrade.get()
    if Year == '最近月':time_section = 0
    elif Year == '本年':time_section = 1
    elif Year == '上年':time_section = 2
    elif Year == '前2年':time_section = 3
    elif Year == '前3年':time_section = 4
        
    port = landString.get();port_input = port.split(',')
    goods = goodString.get();goods_input = goods.split(',')
    
    port_country = comGrade2.get()
    if port_country == '進口商國家':port_section = 0
    elif port_country == '出口商國家':port_section = 1
    citys = cityString.get();citys_input = citys.split(',')

    port_search = radioValue.get()
    sort_threshold = radioValue2.get()
    if port_search == '企查通搜尋進口商':port_search_section = 'A'
    elif port_search == '企查通搜尋出口商':port_search_section = 'B'
        
    company_threshold = companyString.get()
    web_threshold  = webString.get()
    savedirpath  = save_path.get()
    Already_search_company  =  int(company_numberString.get())
    
    start_date_threshold = start_date.get()
    end_date_threshold = end_date.get()
    Date = [start_date_threshold,end_date_threshold]
    
    # ---------------------- check input info ----------------------
    if savedirpath == '':
        save_path.set('請選擇存放路徑')
        Entry_save_path.config(fg = 'red')
        return -1
    
    if web_threshold.isdigit() == False :
        webString.set('請輸入大於0之數字')
        entryweb.config(fg = 'red')
        return -1
    else: 
        if float(web_threshold) > 0 :
            web_threshold = int(web_threshold)
        else:
            webString.set('請輸入大於0之數字')
            entryweb.config(fg = 'red')
            return -1

    try:
        with open(savedirpath + '/' +'Record_result.txt','r') as file_recording :
            for line in file_recording:
                if line.find('已搜尋公司數 : ')!= -1 :
                    data_already_save = line.replace('已搜尋公司數 : ','').replace('\n','')
                    data_already_save = int(data_already_save)
    except:
        try:
            mypath = savedirpath+'/search_result/'
            data_already_save = 0
            # 取得所有檔案與子目錄名稱
            files = listdir(mypath)
            # 以迴圈處理
            for f in files:
              # 產生檔案的絕對路徑
              fullpath = join(mypath, f)
              # 判斷 fullpath 是檔案還是目錄
              if isfile(fullpath):
                if fullpath[-4:] == '.csv' :
                    print("檔案：", f)        
                    data_already_save += 1
        except:
            data_already_save = 0
        
    mkdir_dir(savedirpath)
        
    if data_already_save != Already_search_company :
        company_numberString.set('內有csv,請調整為'+str(data_already_save))
        entrycompany_number.config(fg = 'red')
        return -1
    
    # --------------- running --------------- 
    
    try:
        with open(savedirpath + '/' +'Record_input.txt','w') as file_recording :
            file_recording.write('Timeline : '+str(Year)+'\n')
            file_recording.write('Date1 : '+str(Date[0])+'\n')        
            file_recording.write('Date2 : '+str(Date[1])+'\n')       
            file_recording.write('Port : '+str(port)+'\n')
            file_recording.write('Goods : '+str(goods)+'\n')
            file_recording.write('Port_country : '+str(port_country)+'\n')
            file_recording.write('Citys : '+str(citys)+'\n')
            file_recording.write('Search : '+str(port_search)+'\n')
            time_stamp = int(time.time())
            struct_time = time.localtime(time_stamp) # 轉成時間元組
            timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
            file_recording.write('Search time : '+str(timeString)+'\n')
    except:
        with open(savedirpath + '/' +'Record_input.txt','a') as file_recording :
            file_recording.write('Timeline : '+str(Year)+'\n')
            file_recording.write('Date1 : '+str(Date[0])+'\n')        
            file_recording.write('Date2 : '+str(Date[1])+'\n')       
            file_recording.write('Port : '+str(port)+'\n')
            file_recording.write('Goods : '+str(goods)+'\n')
            file_recording.write('Port_country : '+str(port_country)+'\n')
            file_recording.write('Citys : '+str(citys)+'\n')
            file_recording.write('Search : '+str(port_search)+'\n')
            time_stamp = int(time.time())
            struct_time = time.localtime(time_stamp) # 轉成時間元組
            timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
            file_recording.write('Search time : '+str(timeString)+'\n')
        
    try:
        with open(All_data_path+'Record_input.txt','w') as file_recording :
            file_recording.write('Timeline : '+str(Year)+'\n')
            file_recording.write('Date1 : '+str(Date[0])+'\n')        
            file_recording.write('Date2 : '+str(Date[1])+'\n')        
            file_recording.write('Port : '+str(port)+'\n')
            file_recording.write('Goods : '+str(goods)+'\n')
            file_recording.write('Port_country : '+str(port_country)+'\n')
            file_recording.write('Citys : '+str(citys)+'\n')
            file_recording.write('Search : '+str(port_search)+'\n')
            time_stamp = int(time.time())
            struct_time = time.localtime(time_stamp) # 轉成時間元組
            timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
            file_recording.write('Search time : '+str(timeString)+'\n')
    except:
        with open(All_data_path+'Record_input.txt','a') as file_recording :
            file_recording.write('Timeline : '+str(Year)+'\n')
            file_recording.write('Date1 : '+str(Date[0])+'\n')        
            file_recording.write('Date2 : '+str(Date[1])+'\n')     
            file_recording.write('Port : '+str(port)+'\n')
            file_recording.write('Goods : '+str(goods)+'\n')
            file_recording.write('Port_country : '+str(port_country)+'\n')
            file_recording.write('Citys : '+str(citys)+'\n')
            file_recording.write('Search : '+str(port_search)+'\n')
            time_stamp = int(time.time())
            struct_time = time.localtime(time_stamp) # 轉成時間元組
            timeString = time.strftime("%Y%m%d_%H%M", struct_time) # 轉成字串
            file_recording.write('Search time : '+str(timeString)+'\n')        
    
    Already_search_company_new = 爬蟲(Date,time_section,port_input,goods_input,port_section,citys_input,port_search_section,company_threshold,web_threshold,sort_threshold,All_data_path,savedirpath,Already_search_company,Recording,print_process = True)
    while Already_search_company_new != -1 or Already_search_company_new != -100 :
        print('Again')
        Already_search_company_new = 爬蟲(Date,time_section,port_input,goods_input,port_section,citys_input,port_search_section,company_threshold,web_threshold,sort_threshold,All_data_path,savedirpath,Already_search_company_new,Recording,print_process = True)
    if Already_search_company_new == -100 :
        save_path.set('已執行完畢感謝您的使用')
        Entry_save_path.config(fg = 'red')
    
num = 開始搜尋 
btn_download = tk.Button(window, text='開始搜尋', font=(fonttype, fontsize), command=progress)
btn_download.place(x=label_x, y=y_top+y_range*num, width=500* size, height=50* size)

num = 執行進度 
tk.Label(window,text='執行進度:',font=(fonttype, fontsize) ).place(x=label_x, y=y_top+y_range*num)
canvas = tk.Canvas(window, width=380* size, height=22* size, bg="white")
canvas.place(x=label_x+200*size, y=y_top+y_range*num)

window.mainloop()
