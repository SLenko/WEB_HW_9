
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field

class QuoteItem(Item):
    quote = Field()
    author = Field()
    tags = Field()

class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description =Field()


class QuotesSpyder(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response, **kwargs):
        for q in response.xpath("//div[@class='quote']"):
            quote = q.xpath(".//span[@class='text']/text()").get().strip()
            author = q.xpath(".//small[@class='author']/text()").get().strip()
            tags = q.xpath(".//div[@class='tags']/a/text()").extract()
            print(quote, author, tags)
            yield QuoteItem(quote=quote, author=author, tags=tags)
            yield response.follow(
                q.xpath(".//span/a/@href").get(), callback=self.parse_author
            )
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(response.urljoin(next_link))

    def parse_author(self, response):
        content = response.xpath("//div[@class='author-details']")
        fullname = content.xpath(".//h3[@class='author-title']/text()").get().strip()
        born_date = (
            content.xpath(".//span[@class='author-born-date']/text()").get().strip()
        )
        born_location = (
            content.xpath(".//span[@class='author-born-location']/text()").get().strip()
        )
        description = (
            content.xpath(".//div[@class='author-description']/text()").get().strip()
        )
        yield AuthorItem(
            fullname=fullname,
            born_date=born_date,
            born_location=born_location,
            description=description,
        )


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpyder)
    process.start()
