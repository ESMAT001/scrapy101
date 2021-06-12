# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_name = scrapy.Field()
    movie_download_links = scrapy.Field()


class SeriesScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    series_name = scrapy.Field()
    series_download_links = scrapy.Field()
