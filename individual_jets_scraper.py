import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup, NavigableString
import re
from urllib.parse import urljoin
import pandas as pd


def get_all_children(parent_item: BeautifulSoup):
    items = parent_item.find_all("li")
    label = parent_item.text.split(":")[0]
    data = []

    try:
        if isinstance((extra_string := parent_item.contents[1]), NavigableString):
            if re.match(r"[\w]", (stripped_extra_string := extra_string.strip())):
                data.append(stripped_extra_string)
    except IndexError:
        pass

    for item in items:
        if item.find_all("li"):
            data.append(get_all_children(item))
        elif item.parent.parent == parent_item:
            data.append(item.text.strip())

    return {label: data}


class IndividualJetSpider(scrapy.Spider):
    name = "individual-jet-spider"
    start_urls = list(pd.read_json("jets.json")["url"])
    # start_urls = ["https://en.wikipedia.org/wiki/Wibault_9"]

    def parse(self, response, **kwargs):
        base_url = "https://www.wikipedia.org/"
        soup = BeautifulSoup(response.text, "lxml")

        try:
            image_url = urljoin(base_url, soup.find("a", {"class": "image"})["href"])
        except:
            image_url = ""

        specifications = {"url": response.url, "image": image_url}
        heading = soup.find("span", id=re.compile("specifications", re.IGNORECASE))
        current_item = heading.find_next("li")
        while current_item.find_previous("h2") == heading.parent:
            if (current_item.find("b")) is not None:
                text = current_item.text.split(":")
                label = text[0].strip()

                if label in specifications:
                    label += "2"

                if current_item.find_all("li"):
                    specifications.update(get_all_children(current_item))
                else:
                    try:
                        specifications[label] = text[1].strip()
                    except:
                        pass
            current_item = current_item.find_next("li")
        yield specifications


if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            "jet_details.json": {"format": "json"}
        },
    })
    process.crawl(IndividualJetSpider)
    process.start()
