from article_parser import parse_and_save_articles, parse_article
from tag_search_parser import TagSearchParser

#tag_search = TagSearchParser()
#tag_search.save_list_of_articles([["scp"], ["supplement"], ["tale"], ["goi-format"]], "articles.json")

#parse_and_save_articles("articles.json", "data.jsonl", starter="scp-4286")

crosslinks, _, _  =parse_article("grant-request-for-the-construction-of-an-interstellar-scienc")
print(crosslinks)