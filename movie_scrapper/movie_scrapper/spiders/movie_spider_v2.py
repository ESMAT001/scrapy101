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
        fl = open('index.html', 'a',encoding="utf-8")
        fl.write(response.css("html").extract()[0])
        fl.close()
        movies_url = response.css("div.title > h2 > a::attr(href)").extract()
        movies_title= response.css("div.title > h2 > a::text").extract()
        for i , value in enumerate(movies_title):
            if 'سریال' in value:
                movies_url.pop(i)
        
        yield  {
            'url':movies_url
        }

        yield from response.follow_all(
            movies_url, callback=self.movie_scrapper)

        # # self.last_page = self.last_page or int(last_page[3])

        next_page = 'https://www.film2movie.asia/category/download-film/page/' + \
            str(self.page_num) + '/'

        fl = open('page.txt', 'a')
        fl.write(str(self.page_num-1)+'\n')
        fl.close()

        if self.page_num <= 1:
            self.page_num += 1
            yield response.follow(next_page, callback=self.parse)

    def movie_scrapper(self, response):
        items = MovieScrapperItem()

        movie_container = response.css("div.content > div").getall()

        all_p = response.css("div.content > *").extract()

        download_links = self.extract_data(all_p,response)

        movie_name = Selector(text=movie_container[0]).css("p > span > span > strong").extract()[0]
        movie_name = Selector(text=movie_name).css("strong::text").extract()[0]
        

        items['movie_name'] = movie_name
        items['movie_download_links'] = download_links

        yield items

    def extract_data(self, all_p,response):
        def get_download_links(new_all_p):
            if 'نسخه دوبله فارسی (دو زبانه)' in new_all_p[0]:
                new_all_p.pop(0)
                new_all_p.pop(0)

            download_links = list()
            start = 0
            end = 0
            for i, p in enumerate(new_all_p):

                if 'نسخه زیرنویس چسبیده فارسی' in p :
                    return None


                if 'دانلود با کیفیت' in p:
                    quality_and_size = p
                    # quality_and_size = quality_and_size[0] if len(quality_and_size) > 0 else None
                    download_link=Selector(text=new_all_p[i+1]).css("p > strong > a::attr(href)").extract()
                    if len(download_link) == 0:
                        download_link=Selector(text=new_all_p[i+1]).css("p > a::attr(href)").extract()
                    download_link = download_link[0] if len(download_link) > 0 else None

                    download_links.append({
                        'quality_and_size': quality_and_size,
                        'download_link': download_link
                    })

            return download_links


        h3_index=None
        hr_index=0

        for i , value in enumerate(all_p):
            if "<h3" in value:
                h3_index=i+1
            elif "<hr>" in value:
                hr_index=i       

        all_p = all_p[ h3_index : hr_index ]

        should_change = False # if original language and persian language exist
     
       
        for i, value in enumerate(all_p):
            if 'نسخه زبان اصلی' in value:
                should_change = True
                all_p = [
                    all_p[0:i],
                    all_p[i+1:]
                ]
                break
        
       

        if not(should_change):
            return {'original_lang': get_download_links(all_p)}
        else:
           
            all_p[1].pop(-1)
           
            return {
                'persian_lang': get_download_links(all_p[0]),
                'original_lang': get_download_links(all_p[1])
            }
