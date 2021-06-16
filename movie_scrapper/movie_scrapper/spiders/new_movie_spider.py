import scrapy
from scrapy.selector import Selector
import json
from ..items import MovieScrapperItem


class MovieScrapper(scrapy.Spider):
    name = 'movies2'
    page_num = 2
    last_page = None
    start_urls = [
        'https://www.film2movie.asia/page/1/'
    ]

    def parse(self, response):
        movies_url = response.css("article.box > div.titlehaver > div.title > h2 > a::attr(href)").extract()

        fl=open('index.html','w',encoding='utf-8')
        fl.write(str(response.css("html").extract()[0]))
        fl.close()
        yield {
            'm': movies_url
        }
        yield from response.follow_all(
            movies_url, callback=self.movie_scrapper)



        next_page = 'https://www.film2movie.asia/page/' + \
            str(self.page_num) + '/'

        if self.page_num <= 1:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def movie_scrapper(self, response):
        items = MovieScrapperItem()

        movie_name = response.css(".titlehaver > .title a::text").extract()[0]
        movie_name = re.split('[^A-Za-z ]', movie_name)
        movie_name = "".join(movie_name)
        movie_name = movie_name.strip()

        download_links = response.css(
            ".content > p a::attr(href)").extract()[1:]

        items['movie_name'] = movie_name
        items['movie_download_links'] = download_links

        if movie_name:
            yield items
