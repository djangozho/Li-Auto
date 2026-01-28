import pandas as pd
from sqlalchemy import create_engine,Inspector
import json
import requests
import time
import numpy as np
import matplotlib.pyplot as plt
import reliability.Fitters as F
import reliability.Distributions as D
from datetime import datetime as dt
from sqlalchemy import text
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


### 索赔单
claims_sql = '''
select * from
(select claim_guarantee_code,vin,guarantee_amount,
delivery_time,fault_time,
driving_mileage,
damage_material_code,damage_material_name,
vehicle_category_code,LEFT(vehicle_category_code,1) as vehicle_cate_merge,
usage_type_name
 from dwd_aftersale_claim_guarantee_order_df
where 1=1 
    and usage_type_name = '销售用车'
    and damage_material_code = 'M01-81030002'
) raw
where 1=1 
and vehicle_cate_merge = 'M'
'''
claims_raw = pd.read_sql(claims_sql, engine)


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
left(actual_product_finish_time,10) as product_date, left(product_delivery_time,10) as delivery_date
from dim_pro_prod_vehicle_base_info_df 
where 1=1 
and left(vehicle_series_category_code,1)  = 'M'
and product_delivery_time is not null
'''
vehicle_raw = pd.read_sql(vehicle_query, engine)


assert 3>4
claims = claims_raw.copy()
mils = mils_raw.copy()
vehicle = vehicle_raw.copy()

claims = claims.merge(vehicle[['vin','delivery_date','product_date']],how='left',on='vin')
vehicle = vehicle.merge(mils,on='vin')
vehicle['use_days'] = (pd.to_datetime('2024-07-03') - pd.to_datetime(vehicle['delivery_date'])).dt.days
vehicle['use_days'] = vehicle['use_days'].apply( lambda x: x if x > 1 else 1)
claims['use_days']= (pd.to_datetime(claims['fault_time']) - pd.to_datetime(claims['delivery_time'])).dt.days
claims['use_days'] = claims['use_days'].apply( lambda x: x if x > 1 else 1)
claims['total_odometer'] = claims['driving_mileage']
assert 3>4

left_data = claims.loc[(claims['product_date']>'2021-01-15')&(
                        claims['use_days']>800)]
right_data= vehicle.loc[(vehicle['product_date']>'2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]
output = F.Fit_Weibull_2P(
    left_data['use_days'].tolist(),
    right_censored = right_data['use_days'].tolist(),
    CI_type='reliability')
# plt.title('断点后-里程')

left_data = claims.loc[(claims['product_date']<='2021-01-15')&(
                        claims['use_days']>800)]
right_data= vehicle.loc[(vehicle['product_date']<='2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]
output = F.Fit_Weibull_2P(
    left_data['use_days'].tolist(),
    right_censored = right_data['use_days'].tolist(),
    CI_type='reliability')
# plt.title('断点后-里程')


assert 3>4
#故障件预处理

left_data = claims.loc[(claims['product_date']>'2021-01-15')&
                       (claims['total_odometer']>20000)]
right_data= vehicle.loc[(vehicle['product_date']>'2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]

output = F.Fit_Weibull_2P(
    left_data['total_odometer'].tolist(),
    right_censored = right_data['total_odometer'].tolist(),
    CI_type='reliability')
# plt.title('断点后-里程')


left_data = claims.loc[(claims['product_date']<='2021-01-15')&
                        (claims['total_odometer']>20000)]
right_data= vehicle.loc[(vehicle['product_date']<='2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]

output = F.Fit_Weibull_2P(
    left_data['total_odometer'].tolist(),
    right_censored = right_data['total_odometer'].tolist(),
    CI_type='reliability')
# plt.title('断点后-里程')

new_rate = 0
out = pd.DataFrame()
out['里程'] = [10000*i for i in range(1,16)]
# out['使用天数'] = [30 *(i+1)for i in range(96)]

out['平均(%)'] = out['里程'].apply(lambda x : (1 - output.distribution.SF(x))*100) +new_rate*100
out['95%上限(%)']=  out['里程'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[-1]*100) +new_rate*100
out['95%下限(%)']=  out['里程'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[0]*100) +new_rate*100


new_rate = 0
out = pd.DataFrame()
out['use_days'] = [100*i for i in range(1,20)]
# out['使用天数'] = [30 *(i+1)for i in range(96)]

out['平均(%)'] = out['use_days'].apply(lambda x : (1 - output.distribution.SF(x))*100) +new_rate*100
out['95%上限(%)']=  out['use_days'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[-1]*100) +new_rate*100
out['95%下限(%)']=  out['use_days'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[0]*100) +new_rate*100


left_data = claims.loc[(claims['product_date']>'2021-01-15')&(claims['use_days']>1000)]
right_data= vehicle.loc[(vehicle['product_date']>'2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]

output = F.Fit_Weibull_2P(
    left_data['use_days'].tolist(),
    right_censored = right_data['use_days'].tolist(),
    CI_type='reliability')
plt.title('断点后-使用天数')



left_data = claims.loc[(claims['product_date']<='2021-01-15')&(claims['use_days']>1000)]
right_data= vehicle.loc[(vehicle['product_date']<='2021-01-15')
                        &(~vehicle['vin'].isin(claims['vin']))]

output = F.Fit_Weibull_2P(
    left_data['use_days'].tolist(),
    right_censored = right_data['use_days'].tolist(),
    CI_type='reliability')
plt.title('断点后-使用天数')



new_rate = 0
out = pd.DataFrame()
out['使用天数'] = [200*i for i in range(1,10)]
# out['使用天数'] = [30 *(i+1)for i in range(96)]

out['平均(%)'] = out['使用天数'].apply(lambda x : (1 - output.distribution.SF(x))*100) +new_rate*100
out['95%上限(%)']=  out['使用天数'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[-1]*100) +new_rate*100
out['95%下限(%)']=  out['使用天数'].apply(lambda x : output.distribution.CDF(CI_x=[x], CI=0.95)[0]*100) +new_rate*100


5*365
# 供应商保修 3年6万， 理想汽车5年10万