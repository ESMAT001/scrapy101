import scrapy
from scrapy.selector import Selector
import json
from ..items import SeriesScrapperItem
import re


class SeriesScrapper(scrapy.Spider):
    name = 'series'
    page_num = 2
    last_page = None
    start_urls = [
        'https://www.film2movie.asia/category/miscellaneous/series/page/1/'
    ]

    def parse(self, response):
        series_url = response.css(
            "article.box > div.title h2 a::attr(href)").extract()
        # last_page = response.css(
        #     "#wbh-pagenumber li:last-child > a::text").extract()
        # if last_page:
        #     last_page = last_page[0]

        yield from response.follow_all(
            series_url, callback=self.series_scrapper)

        # self.last_page = self.last_page or int(last_page)

        next_page = 'https://www.film2movie.asia/category/miscellaneous/series/page/' + \
            str(self.page_num) + '/'
        fl = open('page.txt', 'a')
        fl.write('\n'+str(self.page_num)+'\n')
        fl.close()
        if self.page_num <= 179:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def series_scrapper(self, response):
        items = SeriesScrapperItem()

        # series_container = response.css("div.txtbbb div.txtbbb div").getall()
        # all_div = Selector(text=movie_container).css("divdiv.txtbbb div").getall()
        series_name = response.css(".titlehaver > .title a::text").extract()[0]
        series_name = re.split('[^A-Za-z ]', series_name)
        series_name = "".join(series_name)
        series_name = series_name.strip()

        download_links = response.css(
            ".content > p a::attr(href)").extract()[1:]

        items['series_name'] = series_name
        items['series_download_links'] = download_links

        if series_name:
            yield items
