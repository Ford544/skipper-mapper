#extracting crosslinks from an article

import requests
from bs4 import BeautifulSoup
from lxml import etree

from constants import CANONICAL_BASE_URL, ALTERNATE_BASE_URLS


#function takes in article name (the last part of the url, e. g. 'scp-2311' or 'taboo'), and optionally an offset value
def get_crosslinks(article_name : str, offset : str = 0) -> list[str]:
  #build the url
  
  url = CANONICAL_BASE_URL + article_name
  if offset != 0:
    url += f"/offset/{offset}"
  #fetch the page
  r = requests.get(url)
  s = BeautifulSoup(r.content, "html.parser")
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
    internal = False
    #filter out the links that go outside the wiki
    #internal links can be relative (e. g. '/taboo') or absolute (e.g. 'https://scp-wiki.wikidot.com/scp-8190'))
    for base in ALTERNATE_BASE_URLS:
      if target.startswith(base):
       target = target[len(base):]
       internal = True
       break
    if not internal:
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
        if int(found_offset) > int(offset):
          print(f"entering into offset {found_offset}")
          result.extend(get_crosslinks(article_name, found_offset))
    except:
      pass

    #before adding a link to an offset page, we remove the offset
    #that is, we want to treat a crosslink to scp-6500/offset/16 as simply a crosslink to scp-6500
    if "/offset/" in target:
      target = target[:target.find("/offset/")]
    #do not include self-links
    if target == article_name:
      continue
    result.append(target)
  #at the end, we remove the duplicates
  return list(set(result))

print(get_crosslinks("nagiros-proposal"))