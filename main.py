import datetime

from constants import DATA_RAW_PATH, DATA_TRANSFORMED_PATH

from article_parser import parse_and_save_articles, parse_article
from common import read_data, save_data
from data_transforms import filter_by_tags, filter_inner_links, fill_in_gaps
from tag_search_parser import TagSearchParser


def get_article_list(tag_sets: list[list[str]], filename: str):
    tag_search = TagSearchParser()
    tag_search.save_list_of_articles(tag_sets, filename)

def parse_articles(filename: str, starter: str = None):
    parse_and_save_articles(filename, starter)

def apply_transforms(filename: str):
    entries = read_data(DATA_RAW_PATH + filename)
    entries = filter_by_tags(entries, exclude=["hub"])
    entries = filter_inner_links(entries)
    save_data(entries, DATA_TRANSFORMED_PATH + filename)

def run_pipeline(tag_sets: list[list[str]], filename: str = None, starter: str = None):
    if filename is None:
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jsonl"
    get_article_list(tag_sets, filename)
    parse_articles(filename, starter)
    apply_transforms(filename)