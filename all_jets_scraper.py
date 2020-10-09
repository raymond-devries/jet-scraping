import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class JetsSpider(scrapy.Spider):
    name = "jet-spider"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_fighter_aircraft"]

    def parse(self, response, **kwargs):
        base_url = "https://www.wikipedia.org/"
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table")
        rows = table.find_all("tr")
        for row in rows[1:]:
            try:
                yield {
                    "url": urljoin(base_url, row.contents[1].find("a")["href"].strip()),
                    "name": row.contents[1].find("a").text.strip(),
                    "country": row.contents[3].text.strip(),
                    "class": row.contents[5].text.strip(),
                    "year": row.contents[7].text.strip(),
                    "status": row.contents[9].text.strip(),
                    "number created": row.contents[11].text.strip(),
                    "notes": row.contents[13].text.strip()
                }
            except:
                pass


if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            "jets.json": {"format": "json"}
        },
    })
    process.crawl(JetsSpider)
    process.start()
