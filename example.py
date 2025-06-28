from fin4py import Stock
from pylab import show, plt

if __name__ == "__main__":
    # 建立股票資訊連結(股票代碼，起始時間，結束時間)
    # s = Stock('2330')
    # s = Stock('2330', '2015-10-31')
    s = Stock("2330", "2015-10-31", "2016-03-05")

    # 取得歷史股價
    print("歷史收盤價")
    print(s["Adj Close"])

    # 取得均線值(預設週期為5日)
    # ma = s.MA(5)
    ma = s.MA()
    s["MA5"] = ma

    # 取得KD值(預設週期為9日)
    # k, d = s.KD(9)
    k, d = s.KD()
    s["K"] = k
    s["D"] = d

    # 取得MACD值(預設短週期為12日，長週期為26日，DIF平滑區間為9日)
    # 詳情可至維基百科查詢 https://zh.wikipedia.org/wiki/MACD
    # dif, dem, osc = s.MACD(12, 26, 9)
    dif, dem, osc = s.MACD()
    s["DIF"] = dif
    s["DEM"] = dem
    s["OSC"] = osc

    # 取得乖離率(預設週期為10日)
    # bias = s.BIAS(10)
    bias = s.BIAS()
    s["BIAS"] = bias

    # 取得布林通道值(預設週期為20日, 通道倍率為2倍)
    # top_line, bottom_line, band_width = s.BBand(20, 2)
    top_line, bottom_line, band_width = s.BBand()
    s["BTOP"] = top_line
    s["BBOTTOM"] = bottom_line
    s["BWIDTH"] = band_width

    print("歷史股價及技術線圖表")
    print(s)

    # 繪製技術線型
    # 可指定Axes，未指定則沿用上一個使用的Axes
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True)

    # 繪製K線圖
    # s.plotOHLC()
    s.plotOHLC(ax=axes[0])

    # 繪製成交量圖(以張為單位)
    # s.plotVolume()
    s.plotVolume(ax=axes[1])

    # 繪製其他技術線圖
    # s['Close'].plot()
    # ma.plot()
    k.plot(ax=axes[2])
    d.plot(ax=axes[2])
    # dif.plot()
    # dem.plot()
    # osc.plot.bar()
    # bias.plot()
    top_line.plot(ax=axes[0])
    bottom_line.plot(ax=axes[0])

    show()
