import json
import scrapy
from typing import Any, Union
from datetime import datetime
from scrapy.http import Response
from dateutil import parser as date_parser


class TopicsSpider(scrapy.spiders.SitemapSpider):
    name = 'topics_crawler'
    sitemap_urls = ['https://ok.ru/sitemap-index-group-topic.xml.gz']

    def __init__(
        self,
        group: str,
        from_date: Union[datetime, str, None] = None,
        *args,
        **kwargs
    ):
        """
        SiteMapSpider crawls ok.ru group topics with comments

        :param str group: group id or name
        :param Union[datetime, str, None] from_date: last scraping date (if a string, then in '%Y-%m-%d' format)
        """
        sitemap_rules = [(f'/{group}/topic/', 'parse')]
        super(TopicsSpider, self).__init__(sitemap_rules=sitemap_rules, *args, **kwargs)
        if isinstance(from_date, str):
            self.from_date = datetime.strptime(from_date, '%Y-%m-%d')
        elif isinstance(from_date, datetime) or from_date is None:
            self.from_date = from_date
        else:
            raise TypeError(f'argument from_date must be datetime, str or None, not {type(from_date).__name__}')
        self.from_date = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None

    def sitemap_filter(self, entries):
        for entry in entries:
            date = datetime.strptime(entry['lastmod'], '%Y-%m-%d')
            if not self.from_date or date >= self.from_date:
                yield entry

    def parse(self, response: Response, **kwargs: Any) -> Any:
        try:
            topic = self.parse_topic(response)
            comments = self.parse_comments(response)
            topic.update(comments=comments)
            yield topic
        except Exception as err:
            self.logger.exception(err)

    @staticmethod
    def parse_topic(response: Response) -> dict[str, Any]:
        group_author = json.loads(response.xpath('//div[@class="mlr_top"]/div/group-author/@data').get())
        author_name = group_author['group']['name']
        author_link = group_author['group']['href']
        date_timestamp = date_parser.parse(group_author['timeInfo']['createTime']).timestamp()
        geo_name = response.xpath('//span[@data-module="MediaTopicPlace"]/text()').get()
        geo_lat = response.xpath('//media-topic-map/@lat').get()
        geo_lon = response.xpath('//media-topic-map/@lng').get()
        text = response.xpath('normalize-space(string(//div[@class="media-text_cnt"]))').get()
        comments_num = response.xpath('//div[@class="mlr_disc js-discussion-layer-block"]/div/@data-count').get()
        return {
            'id': response.url.rstrip('/').split('/')[-1],
            'type': 'topic',
            'url': response.url,
            'author': {'author_name': author_name, 'author_link': author_link},
            'geolocation': {'name': geo_name, 'lat': geo_lat, 'lon': geo_lon},
            'text': text,
            'date_timestamp': date_timestamp,
            'comments_num': int(comments_num)
        }

    @staticmethod
    def parse_comments(response: Response) -> dict[str, Any]:
        comments = response.xpath('//div[@class="comments_lst_cnt"]/div[starts-with(@id,"hook_Block_")]')
        data = []
        for comment in comments:
            comment_id = json.loads(comment.xpath('div/@data-seen-params').get())['data']['commentId']
            date_timestamp = comment.xpath('div/@data-time').get()
            author_name = comment.xpath('div/div/div/div/div/span/a[@class="comments_author-name o"]/span/text()').get()
            author_link = comment.xpath('div/div/div/div/div/span/a[@class="comments_author-name o"]/@href').get()
            replied_id = comment.xpath('div/div/div/div/span/@data-rid').get()
            text = comment.xpath('normalize-space(string(div/div/div/div/span/span[@class="js-text-full"]))').get()
            likes_num = comment.xpath('div/div/div/div/li/button/span[@class="tico tico__16"]/text()').get()
            data.append({
                'id': comment_id,
                'type': 'comment',
                'author': {'author_name': author_name, 'author_link': author_link},
                'text': text,
                'date_timestamp': int(date_timestamp),
                'replied_id': replied_id,
                'likes_num': int(likes_num)
            })
        return data
