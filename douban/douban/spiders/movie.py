import scrapy
import re
from selenium import webdriver
from douban.items import ActorItem, ReviewItem


class MovieSpider(scrapy.Spider):
    name = "movie"
    # allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/"]
    movielink = ''
    page = 1
    link1 = ''

    def __init__(self):
        self.driver = webdriver.Edge()

    def parse(self, response):
       self.movielink = response.xpath('//*[@id="db-nav-movie"]/div[2]/div/ul/li[2]/a/@href').extract_first()
       yield scrapy.Request(url=self.movielink, callback=self.movieparse)

    def movieparse(self, response):
        self.link1 = response.xpath('//*[@id="app"]/div/div[2]/ul/li[1]/a/@href').extract_first()
        yield scrapy.Request(url=self.link1, callback=self.actorparse, dont_filter=True)
        yield scrapy.Request(url=self.link1, callback=self.reviewparse, dont_filter=True)

    def actorparse(self, response):
        litags = response.xpath('//*[@id="celebrities"]/ul/li')
        for li in litags[1:]:
            actor = li.xpath('./div/span[1]/a/text()').extract_first()
            role = li.xpath('./div/span[2]/text()').extract_first()

            item = ActorItem()
            item['actor'] = actor
            item['role'] = role

            actorlink = li.xpath('./div/span[1]/a/@href').extract_first()
            yield scrapy.Request(url=actorlink, callback=self.actordetail, meta={'item': item})

    def actordetail(self, response):
        item = response.meta['item']
        litags = response.xpath('//ul[@class="subject-property"]/li')
        actorkey = ['span1', 'span2']
        for litag in litags[:2]:
            name = litag.xpath('./span[1]/text()').extract_first()
            name = re.search(r'[\u4e00-\u9fa5]+', name).group()

            content = litag.xpath('./span[2]/text()').extract_first().strip()
            i = litags.index(litag)
            item[actorkey[i]] = name + ": " + content
        yield item

    def reviewparse(self, response):
        movieid = re.search(r'/(\d+)$', self.link1).group(1)
        urltail = response.xpath('//*[@id="reviews-wrapper"]/p/a/@href').extract_first()
        start = ["https://movie.douban.com/subject/"]
        self.url = start[0] + movieid + '/' + urltail
        yield scrapy.Request(url=self.url, callback=self.reviewdetail)

    def reviewdetail(self, response):
        divtags = response.xpath('//div[@class="review-list  "]/div')
        for div in divtags:
            idname = div.xpath('./div/header/a[2]/text()').extract_first()
            title = div.xpath('./div/div/h2/a/text()').extract_first()

            shortcontent = div.xpath('.//div[@class="short-content"]//text()')
            if (len(shortcontent)>3):
                shortcontent = shortcontent.extract()[2]
            else:
                shortcontent = shortcontent.extract_first()
            shortcontent = re.sub(r'\(',  '', shortcontent).strip()

            item = ReviewItem()
            item['idname'] = idname
            item['title'] = title
            item['shortcontent'] = shortcontent
            yield item

        newurltail = '?start=%d'
        if self.page < 5:
            newurl = self.url + format(newurltail%(20*self.page))
            self.page += 1
            yield scrapy.Request(url=newurl, callback=self.reviewdetail)

    def closed(self, spider):
        self.driver.quit()