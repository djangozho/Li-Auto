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

# 定义数据库连接信息
db_username = 'develop'
db_password = 'Dev&168!'
db_port = '3306'
# db_hostname = '172.24.139.117'
# db_name = 'zlaq_gd_ana'


db_name = 'zlaq_prod'
db_hostname = '172.24.139.206'

# 创建数据库连接字符串
db_connection_str = f'mysql+pymysql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}'

# 创建数据库连接引擎
engine = create_engine(db_connection_str)
inspector = Inspector.from_engine(engine)
tables = inspector.get_table_names()

assert 3>4 
### 索赔单

claims_sql = '''
select * from
(select claim_guarantee_code,vin,guarantee_amount,
delivery_time,fault_time,tech_code,
driving_mileage,
damage_material_code,damage_material_name,guarantee_type,material_total_amount,
vehicle_category_code,LEFT(vehicle_category_code,3) as vehicle_cate_merge,
usage_type_name
 from dwd_aftersale_claim_guarantee_order_df
where 1=1 
    and damage_material_code = 'X03-29150052'
    -- and guarantee_type = 10
) raw
where 1=1 
and vehicle_cate_merge = 'X03'
'''


# claims_raw = pd.read_sql(text(claims_sql), engine)
claims_raw = pd.read_clipboard()

# claims_raw = claims_raw.dropna()
# https://li.feishu.cn/sheets/BN8WsSkMyhE6dzt5gVjcJ8pinDb?sheet=8O672n

###里程
mils_query = '''
select vin,total_odometer from dm_vom_drive_total_sum_df 
'''
# dm_vom_adas_total_odometer  
# dm_vom_drive_total_sum_df


mils_raw = pd.read_sql(mils_query, engine)


###车辆
vehicle_query = '''
select vin,vehicle_series_category_code,vehicle_model_name,factory_name,year_size,
left(actual_product_finish_time,10) as product_date, left(product_delivery_time,10) as delivery_date,ad_platform_name
from dim_pro_prod_vehicle_base_info_df 
where 1=1 
and product_delivery_time is not null
-- and actual_product_finish_time >= '2023-10-01 00:00:00'
-- and actual_product_finish_time <= '2024-03-03 00:59:59'
and vehicle_series_category_code in ('X01','X02')
'''
vehicle_raw = pd.read_sql(vehicle_query, engine)
# vehicle_raw = pd.read_csv(os.path.join(r'D:\代码项目\WEIBULL\数据源','weiling_accm.csv'))
len(vehicle_raw)
# vehicle_raw = pd.read_excel(os.path.join(r'D:\代码项目\WEIBULL\数据源','四通阀问题精确追溯.xlsx'))
assert 3>4
claims = claims_raw.copy()
vehicle = vehicle_raw.copy()

vehicle = vehicle.merge(mils_raw,on='vin')
# ['vin_use', 'vehicle_series_category_code', 'vehicle_category_code', 'vehicle_model_name', 'ticket_create_time', 'product_date', 'delivery_date', 'year_size', 'retail_store_province_name',
#        'total_travel_mileage', 'extracted_value', 'part_code', 'part_barcode', 'mil_1000', 'accum_total_mileage']

# claims = claims.loc[claims['guarantee_type']==10]
claims['vin'] = claims['VIN']
claims['total_odometer'] = claims['故障里程']





failure_data = claims.loc[claims.vin.isin(vehicle.vin)]
failure_data['total_odometer'].hist(bins=20)
failure_data.sort_values('total_odometer',inplace=True)
failure_data.drop_duplicates('vin',keep='first',inplace=True)
# .loc[claims['ad_platform_name']=='AD MAX']
risk_data = vehicle

vehicle['total_odometer'].hist(bins=20)


print(len(failure_data),len(risk_data))


new_rate = len(failure_data.loc[failure_data['total_odometer']<=1000])/len(risk_data)

failure_data.total_odometer.hist(bins=20)
risk_data.use_days.hist(bins=20)
output = F.Fit_Weibull_2P(
        failure_data.loc[failure_data['total_odometer']>1000,'total_odometer'].tolist(),
        right_censored = risk_data.loc[~risk_data.vin.isin(failure_data.vin)]['total_odometer'].tolist(),
        CI_type='reliability')

assert 3>4
# new_rate = 0
out = pd.DataFrame()
out['total_odometer'] = [10000*i for i in range(1,11)]
# out['使用天数'] = [30 *(i+1)for i in range(96)]

out['平均(%)'] = out['total_odometer'].apply(lambda x : (1 - output.distribution.SF(x))*100) +new_rate*100
out['95%上限(%)']=  out['total_odometer'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[-1]*100) +new_rate*100
out['95%下限(%)']=  out['total_odometer'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[0]*100) +new_rate*100

out.to_clipboard(index=False)

miles = 100000
use = out.loc[out['total_odometer'] == miles]

rate_ = use.values.reshape(-1)[2:]
num_ = len(risk_data) * rate_/100 
print(f"{miles}公里故障率在{min(rate_) :.4f}%到{max(rate_) :.4f}%之间，估计损失件在{min(num_) :.0f}到{max(num_) :.0f}之间。更高里程数据缺乏证据，仅作为参考。")










assert 3>4

risk_data = pd.read_clipboard() 
# 32028
# https://li.feishu.cn/sheets/IZp0sTKC5hshcatRJ6zc0fd7n3b
vehicle_raw['vin'] = vehicle_raw['vin_use']
risk_data = risk_data.merge(vehicle_raw,on='vin',how='inner')

# 29478
misscar = 1 - 29478/32028


risk_data['use_days'] = pd.to_datetime('2024-11-26') - pd.to_datetime(risk_data['delivery_date'])
risk_data['use_days'] = risk_data['use_days'].dt.days


(risk_data['use_days']//30).value_counts().to_clipboard()

