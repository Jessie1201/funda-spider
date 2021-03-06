import scrapy

class FundaSpider(scrapy.Spider):
    name = "funda"

    start_urls = [
        'https://www.funda.nl/en/koop/almere/',
        # 'https://www.funda.nl/en/koop/heel-nederland/',
        # 'https://www.funda.nl/en/koop/provincie-noord-holland/',
    ]

    def parse(self, response):
        urls = []
        for item in response.css('li.search-result'):
            url_suffix = item.css('[data-object-url-tracking=resultlist]::attr(href)').get()
            # only houses but not appartment due to personal preference
            if url_suffix.split('/')[-2][:4] == 'huis':
                urls.append(response.urljoin(url_suffix))

        # scrape every item
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_item)

        # scrape every page
        next_page = response.css('[rel=next]::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        # html source code contains a json including some data
        source_json = eval(response.css('main#content').css('script::text').get().replace('\r\n','').strip())

        yield {
            'address': response.css('span.object-header__title::text').get(),
            'postcode': source_json['postcode'] if 'postcode' in source_json else None,
            'place': source_json['plaats'] if 'plaats' in source_json else None,
            'price': source_json['vraagprijs'] if 'vraagprijs' in source_json else None,
            'photo': response.css('div.object-media-foto').css('img::attr(src)').get(),
            'living_area': int(source_json['woonoppervlakte']) if 'woonoppervlakte' in source_json else None,
            'year': source_json['bouwjaar'] if 'bouwjaar' in source_json else None,
            'url': response.url,

            # TODO: fix, cannot get value from second page on
            # 'plot_size': response.css('span[title~=plot]+span::text').get(),
            # 'bedrooms': response.css('span[title~=bedrooms]+span::text').get(),
        }

