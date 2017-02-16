import scrapy

from feeds.loaders import FeedEntryItemLoader
from feeds.spiders import FeedsSpider


class VerbraucherrechtAtSpider(FeedsSpider):
    name = 'verbraucherrecht.at'
    allowed_domains = ['verbraucherrecht.at']
    start_urls = ['https://verbraucherrecht.at/cms/index.php?id=198']

    _title = 'Verbraucherrecht'
    _subtitle = 'Neuigkeiten rund um Konsumentenschutz und Verbraucherrechte'
    _author_name = 'Verein für Konsumenteninformation'
    _link = 'https://{}'.format(name)
    _logo = ('https://{}/cms/fileadmin/imag/logo.gif'.format(name))
    _timezone = 'Europe/Vienna'

    def parse(self, response):
        # Fetch only the current news page and deliberately ignore old news.
        for link in response.xpath(
                '//div[@class="news-list-container"]//h2/a/@href').extract():
            yield scrapy.Request(response.urljoin(link), self.parse_item)

    def parse_item(self, response):
        il = FeedEntryItemLoader(
            response=response,
            base_url='{}/cms/'.format(self._link),
            timezone=self._timezone,
            remove_elems=['.news-latest-date', '.news-single-rightbox', 'hr',
                          'h7'],
            remove_elems_xpath=['//div[@class="news-single-item"]/b[1]',
                                '//div[@class="news-single-item"]/br[1]'],
        )

        il.add_value(
            'title',
            response.xpath('//head/title/text()').re_first(r'::: (.*)'))

        il.add_value('link', response.url)

        il.add_value(
            'updated',
            response.xpath('//div[@class="news-single-rightbox"]').
            re_first(r'(\d{2}\.\d{2}\.\d{4})'))

        il.add_value(
            'author_name',
            response.xpath('//head/meta[@name="publisher"]/@content').
            re_first('recht.at, (.*);'))
        il.add_xpath('author_name', '//head/meta[@name="author"]/@content')
        il.add_value('author_name', self.name)

        il.add_xpath('author_email', '//head/meta[@name="reply-to"]/@content')

        il.add_css('content_html', '.news-single-item h7 font strong')
        il.add_css('content_html', '.news-single-item')

        yield il.load_item()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent
