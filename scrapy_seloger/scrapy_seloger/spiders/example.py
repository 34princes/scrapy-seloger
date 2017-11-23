# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class SaleSpider(scrapy.Spider):
    name = 'sale'
    allowed_domains = ['zoopla.co.uk']
    start_urls = ['https://www.zoopla.co.uk/for-sale/flats/angel/?beds_min=1&price_max=3000000&price_min=400000&q=Angel%2C%20London&results_sort=newest_listings&search_source=home&page_size=100']


    def parse(self, response):

        import re
        from posixpath import join as urljoin
        # Extract properties
        properties = response.xpath('//li[@class="srp clearfix   "]')
        base_url = "https://www.zoopla.co.uk"

        for property in properties:

            listing_id = property.xpath('.//@data-listing-id').extract_first()

            relative_url = property.xpath('.//a/@href').extract_first()
            url = urljoin(base_url, relative_url[1:len(relative_url)])

            # Get price
            price_str = property.xpath('.//a[@class="listing-results-price text-price"]/text()').extract_first()
            try:
                price_str_clean = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", price_str)
                price = int(price_str_clean[0].replace(",", ""))
            except:
                price = None
            # Get address
            location_info = property.xpath('.//span[@itemprop="address"]')
            try:
                full_address = location_info.xpath('.//a[@class="listing-results-address"]/text()').extract_first()
            except:
                full_address = None
            try:
                street_address = location_info.xpath('.//meta[@itemprop="streetAddress"]/@content').extract_first()
            except:
                street_address = None
            try:
                location = location_info.xpath('.//meta[@itemprop="addressLocality"]/@content').extract_first()
            except:
                location = None

            # Get geo-location
            try:
                geo = property.xpath('.//div[@itemprop="geo"]')
                lat = geo.xpath('.//meta[@itemprop="latitude"]/@content').extract_first()
                lon = geo.xpath('.//meta[@itemprop="longitude"]/@content').extract_first()
            except:
                lat, lon = None, None

            # Get property attributes
            try:
                num_beds = int(property.xpath('.//span[@class="num-icon num-beds"]/text()').extract_first())
            except TypeError:
                num_beds = None

            try:
                num_baths = int(property.xpath('.//span[@class="num-icon num-baths"]/text()').extract_first())
            except TypeError:
                num_baths = None

            try:
                num_receptions = int(property.xpath('.//span[@class="num-icon num-reception"]/text()').extract_first())
            except TypeError:
                num_receptions = None

            try:
                num_sqft_str = property.xpath('.//span[@class="num-icon num-sqft "]/text()').extract_first()
                num_sqft_clean = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", num_sqft_str)
                num_sqft = int(num_sqft_clean[0].replace(",", ""))
                surface_sqm = round(num_sqft * 0.092903, 2)
            except TypeError:
                surface_sqm = None


            yield {'Price': price,
                   'Num bedrooms': num_beds,
                   'Num bathrooms': num_baths,
                   'Num receptions': num_receptions,
                   'Surface_sqm': surface_sqm,
                   'URL': url,
                   'Listing id': listing_id,
                   'Street address': street_address,
                   'Location': location,
                   'Full address': full_address,
                   'Longitude': lon,
                   'Latitude': lat}

        # Extract next page url if exists
        relative_next_url = response.xpath('//div[@class="paginate bg-muted"]/a[contains(text(),"Next")]/@href').extract_first()
        if relative_next_url:

            next_page_url = urljoin(base_url, relative_next_url[1:len(relative_next_url)])
            print("\n\tTHE NEXT PAGE IS:\n\t\t", next_page_url, "\n\n")
            yield Request(url=next_page_url, callback=self.parse)
        else:
            print("\n\tLAST PAGE REACHED\n\n")

