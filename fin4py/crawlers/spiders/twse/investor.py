import datetime
import json

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, SelectJmes
from fin4py.crawlers.utils import ItemParser


class InvestorTradingItem(scrapy.Item):
    date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date)
    )  # 資料日期
    code = scrapy.Field()  # 證券代號
    name = scrapy.Field()  # 證券名稱

    foreign_buy = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外陸資買進股數(不含外資自營商)
    foreign_sell = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外陸資賣出股數(不含外資自營商)
    foreign_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外陸資買賣超股數(不含外資自營商)

    foreign_dealer_buy = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外資自營商買進股數
    foreign_dealer_sell = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外資自營商賣出股數
    foreign_dealer_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 外資自營商買賣超股數

    trust_buy = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 投信買進股數
    trust_sell = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 投信賣出股數
    trust_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 投信買賣超股數

    dealer_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商買賣超股數
    native_dealer_buy = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商買進股數(自行買賣)
    native_dealer_sell = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商賣出股數(自行買賣)
    native_dealer_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商買賣超股數(自行買賣)
    native_dealer_hedge_buy = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商買進股數(避險)
    native_dealer_hedge_sell = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商賣出股數(避險)
    native_dealer_hedge_net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 自營商買賣超股數(避險)

    net = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 三大法人買賣超股數

    class Meta:
        fields = [
            "code",
            "name",
            "foreign_buy",
            "foreign_sell",
            "foreign_net",
            "foreign_dealer_buy",
            "foreign_dealer_sell",
            "foreign_dealer_net",
            "trust_buy",
            "trust_sell",
            "trust_net",
            "dealer_net",
            "native_dealer_buy",
            "native_dealer_sell",
            "native_dealer_net",
            "native_dealer_hedge_buy",
            "native_dealer_hedge_sell",
            "native_dealer_hedge_net",
            "net",
        ]


class InvestorTradingSpider(scrapy.Spider):
    name = "twse_investor_trading"
    allowed_domains = ["www.twse.com.tw"]
    date = datetime.date.today().strftime("%Y%m%d")

    def start_requests(self):
        self.logger.info(f"Parsing date: {self.date}")
        yield scrapy.Request(
            url=f"https://www.twse.com.tw/fund/T86?response=json&date={self.date}&selectType=ALLBUT0999",
            callback=self.parse,
            encoding="cp950",
        )

    def parse(self, response):
        self.logger.info("%s", response.url)
        fields = InvestorTradingItem.Meta.fields
        jresp = json.loads(response.text)
        data = SelectJmes("data")(jresp)
        if not data:
            return
        date = SelectJmes("date")(jresp)
        for row in data:
            loader = ItemLoader(item=InvestorTradingItem())
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("date", date)
            for idx, field in enumerate(fields):
                loader.add_value(field, SelectJmes(f"[{idx}]")(row))
            yield loader.load_item()
