#extracting crosslinks from an article

from common import get_logger

logger = get_logger("parsing.log")

import requests
from bs4 import BeautifulSoup
from lxml import etree
import json
import jsonlines

from common import extract_article_name
from constants import CANONICAL_BASE_URL, ALTERNATE_BASE_URLS


def get_article(article_name : str, offset : str = 0) -> BeautifulSoup:
  #build the url
  url = CANONICAL_BASE_URL + article_name
  if offset != 0:
    url += f"/offset/{offset}"
  #fetch the page
  try:
    r = requests.get(url)
    r.raise_for_status()
  except requests.exceptions.HTTPError as err:
    logger.error(f"Failed to fetch article {article_name}{", offset="+offset if offset != 0 else ""}, error: {err}")
    raise err
  logger.info(f"Succesfuly fetched article {article_name}{", offset="+offset if offset != 0 else ""}")
  s = BeautifulSoup(r.content, "html.parser")

  return s

def parse_article(article_name : str, offset : str = 0):
  logger.info(f"Attempting parsing article {article_name}{", offset="+offset if offset != 0 else ""}")
  try:
    s = get_article(article_name, offset)
  except requests.exceptions.HTTPError as err:
    return [], [], 0
  crosslinks = get_crosslinks(s, article_name, offset)
  tags = get_tags(s)
  rating = get_rating(s)
  return crosslinks, tags, rating

def get_rating(s):
  et = etree.HTML(str(s))
  rating_span = et.xpath("//span[contains(@class,'prw54353')]")
  try:
    rating = int(rating_span[0].text)
    logger.info(f"Rating found: {rating}")
  except IndexError:
    logger.warning(f"Failed to find rating, setting to 0")
    rating = 0
  except ValueError:
    logger.warning(f"Rating found, but not a valid number ({rating}), setting to 0")
    rating = 0
  return rating
  

def get_tags(s):
  et = etree.HTML(str(s))
  tag_div = et.xpath("//div[@class='page-tags']")
  if len(tag_div) != 1:
    logger.warning("Failed to find the tag section")
    return []
  tag_links = tag_div[0].xpath(".//a")
  tags = [tag.text for tag in tag_links if not tag.text.startswith("_")]
  logger.info(f"Tags found: {", ".join(tags)}")
  return tags

#function takes in article name (the last part of the url, e. g. 'scp-2311' or 'taboo'), and optionally an offset value
def get_crosslinks(s : BeautifulSoup, article_name : str, offset : str = 0, visited_offsets=None) -> list[str]:
  
  if visited_offsets is None: visited_offsets = ["0"]
  et = etree.HTML(str(s))

  #to find crosslinks, we look for <a> tags inside the page-content div
  #the problem is that page-content may also include things that are not 'real' crosslinks
  #like the ones on the nav bar or license info or link to an author page
  #so we need to filter those out
  #fortunately, we're going to preemptively limit the domain, so even if we let some, say, author pages slide through they won't be included in the graph anyway
  crosslinks = et.xpath("//div[@id='page-content']//a[not(ancestor::div[@class='footer-wikiwalk-nav']) and not(ancestor::div[@class='licensebox']) and not(ancestor::div[@id='u-author_block']) and not(ancestor::div[@class='u-faq'])]")

  result = []

  for crosslink in crosslinks:
    target = crosslink.get("href")

    #filter out the links that go outside the wiki
    #internal links can be relative (e. g. '/taboo') or absolute (e.g. 'https://scp-wiki.wikidot.com/scp-8190'))
    if target is None:
      continue
    try:
      target = extract_article_name(target)
    except ValueError:
      continue

    #this is for identifying offset pages
    levels = target.split("/")

    #if we find a link to an offset page of the same article, we need to follow it and append any crosslinks we find there to our list
    #after all, an offset page is still part of the same article
    #here I follow any offset link that has offset greater than the current one
    #this prevents infinite loops, but may cause us to parse some offset pages more than once if there are multiple links to it across the article
    #this should not be much of a problem
    try:
      if levels[1] == "offset" and levels[0] == article_name:
        found_offset = levels[2]
        if found_offset not in visited_offsets:
          visited_offsets.append(found_offset)
          logger.info(f"Found an offset page, number {found_offset}; following")
          result.extend(get_crosslinks(get_article(article_name, found_offset), article_name, found_offset, visited_offsets))
    except:
      pass

    #before adding a link to an offset page, we remove the offset
    #that is, we want to treat a crosslink to scp-6500/offset/16 as simply a crosslink to scp-6500
    if "/offset/" in target:
      target = target[:target.find("/offset/")]
    #likewise, remove parameters
    #we do not want shit like scp-255?theme_url=/local--files/scp-255/noeffect.css
    if "?" in target:
      target = target[:target.find("?")]
    #nor do we want task-forces#alpha-1
    if "#" in target:
      target = target[:target.find("#")]
    #do not include self-links
    if target == article_name:
      continue
    result.append(target)
  #at the end, we remove the duplicates
  crosslinks = list(set(result))
  logger.info(f"Crosslinks found: {", ".join(crosslinks)}")
  return crosslinks

def parse_and_save_articles(input_path : str, output_path : str, starter : str = None):
  with open(input_path, "r") as input_file:
    articles_dict = json.load(input_file)
  articles = [article for articles_list in articles_dict.values() for article in articles_list]
  with jsonlines.open(output_path, "a") as writer:
    for entry in articles:

      if starter is not None and entry["name"] != starter:
        continue
      starter = None
      
      crosslinks, tags, rating = parse_article(entry["name"])
      write_entry = {
        "name" : entry["name"],
        "authors" : entry["authors"],
        "crosslinks" : crosslinks,
        "tags" : tags,
        "rating" : rating
      }
      writer.write(write_entry)