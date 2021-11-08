# import time
# from selenium import webdriver
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from webdriver_manager.chrome import ChromeDriverManager
# import json

# ##### Web scrapper for infinite scrolling page #####
# driver = webdriver.Chrome(ChromeDriverManager().install())
# driver.get("https://www.reddit.com/search/?q=r%2FCOVID19")
# time.sleep(2)  # Allow 2 seconds for the web page to open
# scroll_pause_time = 1 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
# screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
# i = 1

# while True:
#     # scroll one screen height each time
#     driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
#     i += 1
#     time.sleep(scroll_pause_time)
#     # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
#     scroll_height = driver.execute_script("return document.body.scrollHeight;")  
#     # Break the loop when the height we need to scroll to is larger than the total scroll height
#     if (screen_height) * i > scroll_height:
#         break 

# ##### Extract Reddit URLs #####
# urls = []
# soup = BeautifulSoup(driver.page_source, "html.parser")
# for parent in soup.find_all(class_="y8HYJ-y_lTUHkQIc1mdCq _2INHSNB8V5eaWp4P0rY_mE"):
#     a_tag = parent.find("a", class_="SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE")
#     base = "https://www.reddit.com/search/?q=covid19"
#     link = a_tag.attrs['href']
#     url = urljoin(base, link)
#     urls.append(url)
#     with open("HUY.json", "w") as jsonFile:
#         jsonFile.write(json.dumps(urls, indent=4))




import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
import json

##### Web scrapper for infinite scrolling page #####
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://rarible.com")
time.sleep(2)  # Allow 2 seconds for the web page to open
scroll_pause_time = 1 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")  
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break 
    recommendation_element = driver.find_element_by_class_name("ReactVirtualized__Grid__innerScrollContainer")
    print(recommendation_element.text)

# ##### Extract Reddit URLs #####
# urls = []
# soup = BeautifulSoup(driver.page_source, "html.parser")
# dom = etree.HTML(str(soup))
# # print(dom.xpath('//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div[8]/div[2]/div').text)
# for parent in dom.xpath('//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div[8]/div[2]/div'):
#     print(parent)
# #     a_tag = parent.//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div[8]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/a/img
# #     print(a_tag)
#     # base = "https://www.reddit.com/search/?q=covid19"
#     # link = a_tag.attrs['href']
#     # url = urljoin(base, link)
#     # urls.append(url)
#     # with open("HUY.json", "w") as jsonFile:
#     #     jsonFile.write(json.dumps(urls, indent=4))



##### Extract Reddit URLs #####
# driver.page_source
# urls = []
# soup = BeautifulSoup(driver.page_source, "html.parser")
# # [-1].find_all("div")[-1].find_all("div")[-1].find_all("div")[0].find_all("div")[0]).find("div").find_all("div")[-1].find_all("div")[-1].find("div"))
# print(len(soup.find("body").find("div").find_all("div")))
# print(len(soup.find("div",class_="ReactVirtualized__Grid__innerScrollContainer").find("div",class_="ReactVirtualized__Grid__innerScrollContainer")))
# for parent in soup.find("div",class_="ReactVirtualized__Grid").find("div",class_="ReactVirtualized__Grid__innerScrollContainer"):
#     # print(parent)
#     a_tag = parent.find("div").find_all("div")[-1]
#     print(a_tag)
    # base = "https://www.reddit.com/search/?q=covid19"
    # link = a_tag.attrs['href']
    # url = urljoin(base, link)
    # urls.append(url)
    # with open("HUY.json", "w") as jsonFile:
    #     jsonFile.write(json.dumps(urls, indent=4))
