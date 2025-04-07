import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from Data import dgp_config as dcf

# 确保缓存目录存在
os.makedirs(dcf.CACHE_DIR, exist_ok=True)

def create_fake_spy_data(freq, start_date='1990-01-01', end_date='2020-07-31'):
    """
    创建虚假的SPY数据文件

    参数:
    freq (str): 频率，可以是 'week', 'month', 或 'quarter'
    start_date (str): 开始日期
    end_date (str): 结束日期
    """
    # 转换日期为datetime对象
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    # 根据频率生成日期序列
    if freq == 'week':
        # 每周五
        dates = pd.date_range(start=start, end=end, freq='W-FRI')
    elif freq == 'month':
        # 每月最后一个工作日
        dates = pd.date_range(start=start, end=end, freq='BM')
    elif freq == 'quarter':
        # 每季度最后一个工作日
        dates = pd.date_range(start=start, end=end, freq='BQ')
    elif freq == 'year':
        # 每年最后一个工作日
        dates = pd.date_range(start=start, end=end, freq='BY')

    # 生成随机收益率数据
    np.random.seed(42)  # 设置随机种子以确保可重复性
    returns = np.random.normal(0.001, 0.02, size=len(dates))  # 均值0.1%，标准差2%

    # 创建DataFrame
    spy_df = pd.DataFrame({
        'date': dates,
        'ret': returns
    })

    # 保存为CSV
    output_path = os.path.join(dcf.CACHE_DIR, f'spy_{freq}_ret.csv')
    spy_df.to_csv(output_path, index=False)
    print(f'已创建虚假SPY {freq}频率数据文件: {output_path}')

    return spy_df


# 为所有需要的频率创建虚假数据
for freq in ['week', 'month', 'quarter', 'year']:
    create_fake_spy_data(freq)
