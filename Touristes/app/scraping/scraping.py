import time

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from api.models.user import User
import requests


s = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()
driver.get("https://meet.jit.si/12344321qwedsds")
users_list = []


def launch_chrome():
    input()
    spanz = driver.find_elements(By.CSS_SELECTOR, "span.videocontainer")
    videos = driver.find_elements(By.CSS_SELECTOR, "span.videocontainer:not(#localVideoContainer) video")
    i = 1
    for span in spanz:
        name = ""
        if 'participant_' in span.get_attribute('id'):
            name = span.find_elements(By.CSS_SELECTOR, "span.displayname")
            print(name[0].get_attribute("innerText"))
            videos = span.find_element(By.CSS_SELECTOR, "video")
            print(videos)
            user = User(span.get_attribute('id'), name[0].get_attribute("innerText"), videos)
            users_list.append(user)
            i = i + 1


def getImages():
    while (True):
        spanz = driver.find_elements(By.CSS_SELECTOR, "span.videocontainer")
        for user in users_list:
                for span in spanz:
                    if user.id == span.get_attribute('id'):
                        img = span.find_element(By.CSS_SELECTOR, "video").screenshot_as_base64
                        post = requests.post("http://localhost:5000/calculateScore", data={"id": user.id, "name": user.name, "img": img})
        time.sleep(10)


launch_chrome()
getImages()
