import time
import json
import redis
import scrapy
import logging
import schedule
import multiprocessing
from spider import TopicsSpider
from multiprocessing import Pool
from argparse import ArgumentParser
from scrapyscript import Job, Processor
from datetime import datetime, timedelta

spider_params_db = redis.Redis(decode_responses=True, db=0)
crawled_data_db = redis.Redis(db=1)


def crawl_group(group: str):
    spider_params = spider_params_db.hgetall(group)
    processor = Processor(settings=scrapy.settings.Settings(values={'LOG_LEVEL': 'CRITICAL'}))
    job = Job(TopicsSpider, **spider_params)
    data_updates = processor.run(job)
    data_updates = {item['id']: item for item in data_updates}
    data = crawled_data_db.get(group)
    if data_updates:
        if data:
            data = json.loads(data)
            data.update(data_updates)
        else:
            data = data_updates
        crawled_data_db.set(group, value=json.dumps(data))
    spider_params['from_date'] = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    spider_params_db.hmset(group, spider_params)


def main(workers: int = multiprocessing.cpu_count()):
    logging.debug('Start crawlers')
    keys = spider_params_db.keys()
    pool = Pool(workers)
    pool.map(crawl_group, keys)
    logging.debug('Sleep')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--workers', type=int, help='workers num', default=multiprocessing.cpu_count())
    parser.add_argument('--delay', type=int, help='delay between crawls in hours', default=24)
    args = parser.parse_args()

    main(args.workers)  # first run
    schedule.every(args.delay).minutes.do(main, workers=args.workers)  # schedule next runs

    while True:
        schedule.run_pending()
        time.sleep(1)
