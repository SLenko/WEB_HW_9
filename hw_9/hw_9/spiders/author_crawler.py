import logging

import scrapy.spiders
from scrapy.crawler import CrawlerProcess
import scrapy.linkextractors


class RegularSpiderItem(scrapy.Item):
    author = scrapy.Field()
    quote = scrapy.Field()


class AuthorsCrawler(scrapy.spiders.CrawlSpider):
    name = "author_crawler"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    rules = (
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(
                allow=("page"), deny=("tag")
            ),
            callback='parse_authors',
            follow=True
        ),
    )

    def parse_authors(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            author = quote.xpath(".//span/small/text()").get()
            quote_text = quote.xpath(".//span[@class='text']/text()").get()

            logging.info(f"Author: {author}, Quote: {quote_text}")

            item = RegularSpiderItem(author=author, quote=quote_text)

            yield item
if  __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    process = CrawlerProcess()
    process.crawl(AuthorsCrawler)
    process.start()
