import json
import datetime

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, SelectJmes
from fin4py.crawlers.utils import ItemParser


class QuoteItem(scrapy.Item):
    date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date)
    )  # 資料日期
    code = scrapy.Field()  # 證券代號
    name = scrapy.Field()  # 證券名稱
    shares = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, int))  # 成交股數
    count = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, int))  # 成交筆數
    amount = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, int))  # 成交金額
    open = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, float))  # 開盤價
    high = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, float))  # 最高價
    low = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, float))  # 最低價
    close = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, float))  # 收盤價
    change_sign = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_sign)
    )  # 漲跌記號
    change = scrapy.Field(input_processor=MapCompose(ItemParser.p_num, float))  # 漲跌值
    last_bid = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 最後揭示買價
    last_bid_qty = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 最後揭示買量
    last_ask = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 最後揭示賣價
    last_ask_qty = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 最後揭示賣量
    pe_ratio = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 本益比

    class Meta:
        fields = [
            "code",
            "name",
            "shares",
            "count",
            "amount",
            "open",
            "high",
            "low",
            "close",
            "change_sign",
            "change",
            "last_bid",
            "last_bid_qty",
            "last_ask",
            "last_ask_qty",
            "pe_ratio",
        ]


class QuoteSpider(scrapy.Spider):
    name = "twse_quote"
    allowed_domains = ["www.twse.com.tw"]
    date = datetime.date.today().strftime("%Y%m%d")

    def start_requests(self):
        self.logger.info(f"Parsing date: {self.date}")
        yield scrapy.Request(
            url=f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={self.date}&type=ALLBUT0999",
            callback=self.parse,
            encoding="cp950",
        )

    def parse(self, response):
        self.logger.info("%s", response.url)
        terms = QuoteItem.Meta.fields
        jresp = json.loads(response.text)
        data = SelectJmes("data9")(jresp)
        if not data:
            return
        date = SelectJmes("date")(jresp)
        for row in data:
            loader = ItemLoader(item=QuoteItem())
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("date", date)
            for idx, field in enumerate(terms):
                loader.add_value(field, SelectJmes(f"[{idx}]")(row))
            yield loader.load_item()
