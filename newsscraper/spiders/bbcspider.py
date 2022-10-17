import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.html import replace_tags

from newsscraper import constants as c


class BbcSpider(CrawlSpider):
    name = 'bbc'
    root_url = 'https://www.bbc.com'
    allowed_domains = ['bbc.com']

    # Root URL to crawl
    start_urls = [root_url + '/news']

    # Only selecting URL which has sport and news in it.
    rules = \
        (
            Rule(LinkExtractor(allow='news'), callback='parse_news_page'),
            Rule(LinkExtractor(allow='sport'), callback='parse_sports_page')
        )

    """
    This method is used for parse home page of bbc news
    :param Response object of the url crawled
    :return Request to specific news article which were present on the home page"""

    def parse_news_page(self, response):
        self.logger.info("Parsing News page")
        try:
            for promo_articles in response.css('div.gs-c-promo-body'):

                promo_articles_heading = promo_articles.css('div a.gs-c-promo-heading')
                item = dict()

                item[c.d_heading_key] = promo_articles_heading.css('h3.gs-c-promo-heading__title::text').get()

                url = promo_articles.css('::attr(href)').get()
                if 'http' in url:
                    item[c.d_article_url] = url
                else:
                    item[c.d_article_url] = self.root_url + url

                item[c.d_summary_key] = promo_articles.css('div p.gs-c-promo-summary::text').get()

                if 'sport' in item[c.d_article_url]:
                    request = scrapy.Request(item[c.d_article_url], callback=self.parse_sports_article,
                                             cb_kwargs=dict(item=item))
                else:
                    request = scrapy.Request(item[c.d_article_url], callback=self.parse_article,
                                             cb_kwargs=dict(item=item))
                yield request
        except Exception as e:
            self.logger.error("Error occurred while scraping news page" + str(e))

    """
    This method is used for parse sports home page of bbc news
    :param Response object of the url crawled
    :return Request to specific sports article which were present on the home page"""

    def parse_sports_page(self, response):
        self.logger.info("Parsing sports page")
        try:
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
                    request = scrapy.Request(item[c.d_article_url], callback=self.parse_sports_article,
                                             cb_kwargs=dict(item=item))
                else:
                    request = scrapy.Request(item[c.d_article_url], callback=self.parse_article,
                                             cb_kwargs=dict(item=item))
                yield request
        except Exception as e:
            self.logger.error("Error occurred while scraping sports page" + str(e))

    """
    This method is used for parse an sports article
    :param Response object of the url crawled
    :return Item object with the data parsed from the article"""

    def parse_sports_article(self, response, item):
        self.logger.info("Parsing sports article")
        try:
            sports_article = response.css('div.gel-layout__item')

            item[c.d_article_title] = sports_article.css('h1.qa-story-headline::text').get()
            item[c.d_article_publish_time] = sports_article.css('span.gs-c-timestamp time::attr(datetime)').get()

            item[c.d_article_author] = sports_article.css('span.qa-contributor-name::text').get()
            item[c.d_article_tag] = sports_article.css('span.gs-u-align-middle a::text').get()

            article_text_selector = 'div.qa-story-body'
            item[c.d_article_text] = self.extract_articles(sports_article, article_text_selector)

            return item
        except Exception as e:
            self.logger.error("Error occurred while scraping sports article" + str(e))

    """
    This method is used for parse an news article
    :param Response object of the url crawled
    :return Item object with the data parsed from the article"""

    def parse_article(self, response, item):
        self.logger.info("Parsing news article")
        try:
            article = response.css('article[class*=ArticleWrapper]')

            if article.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text'):
                item[c.d_article_title] = article.css('header.ssrcss-1eqcsb1-HeadingWrapper h1::text').get()
            else:
                item[c.d_article_title] = article.css('div.ssrcss-1u9a4pt-HeadingContainer h1::text').get()

            item[c.d_article_publish_time] = article.css('span.ssrcss-1if1g9v-MetadataText time::attr(datetime)').get()
            item[c.d_article_author] = article.css('div.ssrcss-68pt20-Text-TextContributorName::text').get()
            item[c.d_article_tag] = article.css('div.ssrcss-84ltp5-Text::text').get()

            article_text_selector = 'div[class*=RichTextComponentWrapper]'
            item[c.d_article_text] = self.extract_articles(article, article_text_selector)
            return item
        except Exception as e:
            self.logger.error("Error occurred while scraping news article" + str(e))

    """
    This method is used extract article text from the url crawled
    :param Response object of the url crawled
    :param css_selector - selection criteria for extracting the text
    :return Item object with the data parsed from the article"""

    def extract_articles(self, response, css_selector):
        self.logger.info("Extracting aticle text from an page")
        try:
            paragraph = ""

            for para in response.css(css_selector):
                paragraph += replace_tags(para.get(), " ")

            return re.sub(' +', ' ', paragraph)
        except Exception as e:
            self.logger.error("Error occurred while extracting article text from an url" + str(e))
            return ""
