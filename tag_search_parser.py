from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,TimeoutException

import json
import logging

from common import extract_article_name, get_logger
from constants import ARTICLES_PATH

class TagSearchParser:

  logger : logging.Logger
  driver : webdriver.Chrome

  def __init__(self):
    self.logger = get_logger("tag_search_log","tag_search_parsing.log")
    self.logger.info("Creating browser...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    self.driver = webdriver.Chrome(options=options)

  def apply_tags(self, tags : list[str]) -> None:
    for tag in tags:
      self.logger.info(f"Adding tag {tag} to query")
      text_input = self.driver.find_element(By.XPATH, "//input")
      text_input.send_keys(tag)
      text_input.send_keys(Keys.ENTER)

  def load_more(self) -> None:
    while True:
      try:
        button = WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Load more')]"))
        )
        self.logger.info(f"Loading more results")
        #driver.execute_script("arguments[0].scrollIntoView()", button)
        button.click()
      except Exception as e:
        #print(e)
        break
    self.logger.info(f"Loading finished")

    button = WebDriverWait(self.driver, 10).until(
          EC.invisibility_of_element_located((By.XPATH, "//button[contains(.,'Load more')]"))
    )

  def _extract_entry_from_list_item(self, item) -> dict[str, str]:
    name = item.find_element(By.XPATH, "./a").get_attribute('href')
    name = extract_article_name(name)
    authors = item.find_elements(By.XPATH, "./div/span/span")[1:]
    authors = [author.text[:-1] if author.text[-1] == "," else author.text for author in authors]
    return {"name" : name, "authors" : authors}
  
  def cancel_tags(self) -> None:
    tag_cancel_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Delete')]")
    
    for tag_cancel_button in tag_cancel_buttons: 
      tag_cancel_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Delete')]")
      tag_cancel_button = WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable(tag_cancel_button)
      )
      self.driver.execute_script("arguments[0].scrollIntoView()", tag_cancel_button)
      tag_cancel_button.click()

#TODO wrong type hints
  def get_article_urls_for_tags(self, tags : list[str]) -> list[str]:

    self.apply_tags(tags)

    self.load_more()

    items = self.driver.find_elements(By.XPATH, "//li[.//a]")
    result = [self._extract_entry_from_list_item(item) for item in items]

    self.cancel_tags()

    return result

  def get_article_urls_for_tag_sets(self, tag_sets : list[list[str]]) -> list[list[str]]:
    self.logger.info(f"Getting the article list for tag sets: {tag_sets}")
    result = {}
    for tags in tag_sets:
      self.logger.info(f"Searching for tags: {tags}")
      result[", ".join(tags)] = self.get_article_urls_for_tags(tags)
    return result

  def close_cookiebox(self):
    self.driver.execute_script("cookiesAreOk()")
  

  def query_tag_search(self, tag_sets : list[list[str]]) -> list[list[str]]:
    self.logger.info("Fetching the page")
    url = "https://scp-wiki.wikidot.com/tag-search"
    self.driver.get(url)
    self.close_cookiebox()
    self.logger.info("Switching to iframe")
    iframe = self.driver.find_element(By.XPATH, "//div[@id='u-loading']/following-sibling::iframe")
    self.driver.switch_to.frame(iframe)

    iframe = self.driver.find_element(By.XPATH, "//iframe[@id='crom-frame']")
    self.driver.switch_to.frame(iframe)

    result = self.get_article_urls_for_tag_sets(tag_sets)
    self.driver.quit()
    return result

  def save_list_of_articles(self, tag_sets : list[list[str]], filename : str):
    response = self.query_tag_search(tag_sets)
    with open(ARTICLES_PATH + filename, "w") as file:
      json.dump(response, file)
