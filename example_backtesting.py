from fin4py import Stock
from fin4py.backtesting import BandTest
from pylab import show

if __name__ == "__main__":
    # 建立股票資訊連結以及將資訊丟入回測程式
    s = Stock("2330", "2015-10-31", "2016-03-05")
    bt = BandTest(s)

    # 範例策略一
    # 在歷史股價內新增K, D兩個值的欄位
    s["K"], s["D"] = s.KD()

    # 撰寫個人策略 => def 名稱自取(今日, 今日資訊, 股票資訊)
    def golden_cross(today, today_data, stock):
        # 回傳資訊為 True = 持有狀態, False = 非持有狀態
        return today_data["K"] > today_data["D"]

    # 將策略新增至回測程式中並取名
    bt.addStrategy("KD黃金交叉", golden_cross)

    # 範例策略二
    s["MA5"] = s.MA()
    s["MA20"] = s.MA(20)

    def average_cross(today, today_data, stock):
        return today_data["MA5"] > today_data["MA20"]

    bt.addStrategy("均線黃金交叉", average_cross)

    # 範例策略三
    s["DIF"], s["DEM"], s["OSC"] = s.MACD()

    def macd_cross(today, today_data, stock):
        # 可調整today並透過stock取得其他日的資訊
        yesterday = today - 1
        yesterday_data = stock.getData(yesterday)

        return (today_data["DIF"] > today_data["DEM"]) & (
            yesterday_data["DIF"] > yesterday_data["DEM"]
        )

    bt.addStrategy("MACD連續兩日黃金交叉", macd_cross)

    # 繪製回測結果 (縱軸為資產倍率)
    bt.plot()

    show()
