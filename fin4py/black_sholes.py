# Reference: https://www.macroption.com/black-scholes-formula
# Reference: https://stackoverflow.com/questions/61289020/fast-implied-volatility-calculation-in-python

# CP: call=True, put=False
# S:  underlying price
# K:  strike price
# T:  time to expiration (% of year)
# R:  risk-free interest rate (% p.a.)
# V:  volatility (% p.a.)
# SP: spot price of option

import datetime
import logging
from math import sqrt, log, fabs, exp


RFR = 2.70
DEFAULT_IV = 0.25
DAYOFYEAR = 1.0 / 365.0
RSQRT2PI = 0.39894228040143267793994605993438
PRECISION = 1.0e-5
MAX_ITERATIONS = 200


def nd(d):
    return exp(-0.5 * d * d) * RSQRT2PI


def cnd(d):
    A1 = 0.31938153
    A2 = -0.356563782
    A3 = 1.781477937
    A4 = -1.821255978
    A5 = 1.330274429
    K = 1.0 / (1.0 + 0.2316419 * fabs(d))
    ret_val = (
        RSQRT2PI
        * exp(-0.5 * d * d)
        * (K * (A1 + K * (A2 + K * (A3 + K * (A4 + K * A5)))))
    )
    if d > 0:
        ret_val = 1.0 - ret_val
    return ret_val


def bs_price(CP, S, K, T, R, V):
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (R + 0.5 * V * V) * T) / (V * sqrtT)
    d2 = d1 - V * sqrtT
    cndd1 = cnd(d1)
    cndd2 = cnd(d2)
    expRT = exp((-1.0 * R) * T)

    if CP:
        return S * cndd1 - K * expRT * cndd2
    else:
        return K * expRT * (1.0 - cndd2) - S * (1.0 - cndd1)


def bs_delta(CP, S, K, T, R, V):
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (R + 0.5 * V * V) * T) / (V * sqrtT)
    cndd1 = cnd(d1)
    expRT = exp((-1.0 * R) * T)

    if CP:
        return expRT * cndd1
    else:
        return expRT * (cndd1 - 1.0)


def bs_theta(CP, S, K, T, R, V):
    sqrtT = sqrt(T)
    rsqrtT = 1.0 / sqrtT
    d1 = (log(S / K) + (R + 0.5 * V * V) * T) * rsqrtT / V
    d2 = d1 - V * sqrtT
    ndd1 = nd(d1)
    cndd1 = cnd(d1)
    cndd2 = cnd(d2)
    expRT = exp((-1.0 * R) * T)

    if CP:
        return (
            -S * V * expRT * ndd1 * 0.5 * rsqrtT
            - R * K * expRT * cndd2
            + R * S * expRT * cndd1
        ) * DAYOFYEAR
    else:
        return (
            -S * V * expRT * ndd1 * 0.5 * rsqrtT
            + R * K * expRT * (1.0 - cndd2)
            - R * S * expRT * (1.0 - cndd1)
        ) * DAYOFYEAR


def bs_vega(S, K, T, R, V):
    sqrtT = sqrt(T)
    d1 = (log(S / K) + (R + 0.5 * V * V) * T) / (V * sqrtT)
    ndd1 = nd(d1)
    expRT = exp((-1.0 * R) * T)
    return S * expRT * sqrtT * ndd1


def bs_iv(CP, S, K, T, R, SP):
    iv = 0.5
    for i in range(MAX_ITERATIONS):
        price = bs_price(CP, S, K, T, R, iv)
        vega = bs_vega(S, K, T, R, iv)
        d = SP - price
        if abs(d) < PRECISION:
            return iv if iv < 10.0 else 0.0
        iv = iv + (d / vega)
    return iv if iv < 10.0 else 0.0


class BlackScholesPricingEngine:
    def __init__(
        self,
        is_call: bool,
        strike: float,
        today: datetime.datetime.date,
        maturity: datetime.datetime.date,
        iv: float = DEFAULT_IV,
    ):
        self._is_call = is_call
        self._strike = float(strike)
        self._time_remain = float((maturity - today).days / 365.0)
        self._iv = float(iv)

    def price(self, ul_price: float) -> float:
        price = bs_price(
            self._is_call,
            float(ul_price),
            self._strike,
            self._time_remain,
            RFR,
            self._iv,
        )
        return float(price)

    def delta(self, ul_price: float) -> float:
        delta = bs_delta(
            self._is_call,
            float(ul_price),
            self._strike,
            self._time_remain,
            RFR,
            self._iv,
        )
        return float(delta)

    def theta(self, ul_price: float) -> float:
        theta = bs_theta(
            self._is_call,
            float(ul_price),
            self._strike,
            self._time_remain,
            RFR,
            self._iv,
        )
        return float(theta)

    def update_iv(self, ul_price: float, option_spot_price: float) -> float:
        try:
            iv = bs_iv(
                self._is_call,
                float(ul_price),
                self._strike,
                self._time_remain,
                RFR,
                float(option_spot_price),
            )
            self._iv = float(iv)
            return self._iv
        except ZeroDivisionError as e:
            logging.warning(
                f"{e} with ul_price({ul_price}) option_spot_price({option_spot_price})"
            )
            self._iv = 0.0
            return self._iv
