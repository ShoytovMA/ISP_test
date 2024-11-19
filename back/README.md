# Сборщик
Сборщик постов в группах социальной сети [Одноклассники](https://ok.ru).

## spider.py
Осуществляет обход сайта через сайтмап и сбор постов группы и коментариев к ним.

### Параметры
```
class TopicsSpider(scrapy.spiders.sitemap.SitemapSpider)
 |  TopicsSpider(group: Union[int, str], from_date: Union[datetime.datetime, str, NoneType] = None, *args, **kwargs)
 |
 |  SiteMapSpider crawls ok.ru group topics with comments
 |
 |  Parameters:
 |      group: Union[int, str] - group id or name
 |      from_date: Union[datetime, str, None] = None - last scraping date (if a string, then in '%Y-%m-%d' format)
```

## crawler.py
Запускает `TopicsSpider`.
### Параметры
```commandline
crawler.py [-h] [--workers WORKERS] [--delay DELAY]

options:
  -h, --help         show this help message and exit
  --workers WORKERS  workers num
  --delay DELAY      delay between crawls in hours
```