import scrapy


class TestSpider(scrapy.Spider):
    name = 'quotes'
    start_url = [
        "http://quotes.toscrape.com/"
    ]

    def parse(self, response):
        title = response.css("title").extract()
        yield {'title': title}
