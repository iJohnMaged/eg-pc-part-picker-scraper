# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
from typing import Union
from scrapy.exceptions import DropItem
from urllib.parse import quote
from pcparts import settings as pcparts_settings
from pcparts.models import (
    db_connect,
    create_all_metadata,
    Part,
    get_all_stores,
    get_all_categories,
)
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.orm import sessionmaker


class FormatPipeline:
    def __quote(self, url: str) -> str:
        return quote(url, safe="/:?=& ")

    def __parse_price_float(self, price_str: str) -> Union[float, None]:
        try:
            return float(price_str.replace("EGP", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            return None

    def process_item(self, item, _):
        item["price"] = self.__parse_price_float(item["price"])
        item["url"] = self.__quote(item["url"])
        item["image"] = self.__quote(item["image"])
        item["category"] = item["category"].lower()
        item["name"] = item["name"].lower()

        if not item["price"]:
            raise DropItem

        return item


class DatabasePipeline:
    categories = {}
    stores = {}
    parts = []

    def open_spider(self, _):
        self.engine = db_connect()
        create_all_metadata(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        session = self.Session()
        self.stores = get_all_stores(session)
        self.categories = get_all_categories(session)
        session.close()

    def process_item(self, item, spider):
        item_clone = item.copy()
        item_clone["store"] = self.stores[spider.store_name]
        item_clone["category"] = self.categories[item_clone["category"]]
        item_clone["imageUrl"] = item_clone.pop("image")
        for other_item in self.parts:
            if (
                other_item["store"] == item_clone["store"]
                and other_item["name"] == item_clone["name"]
                and other_item["category"] == item_clone["category"]
            ):
                raise DropItem
        self.parts.append(item_clone)
        return item

    def close_spider(self, _):
        if not self.parts:
            return
        try:
            # TODO: start a transaction and mark previous results from this spider with recently_scrapped = False
            # And add recently_scrapped = True to current items
            session = self.Session()
            insert_stmt = insert(Part).values(self.parts)
            update_stmt = insert_stmt.on_conflict_do_update(
                constraint="unique_part",
                set_={
                    "price": insert_stmt.excluded.price,
                },
            )
            result = session.execute(update_stmt)
            print(f"{result = }")
            session.commit()
        except Exception as e:
            print("INSERTION ERROR: ", e)
            session.rollback()
        finally:
            session.close()


class LocalJsonPipeline:
    def process_item(self, item, spider):
        filename = (
            f"{pcparts_settings.OUTPUT_DIR}/{spider.name}/{item['category']}.json"
        )
        data = []
        if not os.path.isfile(filename):
            data.append(item)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return item

        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                dupe = False
                for item_data in data:
                    if (
                        item["name"] == item_data["name"]
                        and item["url"] == item_data["url"]
                    ):
                        dupe = True
                        if item["price"] == item_data["price"]:
                            return item
                        item_data["price"] = item["price"]
                if not dupe:
                    data.append(item)
            except json.decoder.JSONDecodeError:
                data = [item]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return item
