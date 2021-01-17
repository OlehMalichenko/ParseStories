import scrapy
from scrapy_splash import SplashRequest


class AaaSplashSpider(scrapy.Spider):
    name = 'aaa_splash'
    allowed_domains = ['aaa.com']

    def start_requests(self):
        yield SplashRequest(url='https://www.revolve.com/clothing/br/3699fc/?navsrc=subclothing', endpoint='render.html')

    def parse(self, response):
        print(response.url)
