from datetime import datetime
import re
from typing import Any
from urllib.parse import urlencode, urljoin

import scrapy

from utils.xlsx import XlsxReader

cookies = {
    "evoauth": "wba3cf46559bc42a09fec4fe9550beb80",
    "cid": "202144380079170492247692750520637419919",
    "csrf_token_company_site": "2e601b5bebc44c73bf63c29e64cec5d6",
    "_ga": "GA1.1.1640673776.1703783909",
    "_ga_T7S2G9Q21Q": "GS1.1.1705248047.4.0.1705248071.0.0.0",
}

headers = {
    "authority": "performance-parts.com.ua",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://performance-parts.com.ua/ua/",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class PerformanceSpider(scrapy.Spider):
    name = "performance"
    allowed_domains = ["performance-parts.com.ua"]
    start_urls = ["https://performance-parts.com.ua/ua/site_search"]

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
            params = {"search_term": keyword}
            url = urljoin(self.start_urls[0], "?" + urlencode(params))
            yield scrapy.Request(
                url,
                headers=headers,
                cookies=cookies,
                cb_kwargs={"keyword": keyword, "index": index},
            )

    def parse(self, response, keyword, index):
        products = response.css(".b-product-gallery__item")

        for product in products:
            product_html = product.get()

            if (
                re.search(rf"\b{re.escape(keyword)}\b", product_html)
                and "В наявності" in product_html
            ):
                self.logger.info("Item[%s] Keyword %s is in stock" % (index, keyword))
                return {
                    "Производитель": self.keywords[keyword],
                    "Код": keyword,
                    "Наличие": "В наличии",
                }

        self.logger.info("Item[%s] Keyword %s is not in stock" % (index, keyword))
