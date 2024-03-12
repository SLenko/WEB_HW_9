import scrapy

from regular_spider.items import RegularSpiderItem

class AuthorsSpider(scrapy.Spider):
    name = "authors"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            item = RegularSpiderItem(
                author=quote.xpath("span/small/text()").extract()[0],
                quote=quote.xpath("span[@class='text']/text()").get()
            )

            yield item

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)
