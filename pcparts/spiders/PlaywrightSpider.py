import scrapy
from pcparts.io_helper import create_folder
from scrapy_playwright.page import PageCoroutine
from pcparts import settings as pcparts_settings
import re


class PlaywrightSpider(scrapy.Spider):
    required_attrs = ["start_urls", "query_params"]
    initial_metadata = dict(
        playwright=True,
        playwright_include_page=True,
        playwright_page_coroutines=[
            PageCoroutine("route", re.compile(".google."), lambda route: route.abort()),
            PageCoroutine("wait_for_load_state", "domcontentloaded", timeout=60),
            PageCoroutine("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
        ],
        page_number=1,
    )
    page_keyword = "page"

    def generate_url_with_query_params(self, url: str, page: int) -> str:
        url_with_query_params = f"{url}?{self.page_keyword}={page}"
        try:
            for key, value in self.query_params.items():
                url_with_query_params += f"&{key}={value}"
        except AttributeError:
            pass
        return url_with_query_params

    def start_requests(self):
        for category, initial_url in self.start_urls.items():
            metadata = self.initial_metadata.copy()
            metadata.update(category=category)
            yield scrapy.Request(
                self.generate_url_with_query_params(
                    initial_url, metadata["page_number"]
                ),
                meta=metadata,
            )

    def __assert_initial_values(self):
        for attr in self.required_attrs:
            assert not not getattr(
                self, attr, None
            ), f"{attr} is required in {self.name}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__assert_initial_values()
        create_folder(f"{pcparts_settings.OUTPUT_DIR}/{self.name}")
        for category, _ in self.start_urls.items():
            with open(
                f"{pcparts_settings.OUTPUT_DIR}/{self.name}/{category}.json", "w"
            ) as f:
                f.write("[]")
