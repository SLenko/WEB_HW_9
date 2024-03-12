import json
from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from itemadapter import ItemAdapter
import logging

from src.DB.connect import connect_mongoDb
from src.DB.seed_to_db import seeds


json_dest = Path(__file__).resolve().parent.joinpath("src").joinpath("data")


class QuoteItem(Item):
    keywords = Field()
    author = Field()
    quote = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class QuotesAuthorPipeline:
    authors = []
    quotes = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if "fullname" in adapter.keys():
            self.authors.append(
                {
                    "fullname": adapter.get("fullname"),
                    "born_date": adapter.get("born_date"),
                    "born_location": adapter.get("born_location"),
                    "description": adapter.get("description"),
                }
            )
            logging.debug(f"Added author: {adapter.get('fullname')}")
        elif "quote" in adapter.keys():
            self.quotes.append(
                {
                    "tags": adapter.get("keywords"),
                    "author": adapter.get("author"),
                    "quote": adapter.get("quote"),
                }
            )
            logging.debug(f"Added quote by {adapter.get('author')}")
        return item

    def write_json_file(self, data: list[dict], json_path: Path):
        with json_path.open("w", encoding="UTF-8") as fp:
            json.dump(data, fp, ensure_ascii=False)

    def write_json_files(self):
        quotes_path = json_dest.joinpath("quotes.json")
        authors_path = json_dest.joinpath("authors.json")
        self.write_json_file(self.authors, authors_path)
        self.write_json_file(self.quotes, quotes_path)

    def write_to_databse(self):
        if connect_mongoDb():
            seeds()

    def close_spider(self, spider):
        print(
            f"> Write to json files: authors ({len(self.authors)}), quotes ({len(self.quotes)})"
        )
        self.write_json_files()
        print("> Write to database")
        self.write_to_databse()


class QuotesAuthorSpider(scrapy.Spider):
    name = "quotes_authors"
    custom_settings = {"ITEM_PIPELINES": {QuotesAuthorPipeline: 300}}
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            keywords = [
                k.strip() for k in quote.xpath("div[@class='tags']/a/text()").getall()
            ]
            author = quote.xpath("span/small/text()").get().strip()
            author_link = quote.xpath("span/a/@href").get()
            quote = quote.xpath("span[@class='text']/text()").get().strip()
            yield QuoteItem(keywords=keywords, author=author, quote=quote)
            yield response.follow(
                url=self.start_urls[0] + author_link, callback=self.nested_parse_author
            )
            
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)
            # yield scrapy.Request(url=response.urljoin(next_link))

    def nested_parse_author(self, response):
        author = response.xpath("/html//div[@class='author-details']")
        fullname = author.xpath('h3[@class="author-title"]/text()').get().strip()
        born_date = (
            author.xpath('p/span[@class="author-born-date"]/text()').get().strip()
        )
        born_location = (
            author.xpath('p/span[@class="author-born-location"]/text()').get().strip()
        )
        description = (
            author.xpath('div[@class="author-description"]/text()').get().strip()
        )
        yield AuthorItem(
            fullname=fullname,
            born_date=born_date,
            born_location=born_location,
            description=description,
        )


if __name__ == "__main__":
    process = CrawlerProcess()
    logger_pymongo = logging.getLogger("pymongo")
    logger_pymongo.setLevel(logging.ERROR)
    # run spider: 
    logger_scrapy = logging.getLogger("scrapy")
    logger_scrapy.setLevel(logging.ERROR)
    logger_urllib = logging.getLogger("urllib3")
    logger_urllib.setLevel(logging.ERROR)
    process.crawl(QuotesAuthorSpider)
    logging.basicConfig(level=logging.ERROR)
    process.start()
