from scrapy.crawler import CrawlerProcess
from scrapy.utils import project
from scrapy import spiderloader
from pcparts.models import (
    db_connect,
    get_all_stores,
    get_all_categories,
    create_all_metadata,
    sessionmaker,
    Category,
    Store,
)


def init_db(spider_classes):
    """
    Inserts missing stores and categories into the database.
    """
    engine = db_connect()
    create_all_metadata(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    stores = get_all_stores(session)
    categories = get_all_categories(session)
    stores_to_insert = []
    categories_to_insert = []

    for spider_class in spider_classes:
        for category in spider_class.start_urls:
            if category not in categories:
                categories_to_insert.append({"name": category})
        if spider_class.store_name not in stores:
            stores_to_insert.append(
                {"name": spider_class.store_name, "url": spider_class.store_url}
            )

    if stores_to_insert:
        session.bulk_insert_mappings(Store, stores_to_insert)
    if categories_to_insert:
        session.bulk_insert_mappings(Category, categories_to_insert)
    session.commit()
    

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
    main()
