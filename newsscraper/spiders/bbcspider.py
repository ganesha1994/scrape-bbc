import scrapy
from w3lib.html import remove_tags, replace_tags
from newsscraper import constants as c


class BbcSpider(scrapy.Spider):
    name = 'bbc'
    root_url = 'https://www.bbc.com'
    allowed_domains = ['bbc.com']
    start_urls = [root_url + '/sport' ]#,root_url + '/news'

    # def parse(self, response):#News
    #     for promo_articles in response.css('div.gs-c-promo-body'):
    #
    #         promo_articles_heading = promo_articles.css('div a.gs-c-promo-heading')
    #         article = dict()
    #
    #         article[c.d_heading_key] = promo_articles_heading.css('h3.gs-c-promo-heading__title::text').get()
    #
    #         url = promo_articles.css('::attr(href)').get()
    #         if 'http' in url:
    #             article[c.d_article_url] = url
    #         else:
    #             article[c.d_article_url] = self.root_url + url
    #
    #         article[c.d_summary_key] = promo_articles.css('div p.gs-c-promo-summary::text').get()
    #
    #         if 'sport' in article[c.d_article_url]:
    #             request = scrapy.Request(article[c.d_article_url], callback=self.parse_sports_article, cb_kwargs=article)
    #         else:
    #             request = scrapy.Request(article[c.d_article_url], callback=self.parse_article, cb_kwargs=article)
    #         yield request

    def parse(self, response):#sports
        for promo_articles in response.css('div.ssrcss-tq7xfh-PromoContent'):

            promo_articles_heading = promo_articles.css('div.ssrcss-1f3bvyz-Stack')
            item = dict()
            item[c.d_heading_key] = promo_articles_heading.css('p.ssrcss-6arcww-PromoHeadline span::text').get()
            url = promo_articles_heading.css('a::attr(href)').get()
            if 'http' in url:
                item[c.d_article_url] = url
            else:
                item[c.d_article_url] = self.root_url + url

            item[c.d_summary_key] = promo_articles_heading.css('p.ssrcss-1q0x1qg-Paragraph::text').get()

            if 'sport' in item[c.d_article_url]:
                request = scrapy.Request(item[c.d_article_url], callback=self.parse_sports_article, cb_kwargs=dict(item=item))
            else:
                request = scrapy.Request(item[c.d_article_url], callback=self.parse_article, cb_kwargs=dict(item=item))
            yield request

    def parse_sports_article(self, response, item):

        sports_article = response.css('div.gel-layout__item')

        item[c.d_article_title] = sports_article.css('h1.qa-story-headline::text').get()
        item[c.d_article_publish_time] = sports_article.css('span.gs-c-timestamp time::attr(datetime)').get()

        item[c.d_article_author] = sports_article.css('span.qa-contributor-name::text').get()
        item[c.d_article_tag] = sports_article.css('span.gs-u-align-middle a::text').get()

        item[c.d_article_text] = self.extract_sports_articles(sports_article)

        return item

    def parse_article(self, response, item):

        article = response.css('article[class*=ArticleWrapper]')

        if article.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text'):
            item[c.d_article_title] = article.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text').get()
        else:
            item[c.d_article_title] = article.css('div.ssrcss-1u9a4pt-HeadingContainer h1::text').get()

        item[c.d_article_publish_time] = article.css('span.ssrcss-1if1g9v-MetadataText time::attr(datetime)').get()
        item[c.d_article_author] = article.css('div.ssrcss-68pt20-Text-TextContributorName::text').get()
        item[c.d_article_tag] = article.css('div.ssrcss-84ltp5-Text::text').get()

        item[c.d_article_text] = self.extract_articles(article)
        return item

    def extract_articles(self, response):
        try:
            paragraph = ""

            for para in response.css('div[class*=RichTextComponentWrapper]'):
                paragraph += replace_tags(para.get(), " ")

            return paragraph
        except:
            return "Not able to extract"

    def extract_sports_articles(self, response):
        try:
            paragraph = ""

            for para in response.css('div.qa-story-body'):
                paragraph += replace_tags(para.get(), " ")

            return paragraph
        except:
            return "Not able to extract"
