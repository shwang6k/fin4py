import datetime
import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class StockInfoItem(scrapy.Item):
    date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date)
    )  # 資料日期
    code = scrapy.Field()  # 證券代號
    name = scrapy.Field()  # 股票名稱
    publish_shares = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 已發行普通股數
    listing_date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date_minguo)
    )  # 掛牌日

    class Meta:
        pass


class StockInfoSpider(scrapy.Spider):
    name = "twse_stock_info"
    allowed_domains = ["mops.twse.com.tw"]
    date = datetime.date.today().strftime("%Y%m%d")
    form = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "TYPEK": "sii",
        "code": "",
    }

    def start_requests(self):
        self.logger.info(f"Parsing date: {self.date}")
        yield scrapy.FormRequest(
            url="https://mops.twse.com.tw/mops/web/ajax_t51sb01",
            formdata=self.form,
            callback=self.parse,
        )

    def parse(self, response):
        self.logger.info("%s", response.url)
        x_paths = [
            ("code", "//td[1]/text()"),
            ("name", "//td[3]/text()"),
            ("listing_date", "//td[15]/text()"),
            ("publish_shares", "//td[18]/text()"),
        ]
        rows = response.xpath("//tr[count(td)=39]").extract()
        for row in rows:
            loader = ItemLoader(item=StockInfoItem(), selector=Selector(text=row))
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("date", self.date)
            for field, path in x_paths:
                loader.add_xpath(field, path)
            yield loader.load_item()
