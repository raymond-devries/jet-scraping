import scrapy
from scrapy.crawler import CrawlerProcess


class JetsSpider(scrapy.Spider):
    name = "jet-spider"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_fighter_aircraft"]

    def parse(self, response, **kwargs):
        table = response.xpath('//*[@id="mw-content-text"]/div[1]/table')
        rows = table.xpath("//tr")
        for row in rows[1:]:
            table_values = row.css("td::text").getall()
            if len(table_values) == 0:
                continue
            yield {
                "link": row.css("a::attr(href)").get(),
                "name": row.css("a::text").get(),
                "country": table_values[0],
                "year": table_values[1]
            }


if __name__ == '__main__':
    process = CrawlerProcess(settings={
        "FEEDS": {
            "planes.csv": {"format": "csv"}
        },
    })
    process.crawl(JetsSpider)
    process.start()
