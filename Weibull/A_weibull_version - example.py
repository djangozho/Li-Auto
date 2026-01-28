import pandas as pd
from sqlalchemy import create_engine,Inspector,text
import json
import requests
import time
import numpy as np
import matplotlib.pyplot as plt
import reliability.Fitters as F
import reliability.Distributions as D
from datetime import datetime as dt
from sqlalchemy import text
import os 
today = dt.today().strftime('%Y-%m-%d')

plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
today = dt.today().strftime('%Y-%m-%d')




# 读取数据

claims_raw = pd.read_excel('XXXX.xlsx') 
vehicle_raw = pd.read_excel('XXXX.xlsx')
mils_raw = pd.read_excel('XXXX.xlsx')

# 数据分析
claims = claims_raw.copy()
vehicle = vehicle_raw.copy()
vehicle = vehicle.merge(mils_raw,on='vin',how='left')

claims = claims.merge(vehicle[['vin','product_date', 'delivery_date','retail_store_province_name']],on='vin',how='left')

risk_data = vehicle.copy()
claims.sort_values(by='fault_time',inplace=True)
claims.drop_duplicates(subset=['vin'],inplace=True)

failure_data = claims.copy()

# 绘图
print(len(risk_data),len(failure_data))
risk_data['total_odometer'].hist(bins=50)
failure_data['driving_mileage'].hist(bins=50)


# weibull分布
risk_data.loc[risk_data['total_odometer']>100000,'total_odometer'] = 100000
failure_data = failure_data.loc[failure_data['driving_mileage']<100000]
output = F.Fit_Weibull_2P(
        failure_data['driving_mileage'].tolist(),
        right_censored =risk_data.loc[~(risk_data['vin'].isin(failure_data['vin'])),'total_odometer'].tolist(),
        CI_type='reliability')

new_rate = 0

out = pd.DataFrame()
out['total_odometer'] = [50000*i for i in range(1,5)]


out['平均(%)'] = out['total_odometer'].apply(lambda x : (1 - output.distribution.SF(x))*100) +new_rate*100
out['95%上限(%)']=  out['total_odometer'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[-1]*100) +new_rate*100
out['95%下限(%)']=  out['total_odometer'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[0]*100) +new_rate*100

out.to_clipboard(index=False)


# 结论生成
miles = 100000
use = out.loc[out['total_odometer'] == miles]

rate_ = use.values.reshape(-1)[2:]
num_ = len(risk_data) * rate_/100 
print(f"{miles}公里故障率在{min(rate_) :.4f}%到{max(rate_) :.4f}%之间，估计损失件在{min(num_) :.0f}到{max(num_) :.0f}之间。更高里程数据缺乏证据，仅作为参考。")


