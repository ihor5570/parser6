import re
from datetime import datetime
from typing import Any
from urllib.parse import urlencode, urljoin

import scrapy

from utils.xlsx import XlsxReader


class PerformanceSpider(scrapy.Spider):
    name = "quattro"
    allowed_domains = ["quattro.shop"]
    start_urls = ["https://quattro.shop/katalog/search/"]

    current_date = datetime.now()

    custom_settings = {
        "FEED_URI": f'data/{name}_{current_date.strftime("%Y-%m-%d_%H%M")}-6.xlsx',
        "FEED_FORMAT": "xlsx",
        "FEED_EXPORTERS": {
            "xlsx": "scrapy_xlsx.XlsxItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.keywords = XlsxReader.get_input_data_from_xlsx()

    def start_requests(self):
        for index, keyword in enumerate(self.keywords.keys(), 1):
            params = {"q": keyword}
            url = urljoin(self.start_urls[0], "?" + urlencode(params))
            yield scrapy.Request(url, cb_kwargs={"keyword": keyword, "index": index})

    def parse(self, response, keyword, index):
        products = response.css(".catalogCard")

        for product in products:
            product_html = product.get()

            if re.search(rf"\b{re.escape(keyword)}\b", product_html):
                self.logger.info("Item[%s] Keyword %s is in stock" % (index, keyword))
                return {
                    "Производитель": self.keywords[keyword],
                    "Код": keyword,
                    "Наличие": "В наличии",
                }

        self.logger.info("Item[%s] Keyword %s is not in stock" % (index, keyword))
