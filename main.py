from scrapy.crawler import CrawlerProcess
from scrapy.utils import project
from scrapy import spiderloader


def main():
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    spiders_classes = [spider_loader.load(name) for name in spiders]

    crawlers = {}
    process = CrawlerProcess(settings=settings)
    for spider_class in spiders_classes:
        crawlers[spider_class.name] = process.create_crawler(spider_class)
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
    main()
