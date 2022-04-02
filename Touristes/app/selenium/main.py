from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By



s=Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=s,options=options)
driver.maximize_window()
driver.get("https://meet.jit.si/12344321qwedsds")
input()
spanz = driver.find_elements(By.CSS_SELECTOR, "span.videocontainer")
for span in spanz:
  if 'participant_' in span.get_attribute('id'):
    print(span)


