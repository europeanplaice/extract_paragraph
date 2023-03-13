import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# define the URL of the page you want to scrape
start_url = ""
domain = urlparse(start_url).netloc

# create a set to store all the visited URLs
visited_urls = set()
visited_text = set()


def get_header_hierarchy(tag, header_hierarchy: list[str]=[]) -> list[str]:
    import pdb; pdb.set_trace()
    if tag is None or tag.name == 'html':
        # base case: we've reached the top of the hierarchy
        header_hierarchy.reverse()
        return header_hierarchy
    elif tag.name.startswith('h') and tag.name[1:].isdigit():
        # we've found a header tag, so add its text to the hierarchy list
        # import pdb; pdb.set_trace()
        header_hierarchy.append(f"[{tag.name}]: {tag.text}")
    # recursively process the parent of the current tag
    return get_header_hierarchy(tag.parent, header_hierarchy)


def explore_links(url, f):
    # send a GET request to the URL and get the response
    time.sleep(1)
    response = requests.get(url)

    # create a BeautifulSoup object from the response text
    soup = BeautifulSoup(response.text, "html.parser")

    # find all the links on the page
    links = soup.find_all("a")

    # loop through each link and extract the first paragraph from the page
    for link in links:
        # get the URL of the link
        link_url = urljoin(url, link.get("href"))
        if urlparse(link_url).netloc != domain:
            continue

        if link_url is not None and link_url not in visited_urls:
            # add the link URL to the visited URLs set
            visited_urls.add(link_url)

            # send a GET request to the link URL and get the response
            link_response = requests.get(link_url)

            # create a BeautifulSoup object from the link response text
            link_soup = BeautifulSoup(link_response.content, "html.parser")

            # find the first paragraph on the page
            print("Link URL:", link_url)
            paragraphs = link_soup.find_all('p')
            for paragraph in paragraphs:
                paragraph_text: str = paragraph.text.replace("\n", "").strip()
                # print(paragraph_text)
                if paragraph_text == "":
                    continue
                try:
                    res = detect(paragraph_text)
                except LangDetectException:
                    continue
                if res != 'ja':
                    continue
                hierarchy = get_header_hierarchy(paragraph)
                hierarchy.append(paragraph_text)
                if len(hierarchy) == 1:
                    continue
                else:
                    # import pdb; pdb.set_trace()
                    hierarchy_joined: str = " > ".join(hierarchy)
                if not paragraph_text in visited_text:
                    visited_text.add(paragraph_text)
                    print(hierarchy_joined)
                    f.write(hierarchy_joined)
                    f.write("\n")
                # print(paragraph_text)

            # print the URL of the link and the first paragraph of the page

            # recursively explore all links on the page
            explore_links(link_url, f)

# start exploring links from the start URL
with open("body.txt", "w", encoding="utf-8") as f:
    explore_links(start_url, f)
