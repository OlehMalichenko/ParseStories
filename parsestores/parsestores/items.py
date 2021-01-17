# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParsestoresItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    category_1 = scrapy.Field()
    category_2 = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    price_iso_code = scrapy.Field()
    brand = scrapy.Field()
    gender = scrapy.Field()
    site_name = scrapy.Field()
