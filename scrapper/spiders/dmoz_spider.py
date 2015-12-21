import scrapy
import logging
import requests
import re
import base64
from scrapy.utils.log import configure_logging
from scrapy.http import Request

from scrapper.items import CategoryItem,ListItem


class DmozSpider(scrapy.Spider):
    name = "germany"
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        filemode = 'a',
        format='%(asctime)s - %(name)s %(levelname)s: %(message)s',
        level=logging.DEBUG,
        name=__name__
    )
    logging.getLogger('scrapy').propagate = False
    allowed_domains = ["branchenbuch.meinestadt.de"]
    start_urls = [
        "http://branchenbuch.meinestadt.de/deutschland/suche?words=doktor",
        "http://branchenbuch.meinestadt.de/deutschland/suche?words=sex"
    ]

    #Start from category search
    # def parse(self, response):
    #     self.logger.info("categories = " + str(len(response.css('div[class=ms-categories-list-item]'))))
    #     for sel in response.css('div[class=ms-categories-list-item]'):
    #         item = CategoryItem()
    #         item['title'] = sel.xpath('a/text()').extract()[0]
    #         item['link'] = response.urljoin(sel.xpath('a/@href').extract()[0])
    #         item['count'] = sel.xpath('span/text()').extract()[0]
    #         yield Request(item['link'], callback=self.parse_page_contents)


    # def parse_page_contents(self,response):
    def parse(self, response):
        # self.logger.info("Parse sub page")
        self.logger.info("Items on page= " + str(len(response.css('.ms-pre-result-item'))) + " " + str(response))
        for sel in response.css('.ms-pre-result-item'):
            try:
                url = response.urljoin(sel.css('.ms-pre-result-item-title').xpath('@href').extract()[0].strip())
                self.logger.info(url)
                yield Request(url, callback=self.parse_listing_page)
            except Exception as e:
                self.logger.error("Error occured " + e.message)
        next_page = response.css("a.ms-pagination-next")
        if next_page:
            self.logger.info("Next page found")
            yield Request(response.urljoin(next_page.xpath('@href').extract()[0]), callback=self.parse)
        else:
            self.logger.info("next page not found , terminate here")




    def parse_listing_page(self,response):
        self.logger.info("Inside list item")
        item = ListItem()
        try:
            item['title'] = response.css('.ms-mpd-header-left').xpath('h1/span/text()').extract()[0]
            item['phone'] = response.xpath('//*[contains(@id,"ms-poi-phone-id")]/span/text()').extract()[0]
            addressArray = response.css('.ms-mpd-basicmodule-list').xpath('ul/li/span')[1].xpath('span/text()').extract()
            item['address'] = ', '.join(addressArray)
            item['city'] = addressArray[-1]
            item['homepage'] = response.xpath('//*[contains(@id,"ms-poi-homepage-id")]/a/@href').extract()[0]
            item['rating'] = len(response.css('.ms-mpd-call-to-action').css('.ms-star-rating').xpath('span').css('.ms-star-full'))*1 + len(response.css('ms-mpd-call-to-action').css('.ms-star-rating').xpath('span').css('.ms-star-half'))*0.5
            item['industry'] = ', '.join(response.css('.last-list-node').xpath('li/a/span/text()').extract())
            try:
                homepage_response = requests.get(item['homepage'])
                if(homepage_response.content.lower().find('<!doctype html>') > -1):
                    item['html5'] = 1
                else:
                    item['html5'] = 0
                item['homepage_available'] = 1
            except Exception as e:
                item['html5'] = 0
                item['homepage_available'] = 0
                self.logger.error("Error occured " + e.message)
            encoded_email = re.search('window.atob\(\"(.*)\"\)\s+',response.xpath('//*[contains(@id,"ms-poi-mail-id")]/script').extract()[0]).group(1)
            item['email'] = base64.b64decode(encoded_email)
        except Exception as e:
            self.logger.error("Error occured " + e.message)
        self.logger.info("item = " + str(item))
        yield item