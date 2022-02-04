from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pcparts import settings as pcparts_settings

from pcparts.spiders.EgPrices import EgpricesSpider
from pcparts.spiders.CompuArt import CompuartSpider
from pcparts.spiders.ElbadrGroup import ElBadrGroupSpider
from pcparts.spiders.MaximumHardware import MaximumHardwareSpider
from pcparts.spiders.HighEnd import HighEndSpider


def main():
    spiders = [
        EgpricesSpider,
        CompuartSpider,
        ElBadrGroupSpider,
        MaximumHardwareSpider,
        HighEndSpider,
    ]
    crawlers = {}
    settings = Settings()
    settings.setmodule(pcparts_settings)
    process = CrawlerProcess(settings=settings)
    for spider in spiders:
        crawlers[spider.name] = process.create_crawler(spider)
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
