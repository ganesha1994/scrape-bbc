import scrapy


class BbcSpider(scrapy.Spider):
    name = 'bbc'
    root_url = 'https://www.bbc.com'
    allowed_domains = ['bbc.com']
    start_urls = [root_url + '/news']

    def parse(self, response):
        for promo_articles in response.css('div.gs-c-promo-body'):

            promo_articles_heading = promo_articles.css('div a.gs-c-promo-heading')
            article = dict()

            article["heading"] = promo_articles_heading.css('h3.gs-c-promo-heading__title::text').get()

            if 'http' in promo_articles_heading.attrib['href']:
                article["article_url"] = promo_articles_heading.attrib['href']
            else:
                article["article_url"] = self.root_url + promo_articles_heading.attrib['href']

            article["summary"] = promo_articles.css('div p.gs-c-promo-summary::text').get()

            if promo_articles.css('div ul.gs-o-list-inline li.nw-c-promo-meta a span::text'):
                article["label"] = promo_articles.css('div ul.gs-o-list-inline li.nw-c-promo-meta a span::text').get()
            else:
                article["label"] = None

            if promo_articles.css('div ul.gs-o-list-inline li.nw-c-promo-meta span.gs-c-timestamp time'):
                article["publish_time"] = \
                    promo_articles.css('div ul.gs-o-list-inline li.nw-c-promo-meta span.gs-c-timestamp time').attrib["datetime"]
            else:
                article["publish_time"] = None

            yield article