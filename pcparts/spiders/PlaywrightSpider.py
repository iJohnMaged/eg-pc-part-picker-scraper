import scrapy
from pcparts.io_helper import create_folder
from scrapy_playwright.page import PageCoroutine
from pcparts import settings as pcparts_settings


class PlaywrightSpider(scrapy.Spider):
    initial_metadata = dict(
        playwright=True,
        playwright_include_page=True,
        playwright_page_coroutines=[
            PageCoroutine("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageCoroutine("wait_for_load_state", "networkidle"),
        ],
        page_number=1,
        is_in_stock=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_folder(f"{pcparts_settings.OUTPUT_DIR}/{self.name}")
        for category, _ in self.start_urls.items():
            with open(
                f"{pcparts_settings.OUTPUT_DIR}/{self.name}/{category}.json", "w"
            ) as f:
                f.write("[]")
