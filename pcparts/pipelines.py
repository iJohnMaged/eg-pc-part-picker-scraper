# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
from .io_helper import create_folder
from pcparts import settings as pcparts_settings


class CategoryPipeline:
    def process_item(self, item, spider):
        create_folder(spider.name)
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
