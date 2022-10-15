import scrapy
from w3lib.html import remove_tags,replace_tags

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

            request = scrapy.Request(article["article_url"], callback=self.parse_article, cb_kwargs=article)
            yield request

    def parse_article(self, response, heading, article_url, summary, label, publish_time):
        item = dict()
        article = response.css('article[class*=ArticleWrapper]')
        if response.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text'):
            item['article_title'] = article.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text').get()
        elif 'sport' in article_url:  # Need to work upon.
            item['article_title'] = article.css('h1.qa-story-headline::text').get()
        else:
            item['article_title'] = article.css('div.ssrcss-1u9a4pt-HeadingContainer h1::text').get()

        if response.css('span.ssrcss-1if1g9v-MetadataText time'):
            item['article_publish_time'] = response.css('span.ssrcss-1if1g9v-MetadataText time').attrib['datetime']
        else:
            item['article_publish_time'] = None

        item['article_author'] = article.css('div.ssrcss-68pt20-Text-TextContributorName::text').get()
        item['article_tag'] = response.css('div.ssrcss-84ltp5-Text::text').get()
        item['article_text'] = self.extract_articles(article)
        item["heading"] = heading
        item["article_url"] = article_url
        item["summary"] = summary
        item["label"] = label
        item["publish_time"] = publish_time

        return item

    def extract_articles(self, article):
        try:
            paragraph = ""

            for para in article.css('div[class*=RichTextComponentWrapper]'):
                paragraph += replace_tags(para.get(), " ")

            return paragraph
        except:
            return "Not able to extract"
