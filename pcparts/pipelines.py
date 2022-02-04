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


class CategoryPipeline:
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
