# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CategoryItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    count = scrapy.Field()

class ListItem(scrapy.Item):
    title = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    homepage = scrapy.Field()
    rating = scrapy.Field()
    city = scrapy.Field()
    industry = scrapy.Field()
    html5 = scrapy.Field()
    homepage_available = scrapy.Field()
