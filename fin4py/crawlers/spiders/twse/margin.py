import datetime
import json

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, SelectJmes
from fin4py.crawlers.utils import ItemParser


class MarginTradingItem(scrapy.Item):
    date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date)
    )  # 資料日期
    code = scrapy.Field()  # 證券代號
    name = scrapy.Field()  # 證券名稱

    long = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, int))  # 融資買進
    long_flat = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融資賣出
    long_flat_repayment = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融資現金償還
    long_deposit_last = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融資前日餘額
    long_deposit = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融資今日餘額
    long_deposit_limit = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融資限額

    short_flat = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融券買進
    short = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, int))  # 融券賣出
    short_flat_repayment = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融券現券償還
    short_deposit_last = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融券前日餘額
    short_deposit = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融券今日餘額
    short_deposit_limit = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 融券限額

    class Meta:
        fields = [
            "code",
            "name",
            "long",
            "long_flat",
            "long_flat_repayment",
            "long_deposit_last",
            "long_deposit",
            "long_deposit_limit",
            "short_flat",
            "short",
            "short_flat_repayment",
            "short_deposit_last",
            "short_deposit",
            "short_deposit_limit",
        ]


class MarginTradingSpider(scrapy.Spider):
    name = "twse_margin_trading"
    allowed_domains = ["www.twse.com.tw"]
    date = datetime.date.today().strftime("%Y%m%d")

    def start_requests(self):
        self.logger.info(f"Parsing date: {self.date}")
        yield scrapy.Request(
            url=f"https://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date={self.date}&selectType=ALL",
            callback=self.parse,
            encoding="cp950",
        )

    def parse(self, response):
        self.logger.info("%s", response.url)
        terms = MarginTradingItem.Meta.fields
        jresp = json.loads(response.text)
        data = SelectJmes("data")(jresp)
        if not data:
            return
        date = SelectJmes("date")(jresp)
        for row in data:
            loader = ItemLoader(item=MarginTradingItem())
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("date", date)
            for idx, field in enumerate(terms):
                loader.add_value(field, SelectJmes(f"[{idx}]")(row))
            yield loader.load_item()
