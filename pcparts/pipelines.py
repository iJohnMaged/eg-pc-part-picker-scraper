# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
from typing import Union
from scrapy.exceptions import DropItem
from urllib.parse import quote, unquote
from pcparts import settings as pcparts_settings

from ScrapedItems.models import Component, Store, Category


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
        if unquote(item["url"]) == item["url"]:
            item["url"] = self.__quote(item["url"])
        if unquote(item["image"]) == item["image"]:
            item["image"] = self.__quote(item["image"])
        item["category"] = item["category"].lower()
        item["name"] = item["name"]

        if not item["price"]:
            raise DropItem

        return item


class DatabasePipeline:
    categories = {}
    stores = {}
    parts = []

    def open_spider(self, _):
        self.stores = {store.name: store.id for store in Store.objects.all()}
        self.categories = {category.name: category.id for category in Category.objects.all()}

    def process_item(self, item, spider):
        item_clone = item.copy()
        item_clone["store_id"] = self.stores[spider.store_name]
        item_clone["category_id"] = self.categories[item_clone.pop("category")]
        item_clone["recently_scraped"] = True
        for other_item in self.parts:
            # Shortcut dupe items from scraped data
            if (
                other_item["store_id"] == item_clone["store_id"]
                and other_item["name"] == item_clone["name"]
                and other_item["category_id"] == item_clone["category_id"]
            ):
                raise DropItem
        self.parts.append(item_clone)
        return item

    def close_spider(self, spider):
        if not self.parts:
            return
        
        store_id = self.stores[spider.store_name]
        
        Component.objects.filter(store_id=store_id).update(recently_scraped=False)

        records_to_update = []
        records_to_create = []

        records = [
            {
                "id": Component.objects.filter(
                    category_id=part["category_id"],
                    store_id=part["store_id"],
                    name=part["name"],
                    url=part["url"],
                ).first().id
                if Component.objects.filter(
                    category_id=part["category_id"],
                    store_id=part["store_id"],
                    name=part["name"],
                ).first() is not None else None, **part
            }
            for part in self.parts
        ]

        for record in records:
            if record["id"] is not None:
                records_to_update.append(record)
            else:
                record.pop("id")
                records_to_create.append(record)
        Component.objects.bulk_create(
            [Component(**values) for values in records_to_create], batch_size=100
        )
        Component.objects.bulk_update(
            [
                Component(id=values.get("id"), price=values.get("price"), url=values.get("url"), image=values.get("image"), recently_scraped=True)
                for values in records_to_update
            ],
            ["price", "url", "image", "recently_scraped"],
            batch_size=100
        )
        
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
