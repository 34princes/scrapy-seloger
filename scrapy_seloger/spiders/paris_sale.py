# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
from datetime import date
"""
cd scrapy_seloger
scrapy crawl paris_sale -o paris_sale.csv -a url=https://www.urltoscrape1.com
"""

class ParisSaleSpider(scrapy.Spider):
    name = 'paris_sale'
    today = str(date.today())
    page_counter = 0
    property_counter = 1

    allowed_domains = ['www.seloger.com']

    start_urls = ["http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750101&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750102&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750103&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750104&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750105&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750106&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750107&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750108&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750109&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750110&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750111&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750112&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750113&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750114&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750115&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750116&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750117&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750118&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750119&tri=initial",
                  "http://www.seloger.com/list.htm?idtt=2&naturebien=1,2,4&idtypebien=1&ci=750120&tri=initial"
                  ]

    #def start_requests(self):
        #url = getattr(self, 'url', None)
        #yield scrapy.Request(url, self.parse)

    def parse(self, response):

        # Total number of results
        response_num_results = response.xpath('//div[@class="title_nbresult"]/text()').extract_first()
        if response.url == 'http://www.seloger.com/erreur-temporaire/':
            return "\tGET returned {}:\n\tcrawling spotted by www.seloger.com".format(response.url)

        num_results_ls = re.findall("(\d*)", response_num_results)

        # Get listed properties
        properties = response.xpath(".//div[contains(@class, 'cartouche')]")

        for property in properties:

            ad_id = property.xpath('.//@id').extract_first()

            url = property.xpath('.//a[@class="c-pa-link"]/@href').extract_first()

            property_type = property.xpath('.//a[@class="c-pa-link"]/text()').extract_first().lower()

            price_raw = property.xpath('.//span[@class="c-pa-cprice"]/text()').extract_first()
            try:
                price = int("".join(re.findall("(\d*)", price_raw)))
            except:
                price = None

            location = property.xpath('.//div[@class="c-pa-city"]/text()').extract_first()

            attrs_results = property.xpath('.//div[@class="c-pa-criterion"]/em/text()').extract()
            attrs_dict = {'chb': None, 'p': None, 'asc': 0, 'balc': 0}
            for attr in attrs_results:
                res = re.search("(\d*)\s+(\w+)", attr)
                attrs_dict[res.group(2)] = res.group(1)

            results = {'id': ad_id, 'price': price, 'type': property_type, 'date': self.today, 'url': url, 'real_coords': True, 'location': location}
            for k, v in attrs_dict.items():
                results[k] = v

            yield Request(response.urljoin(url), callback=self.parse_page, meta=results)

        # Extract next page url if exists
        next_url = response.xpath('//a[@class="pagination-next"]/@href').extract_first()
        if next_url:
            yield Request(response.urljoin(next_url), callback=self.parse)
        else:
            print("\n\tLAST PAGE REACHED")


    def parse_page(self, response):

        results = response.meta

        js = response.xpath('//script[@type="text/javascript"]/text()').extract()
        js_str = " ".join(js)
        try:
            lat = re.search("""'mapCoordonneesLatitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
            lng = re.search("""'mapCoordonneesLongitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
            lat, lng = float(lat), float(lng)
        except:  # if lat and lng fail, take the average of the coords of the bounding box

            try:
                lat1 = re.search("""'mapBoundingboxNortheastLatitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
                lat2 = re.search("""'mapBoundingboxSouthwestLatitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)

                lng1 = re.search("""'mapBoundingboxNortheastLongitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
                lng2 = re.search("""'mapBoundingboxSouthwestLongitude'.*\n.*value:\s"(\d*.\d*)""", js_str).group(1)
                lat = round((float(lat1) + float(lat2)) / 2, 5)
                lng = round((float(lng1) + float(lng2)) / 2, 5)

                results['real_coords'] = False

            except:
                lat, lng = None, None

        results['latitude'] = lat
        results['longitude'] = lng

        [results.pop(k) for k in ['download_latency', 'download_slot', 'depth', 'download_timeout']]

        replace_column_names = {'m²': 'sqm', 'p': 'rooms', 'chb': 'bedrooms', 'balc': 'balcony', 'asc': 'lift'}
        for k, v in replace_column_names.items():
            results[v] = results.pop(k)

        yield results
