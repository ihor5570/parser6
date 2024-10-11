import re
from datetime import datetime
from typing import Any

import scrapy

from utils.xlsx import XlsxReader


class SavatSpider(scrapy.Spider):
    name = "savat"
    allowed_domains = ["savat-auto.com.ua"]
    start_urls = ["http://savat-auto.com.ua/search/"]

    current_date = datetime.now()

    custom_settings = {
        "FEED_URI": f'data/{name}_{current_date.strftime("%Y-%m-%d_%H%M")}-6.xlsx',
        "FEED_FORMAT": "xlsx",
        "FEED_EXPORTERS": {
            "xlsx": "scrapy_xlsx.XlsxItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOADER_MIDDLEWARES": {
            "parser6.middlewares.ProxyMiddleware": 610,
        },
        "RETRY_TIMES": 20,
    }

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.keywords = XlsxReader.get_input_data_from_xlsx()

    def start_requests(self):
        for index, keyword in enumerate(self.keywords.keys(), 1):
            url = self.start_urls[0] + keyword

            yield scrapy.Request(
                url,
                # errback=self.page_not_found,
                cb_kwargs={"keyword": keyword, "index": index},
            )

    def parse(self, response, keyword, index):
        products = response.css(".table-names table tbody tr")

        for product in products:
            product_html = product.get()

            if (
                re.search(rf"\b{re.escape(keyword)}\b", product_html)
                and "у наявності" in product_html
            ):
                self.logger.info("Item[%s] Keyword %s is in stock" % (index, keyword))
                return {
                    "Производитель": self.keywords[keyword],
                    "Код": keyword,
                    "Наличие": "В наличии",
                }

        self.logger.info("Item[%s] Keyword %s is not in stock" % (index, keyword))

    def page_not_found(self, failure):
        self.logger.info("Page not found")
