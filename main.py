from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pcparts import settings as pcparts_settings

from pcparts.spiders.EgPrices import EgpricesSpider
from pcparts.spiders.CompuArt import CompuartSpider


def main():
    settings = Settings()
    settings.setmodule(pcparts_settings)
    process = CrawlerProcess(settings=settings)
    process.crawl(EgpricesSpider)
    process.crawl(CompuartSpider)
    process.start()


if __name__ == "__main__":
    main()
