# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
"""
cd scrapy_seloger
scrapy crawl paris_sale -o paris_sale.csv urls=https://www.urltoscrape1.com;https://www.urltoscrape2.com
"""

class ParisSaleSpider(scrapy.Spider):
    name = 'paris_sale'
    allowed_domains = ['www.seloger.com']
    
    start_urls = ['http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750114&tri=initial&pxmax=305000']#['http://www.seloger.com/list.htm?org=advanced_search&idtt=2&idtypebien=1&cp=75&tri=initial&naturebien=1,2,4']

    def parse(self, response):

        # Total number of results
        response_num_results = response.xpath('//div[@class="title_nbresult"]/text()').extract_first()
        if response.url == 'http://www.seloger.com/erreur-temporaire/':
            return "\tGET returned {}:\n\tcrawling spotted by www.seloger.com".format(response.url)

        num_results_ls = re.findall("(\d*)", response_num_results)
        num_results = int("".join(num_results_ls))
        print("\tTotal number of results: {}".format(num_results))

        # Get listed properties
        properties = response.xpath(".//div[contains(@class, 'cartouche')]")

        for property in properties:

            ad_id = property.xpath('.//@id').extract_first()

            url = property.xpath('.//a[@class="c-pa-link"]/@href').extract_first()

            property_type = property.xpath('.//a[@class="c-pa-link"]/text()').extract_first().lower()

            price_raw = property.xpath('.//span[@class="c-pa-cprice"]/text()').extract_first()
            price = int("".join(re.findall("(\d*)", price_raw)))

            attrs_results = property.xpath('.//div[@class="c-pa-criterion"]/em/text()').extract()
            attrs_dict = {}
            for attr in attrs_results:
                res = re.search("(\d*)\s+(\w+)", attr)
                attrs_dict[res.group(2)] = res.group(1)

            results = {'id': ad_id, 'price': price, 'url': url, 'type': property_type}
            for k, v in attrs_dict.items():
                results[k] = v

            yield results # DEBUG
            #yield Request(link, callback=self.parse_page, meta=results)

        # Extract next page url if exists
        #next_url = response.xpath('//a[@class="pagination-next"]/@href').extract_first()
        #if next_url:
        #    yield Request(url=next_url, callback=self.parse)
        #else:
        #    print("\n\tLAST PAGE REACHED")

    def parse_page(self, response):
        url = response.meta.get('url')
        ad_id = response.meta.get('id')
        price = response.meta.get('price')
        property_type = response.meta.get('type')

        js = response.xpath('//script[@type="text/javascript"]/text()').extract()
        js_str = " ".join(js)
        lat = re.search("""'mapCoordonneesLatitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
        lng = re.search("""'mapCoordonneesLongitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)

        results = {'url': url, 'id': ad_id, 'price': price, 'type': property_type, 'latitude': lat, 'longitude': lng}

        print(results)

        yield results
