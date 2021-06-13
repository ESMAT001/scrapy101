import scrapy
from scrapy.selector import Selector
import json
from ..items import MovieScrapperItem


class MovieScrapper(scrapy.Spider):
    name = 'movies'
    page_num = 2
    last_page = None
    start_urls = [
        'https://www.film2media.ws/category/film/page/1/'
    ]

    def parse(self, response):
        movies_url = response.css("#post-title h2 a::attr(href)").extract()
        # last_page = response.css("div.textwpnumb span::text").extract()[
        #     0].split(" ")

        yield from response.follow_all(
            movies_url, callback=self.movie_scrapper)

        # self.last_page = self.last_page or int(last_page[3])

        next_page = 'https://www.film2media.ws/category/film/page/' + \
            str(self.page_num) + '/'

        fl = open('page.txt', 'a')
        fl.write('\n'+str(self.page_num)+'\n')
        fl.close()


        if self.page_num <= 371:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def movie_scrapper(self, response):
        items = MovieScrapperItem()

        movie_container = response.css("div.txtbbb div.txtbbb div").getall()
        # all_div = Selector(text=movie_container).css("divdiv.txtbbb div").getall()
        movie_name = Selector(text=movie_container[0]).css(
            "strong::text").extract()[0]
        download_links = response.css("div.txtbbb > p a::attr(href)").extract()

        items['movie_name'] = movie_name
        items['movie_download_links'] = download_links

        yield items
