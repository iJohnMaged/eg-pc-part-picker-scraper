# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ComponentItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
