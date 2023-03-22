from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
import urllib

chrome_options = Options()
driver = Chrome(chrome_options=chrome_options) # for inner primers
driver.get('https://gpss1.tipo.gov.tw/gpsskmc/gpssbkm?@@0.4363377086102256')
save_path = 'D:/Record/'
count_id = 0
for element in driver.find_elements_by_tag_name('img'):
    img_url = element.get_attribute('src')
    if img_url[-4:]!='.png' and img_url.find('.png')!='-1' : # 不同網站請做不同過濾
        count_id += 1
        urllib.request.urlretrieve(img_url, save_path+'png_'+str(count_id)+'.png')
