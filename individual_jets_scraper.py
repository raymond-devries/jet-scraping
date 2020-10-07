import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup, NavigableString
import re


def get_all_children(parent_item: BeautifulSoup):
    items = parent_item.find_all("li")
    label = parent_item.text.split(":")[0]
    data = []

    if isinstance((extra_string := parent_item.contents[1]), NavigableString):
        if (stripped_extra_string := extra_string.strip()) != "":
            data.append(stripped_extra_string)

    for item in items:
        if item.find_all("li"):
            data.append(get_all_children(item))
        elif item.parent.parent == parent_item:
            data.append(item.text.strip())

    return {label: data}


class IndividualJetSpider(scrapy.Spider):
    name = "individual-jet-spider"
    start_urls = ["https://en.wikipedia.org/wiki/Mikoyan-Gurevich_MiG-21"]

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        heading = soup.find("span", id=re.compile("^Specifications"))
        current_item = heading.find_next("li")
        specifications = {}
        while current_item.find_previous("h2") == heading.parent:
            if (current_item.find("b")) is not None:
                text = current_item.text.split(":")
                label = text[0].strip()

                if label in specifications:
                    label += "2"

                if current_item.find_all("li"):
                    specifications.update(get_all_children(current_item))
                else:
                    specifications[label] = text[1].strip()
            current_item = current_item.find_next("li")
        yield specifications


if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            "all_planes.json": {"format": "json"}
        },
    })
    process.crawl(IndividualJetSpider)
    process.start()
