from common import read_data, save_data
from article_parser import parse_article

#goes over entries in the input file, and saves to the output file only those that have at least
#one tag on the include list (if include is not None) and no tags on the exclude list (if exclude is not None) 
def filter_by_tags(entries : list[dict], include=None, exclude=None) -> list[dict]:
    result = []
    for entry in entries:
        if include is None or any([tag in entry["tags"] for tag in include]):
            if exclude is None or all([tag not in entry["tags"] for tag in exclude]):
                result.append(entry)
    return result

def filter_inner_links(entries : list[dict]) -> list[dict]:
    result = []
    domain = set()
    for entry in entries:
        domain.add(entry["name"])
    for entry in entries:
        entry["crosslinks"] = [link for link in entry["crosslinks"] if link in domain]
        result.append(entry)
    return result

def fill_in_gaps(entries : list[dict]) -> list[dict]:
    result = []
    for entry in entries:
        if entry["tags"] == []:
            crosslinks, tags, rating = parse_article(entry["name"])
            entry = {
                "name" : entry["name"],
                "authors" : entry["authors"],
                "crosslinks" : crosslinks,
                "tags" : tags,
                "rating" : rating
            }
        if entry["tags"]:
            result.append(entry)
    return result

entries = read_data("data.jsonl")
entries = fill_in_gaps(entries)
entries = filter_by_tags(entries, exclude=["hub"])
entries = filter_inner_links(entries)
save_data(entries, "data_transformed.jsonl")

import csv

def generate_cosmograph_csv(input_path : str, output_path : str):
    entries = read_data(input_path)
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',)
        writer.writerow(["source", "target"])
        for entry in entries:
            for crosslink in entry["crosslinks"]:
                writer.writerow([entry["name"], crosslink])

generate_cosmograph_csv("data_transformed.jsonl", "cosmodata.csv")