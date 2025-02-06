from constants import ALTERNATE_BASE_URLS

def extract_article_name(url : str):
    name = None
    for base in ALTERNATE_BASE_URLS:
        if url.startswith(base):
            name = url[len(base):]
            break
    if name is None: raise ValueError(f"The url {url} does not conform to a known format.")
    return name