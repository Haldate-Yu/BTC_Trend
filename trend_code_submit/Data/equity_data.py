from __future__ import print_function, division
import os
import os.path as op
import numpy as np
import pandas as pd
import time
from Data import dgp_config as dcf


def get_processed_US_data_by_year(year):
    df = processed_US_data()
    df = df[
        df.index.get_level_values("Date").year.isin([year, year - 1, year - 2])
    ].copy()
    return df


def get_spy_freq_rets(freq):
    assert freq in ["week", "month", "quarter", "year"]
    spy = pd.read_csv(
        os.path.join(dcf.CACHE_DIR, f"spy_{freq}_ret.csv"),
        parse_dates=["date"],
    )
    spy.rename(columns={"date": "Date"}, inplace=True)
    spy = spy.set_index("Date")
    return spy


def get_period_end_dates(period):
    assert period in ["week", "month", "quarter", "year"]
    spy = get_spy_freq_rets(period)
    return spy.index


def processed_US_data():
    processed_us_data_path = op.join(dcf.PROCESSED_DATA_DIR, "us_ret.feather")
    if op.exists(processed_us_data_path):
        print(f"Loading processed data from {processed_us_data_path}")
        since = time.time()
        df = pd.read_feather(processed_us_data_path)
        df.set_index(["Date", "StockID"], inplace=True)
        df.sort_index(inplace=True)
        print(f"Finish loading processed data in {(time.time() - since) / 60:.2f} min")
        return df.copy()
    # here to set dataset
    raw_us_data_path = op.join(dcf.RAW_DATA_DIR, "BTC-USD.csv")
    print("Reading raw data from {}".format(raw_us_data_path))
    since = time.time()
    df = pd.read_csv(
        raw_us_data_path,
        parse_dates=["Date"],
        dtype={
            "StockID": str,
            "Low": np.float64,
            "High": np.float64,
            "Close": np.float64,
            "Vol": np.float64,
            "Open": np.float64,
            "Ret": object,
        },

        header=0,
    )
    print(f"finish reading data in {(time.time() - since) / 60:.2f} s")
    df = process_raw_data_helper(df)

    df.reset_index().to_feather(processed_us_data_path)
    return df.copy()


def process_raw_data_helper(df):
    df.StockID = df.StockID.astype(str)
    df.Ret = df.Ret.astype(str)
    df = df.replace(
        {
            "Close": {0: np.nan},
            "Open": {0: np.nan},
            "High": {0: np.nan},
            "Low": {0: np.nan},
            "Ret": {"C": np.nan, "B": np.nan, "A": np.nan, ".": np.nan},
            "Volume": {0: np.nan, (-99): np.nan},
        }
    )
    if "Shares" not in df.columns:
        df["Shares"] = 0
    df["Ret"] = df.Ret.astype(np.float64)
    df = df.dropna(subset=["Ret"])
    df[["Close", "Open", "High", "Low", "Vol", "Shares"]] = df[
        ["Close", "Open", "High", "Low", "Vol", "Shares"]
    ].abs()
    df["MarketCap"] = np.abs(df["Close"] * df["Shares"])
    df.set_index(["Date", "StockID"], inplace=True)
    df.sort_index(inplace=True)
    df["log_ret"] = np.log(1 + df.Ret)
    df["cum_log_ret"] = df.groupby("StockID")["log_ret"].cumsum(skipna=True)
    df["EWMA_vol"] = df.groupby("StockID")["Ret"].transform(
        lambda x: (x**2).ewm(alpha=0.05).mean().shift(periods=1)
    )
    for freq in ["week", "month", "quarter", "year"]:
        period_end_dates = get_period_end_dates(freq)
        freq_df = df[df.index.get_level_values("Date").isin(period_end_dates)].copy()
        freq_df["freq_ret"] = np.exp(freq_df.groupby("StockID")["cum_log_ret"].transform(lambda x: x.shift(-1) - x)) - 1
        print(
            f"Freq: {freq}: {len(freq_df)}/{len(df)} preriod_end_dates from \
                        {period_end_dates[0]}, {period_end_dates[1]},  to {period_end_dates[-1]}"
        )
        df[f"Ret_{freq}"] = freq_df["freq_ret"]
        num_nan = np.sum(pd.isna(df[f"Ret_{freq}"]))
        print(f"df Ret_{freq} {len(df) - num_nan}/{len(df)} not nan")
    for i in [5, 20, 60, 65, 180, 250, 260]:
        print(f"Calculating {i}d return")
        df[f"Ret_{i}d"] = np.exp(df.groupby("StockID")["cum_log_ret"].transform(lambda x: x.shift(-i) - x)) - 1
    return df


def get_period_ret(period, country="USA"):
    assert country == "USA"
    assert period in ["week", "month", "quarter"]
    period_ret_path = op.join(dcf.CACHE_DIR, f"us_{period}_ret.pq")
    period_ret = pd.read_parquet(period_ret_path)
    period_ret.set_index(["Date", "StockID"], inplace=True)
    period_ret.sort_index(inplace=True)
    return period_ret
