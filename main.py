from article_parser import parse_and_save_articles, parse_article
from tag_search_parser import TagSearchParser

tag_search = TagSearchParser()
tag_search.save_list_of_articles([["scp"], ["supplement"], ["tale"], ["goi-format"]], "articles_test.json")

parse_and_save_articles("articles_test.json", "data_test.jsonl")

#crosslinks, _, _  =parse_article("rounderhouse-proposal")