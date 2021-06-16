import scrapy
from scrapy.selector import Selector
import json
from ..items import MovieScrapperItem
from urllib.parse import unquote as urlDecoder
import re


class MovieScrapper(scrapy.Spider):
    name = 'movies_v2'
    page_num = 2
    last_page = None
    start_urls = [
        'https://www.film2movie.asia/category/download-film/page/18/'
    ]

    def parse(self, response):
        movies_url = response.css("div.title > h2 > a::attr(href)").extract()
        # movies_title = response.css("div.title > h2 > a::text").extract()

        if len(movies_url) > 0:
            for i, value in enumerate(movies_url):
                value = urlDecoder(str(value))
                if re.search(r'سریال',value) is not None or re.search(r'[a-zA-Z]',value) is None:
                    print(value)
                    fl = open('series.txt', 'a',encoding='utf-8')
                    fl.write(value + '\n')
                    fl.close()
                    movies_url.pop(i)

            yield from response.follow_all(
                movies_url, callback=self.movie_scrapper)

        next_page = 'https://www.film2movie.asia/category/download-film/page/' + \
                    str(self.page_num) + '/'

        fl = open('page.txt', 'a')
        fl.write(str(self.page_num - 1) + '\n')
        fl.close()

        if self.page_num <= 1395:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def movie_scrapper(self, response):

        try:
            items = MovieScrapperItem()
            movie_container = response.css("div.content > *").extract()

            all_p = response.css("div.content > *").extract()

            download_links = self.extract_data(all_p, response)
            movie_name = Selector(text=movie_container[0]).css("p > span > span > strong").extract()
            movie_name = Selector(text=movie_name[0]).css("strong::text").extract()[0]

            items['movie_name'] = movie_name
            items['movie_download_links'] = download_links
            # fl = open('data.json', 'a')
            # fl.write(json.dumps({
            #     'movie_name': movie_name,
            #     'movie_download_links': download_links
            # }) + ",")
            # fl.close()
            yield items
        except Exception as e:
            fl = open('page.txt', 'a')
            fl.write('erro:' + str(e) + ' -- retrying! ' + response.url + '\n')
            fl.close()
            return scrapy.Request(response.url,
                                  callback=self.movie_scrapper)

    def extract_data(self, all_p, response):
        def get_download_links(new_all_p):

            download_links = list()
            start = 0
            end = 0
            for i, p in enumerate(new_all_p):

                if 'نسخه زیرنویس چسبیده فارسی' in p:
                    return None

                if 'دانلود با کیفیت' in p:
                    quality_and_size = p
                    # quality_and_size = quality_and_size[0] if len(quality_and_size) > 0 else None
                    download_link = Selector(text=new_all_p[i + 1]).css("p > strong > a::attr(href)").extract()
                    if len(download_link) == 0:
                        download_link = Selector(text=new_all_p[i + 1]).css("p > a::attr(href)").extract()
                    download_link = download_link[0] if len(download_link) > 0 else None

                    download_links.append({
                        'quality_and_size': quality_and_size,
                        'download_link': download_link
                    })

            return download_links

        h3_index = None
        hr_index = 0

        for i, value in enumerate(all_p):
            if "<h3" in value:
                h3_index = i + 1 if h3_index is None else h3_index
            elif "<hr>" in value:
                hr_index = i

        all_p = all_p[h3_index: hr_index]

        should_change = False  # if original language and persian language exist

        for i, value in enumerate(all_p):
            if 'نسخه زبان اصلی' in value:
                should_change = True
                all_p = [
                    all_p[0:i],
                    all_p[i + 1:]
                ]
                break

        if not (should_change):
            return {'original_lang': get_download_links(all_p)}
        else:
            if 'نسخه دوبله فارسی (دو زبانه)' in all_p[0][0]:
                return {
                    'dual_lang': get_download_links(all_p[0]),
                    'original_lang': get_download_links(all_p[1])
                }
            else:
                return {
                    'original_lang': get_download_links(all_p[1])
                }
