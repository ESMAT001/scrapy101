import scrapy
from scrapy.selector import Selector
import json
from ..items import MovieScrapperItem


class MovieScrapper(scrapy.Spider):
    name = 'movies_v_2'
    page_num = 2
    last_page = None
    start_urls = [
        'https://www.film2movie.asia/category/download-film/page/1/'
    ]

    def parse(self, response):
        
        movies_url = response.css("div.title > h2 > a::attr(href)").extract()
        movies_title= response.css("div.title > h2 > a::text").extract()
        for i , value in enumerate(movies_title):
            if 'سریال' in value:
                movies_url.pop(i)
        # last_page = response.css("div.textwpnumb span::text").extract()[
        #     0].split(" ")

        # yield  {
        #     'url':movies_url
        # }
        yield from response.follow_all(
            movies_url, callback=self.movie_scrapper)

        # # self.last_page = self.last_page or int(last_page[3])

        next_page = 'https://www.film2movie.asia/category/download-film/page/' + \
            str(self.page_num) + '/'

        fl = open('page.txt', 'a')
        fl.write(str(self.page_num)+'\n')
        fl.close()

        if self.page_num <= 1:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def movie_scrapper(self, response):
        items = MovieScrapperItem()

        movie_container = response.css("div.content > div").getall()

        # all_p = response.css("div#content > div.txtbbb > *").extract()

        # download_links = self.extract_data(all_p,response)

        movie_name = Selector(text=movie_container[0]).css("p > span > span > strong").extract()[0]
        movie_name = Selector(text=movie_name).css("strong::text")[0]
        # download_links = response.css("div.txtbbb > p a::attr(href)").extract()

        # items['movie_name'] = movie_name
        # items['movie_download_links'] = download_links

        yield {
            'name':movie_name
        }

    def extract_data(self, all_p,response):
        def get_download_links(new_all_p):
            download_links = list()
            start = 0
            end = 0
            for i, p in enumerate(new_all_p):
                if '– – – – – – – – – – – – – – – – – – – – – – –' in p:
                    end = i
                    new_data = new_all_p[start:end]
                    start = end + 1
                    quality_and_size = Selector(text=new_data[0]).css("p").extract()


                    quality_and_size = quality_and_size[0] if len(quality_and_size) > 0 else None

                    download_link=Selector(text=new_data[1]).css("p > a::attr(href)").extract()
                    download_link = download_link[0] if len(download_link) > 0 else None

                    download_links.append({
                        'quality_and_size': quality_and_size,
                        'download_link': download_link
                    })

                    if (i + 3) == (len(new_all_p)-1):
                        new_data = new_all_p[i+1:]
                        quality_and_size = Selector(text=new_data[0]).css("p").extract()

                        quality_and_size = quality_and_size[0] if len(quality_and_size) > 0 else None

                        download_link=Selector(text=new_data[1]).css("p > a::attr(href)").extract()
                        download_link = download_link[0] if len(download_link) > 0 else None

                        download_links.append({
                            'quality_and_size': quality_and_size,
                            'download_link': download_link
                        })

            return download_links

        for _ in range(3):
            all_p.pop(0)
        

        should_change = False # if original language and persian language exist
        should_change_second = False # if only persian version exist
        
        

        # to find نقد و برسی
        for i, value in enumerate(all_p):
            if 'نقد و بررسی' in value:
                all_p = all_p[0:i]
                break
        
        for i, value in enumerate(all_p):
            if 'نسخه زبان اصلی' in value:
                should_change = True
                all_p = [
                    all_p[0:i],
                    all_p[i:]
                ]
                break
        else:
            for value in all_p:
                if 'نسخه دوبله فارسی' in value:
                    should_change_second= True
        
       

        if not(should_change) and not(should_change_second):
           
            all_p.pop(-1)
            return {'original_lang': get_download_links(all_p)}
        elif not(should_change) and should_change_second:
           
            all_p.pop(0)
            all_p.pop(0)
            all_p.pop(-1)
            return {'persian_lang': get_download_links(all_p)}
        else:
           
            for i in range(2):
                all_p[i].pop(0)
                all_p[i].pop(0)
                all_p[i].pop(-1)
           
            return {
                'persian_lang': get_download_links(all_p[0]),
                'original_lang': get_download_links(all_p[1])
            }
