from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,TimeoutException

import json

import logging
import sys

from common import extract_article_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

fileHandler = logging.FileHandler("tag_search_parsing.log", encoding="utf-8")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def apply_tags(driver, tags : list[str]) -> None:
  for tag in tags:
    logger.info(f"Adding tag {tag} to query")
    text_input = driver.find_element(By.XPATH, "//input")
    text_input.send_keys(tag)
    text_input.send_keys(Keys.ENTER)

def load_more(driver) -> None:
  while True:
    try:
      button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Load more')]"))
      )
      logger.info(f"Loading more results")
      #driver.execute_script("arguments[0].scrollIntoView()", button)
      button.click()
    except Exception as e:
      #print(e)
      break
  logger.info(f"Loading finished")

  button = WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, "//button[contains(.,'Load more')]"))
  )

def extract_entry_from_list_item(item) -> dict[str, str]:
  name = item.find_element(By.XPATH, "./a").get_attribute('href')
  name = extract_article_name(name)
  authors = item.find_elements(By.XPATH, "./div/span/span")[1:]
  authors = [author.text[:-1] if author.text[-1] == "," else author.text for author in authors]
  return {"name" : name, "authors" : authors}
  
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

  # links = driver.find_elements(By.XPATH, "//li/a")
  # result = [{"name" : link.get_attribute('href')} for link in links]

  items = driver.find_elements(By.XPATH, "//li[.//a]")
  result = [extract_entry_from_list_item(item) for item in items]

  cancel_tags(driver)

  return result

def get_article_urls_for_tag_sets(driver, tag_sets : list[list[str]]) -> list[list[str]]:
  logger.info(f"Getting the article list for tag sets: {tag_sets}")
  result = {}
  for tags in tag_sets:
    logger.info(f"Searching for tags: {tags}")
    result[", ".join(tags)] = get_article_urls_for_tags(driver, tags)
  return result

def close_cookiebox(driver):
  driver.execute_script("cookiesAreOk()")
  

def query_tag_search(tag_sets : list[list[str]]) -> list[list[str]]:
  logger.info("Creating browser...")
  options = webdriver.ChromeOptions()
  options.add_argument('--headless=new')
  options.add_argument('--no-sandbox')
  # options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=options)
  logger.info("Fetching the page")
  url = "https://scp-wiki.wikidot.com/tag-search"
  driver.get(url)
  close_cookiebox(driver)
  logger.info("Switching to iframe")
  iframe = driver.find_element(By.XPATH, "//div[@id='u-loading']/following-sibling::iframe")
  driver.switch_to.frame(iframe)

  iframe = driver.find_element(By.XPATH, "//iframe[@id='crom-frame']")
  driver.switch_to.frame(iframe)

  result = get_article_urls_for_tag_sets(driver, tag_sets)
  driver.quit()
  return result

def save_list_of_articles(tag_sets : list[list[str]], path : str):
  response = query_tag_search(tag_sets)
  with open(path, "w") as file:
    json.dump(response, file)
