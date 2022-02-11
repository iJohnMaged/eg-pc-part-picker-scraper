import sys
import os
import django

from scrapy.crawler import CrawlerProcess
from scrapy.utils import project
from scrapy import spiderloader

# Django
sys.path.append("./PcBuilder")
os.environ["DJANGO_SETTINGS_MODULE"] = "PcBuilder.settings"

django.setup()

from ScrapedItems.models import Store, Category


def init_db(spider_classes):
    """
    Inserts missing stores and categories into the database.
    """
    for spider in spider_classes:
        for category in spider.start_urls:
            Category.objects.get_or_create(name=category)
        Store.objects.get_or_create(name=spider.store_name, url=spider.store_url)


def main():
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    spiders_classes = [spider_loader.load(name) for name in spiders]

    crawlers = {}
    process = CrawlerProcess(settings=settings)
    for spider_class in spiders_classes:
        crawlers[spider_class.name] = process.create_crawler(spider_class)
    init_db(spiders_classes)
    for crawler in crawlers.values():
        process.crawl(crawler)

    process.start()

    print("---- Finished ----")
    for name, crawler in crawlers.items():
        stats = crawler.stats.get_stats()
        print(f"{name = }")
        print(f"log_count/ERROR: {stats.get('log_count/ERROR', 0)}")
        print(f"item_scraped_count: {stats.get('item_scraped_count', 0)}")
        print("-----")


if __name__ == "__main__":
    print("Starting...")
    main()
