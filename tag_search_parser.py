from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import requests
from bs4 import BeautifulSoup
from lxml import etree

def dump_page(driver, path):
  page = driver.page_source
  with open(path, "w", encoding="utf-8") as file:
    file.write(page)

def apply_tags(driver, tags : list[str]) -> None:
  text_input = driver.find_element(By.XPATH, "//input")
  for tag in tags:
    text_input.send_keys(tag)
    text_input.send_keys(Keys.ENTER)

def load_more(driver) -> None:
  while True:
    try:
      button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Load more')]"))
      )
      button.click()
    except:
      break

  button = WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, "//button[contains(.,'Load more')]"))
  )
  
def cancel_tags(driver) -> None:
  tag_cancel_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Delete')]")
  
  for tag_cancel_button in tag_cancel_buttons: 
    tag_cancel_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Delete')]")
    tag_cancel_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(tag_cancel_button)
    )
    driver.execute_script("arguments[0].scrollIntoView()", tag_cancel_button)
    tag_cancel_button.click()

def get_article_urls_for_tags(driver, tags : list[str]) -> list[str]:

  apply_tags(driver, tags)

  load_more(driver)

  links = driver.find_elements(By.XPATH, "//li/a")
  result = [link.get_attribute('href') for link in links]

  cancel_tags(driver)

  return result

def get_article_urls_for_tag_sets(driver, tag_sets : list[list[str]]) -> list[list[str]]:
  result = []
  for tags in tag_sets:
    result.append(get_article_urls_for_tags(driver, tags)) 
  return result

def query_tag_search(tag_sets : list[list[str]]) -> list[list[str]]:
  options = webdriver.ChromeOptions()
  options.add_argument('--headless=new')
  options.add_argument('--no-sandbox')
  # options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=options)

  url = "https://scp-wiki.wikidot.com/tag-search"
  driver.get(url)

  iframe = driver.find_element(By.XPATH, "//div[@id='u-loading']/following-sibling::iframe")
  driver.switch_to.frame(iframe)

  iframe = driver.find_element(By.XPATH, "//iframe[@id='crom-frame']")
  driver.switch_to.frame(iframe)

  return get_article_urls_for_tag_sets(driver, tag_sets)

def save_list_of_articles(tag_sets : list[list[str]], path : str):
  response = query_tag_search(tag_sets)
  with open(path, "w") as file:
    for links in response:
      for link in links:
        name = link.split("/")[-1]
        file.write(f"{name},")

#["scp"],["tale"],["site"],["hub"],
save_list_of_articles([["scp"],["tale"],["site"],["hub"],["goi-format"]], "links.txt")


