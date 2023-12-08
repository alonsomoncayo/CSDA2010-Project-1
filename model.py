import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX

om3_order = (1,0,0)
om3_seasonal_order = (1,1,1,12)

def fit_model_forecast(df,df_temp):
    pred = df_temp[(df_temp.index > datetime(2023, 8, 1)) & (df_temp.index < datetime(2023, 12, 1))]
    df_forcast_2023 = pd.concat([pred,pd.DataFrame(df_temp[df_temp.index == datetime(2022, 12, 1)].iat[0, 0],columns=['Mean Temp'],index=[datetime(2023, 12, 1)])])
    
    ind = pd.date_range(start='2024-01-01', end='2024-12-01', freq='MS')
    df_forcast_2024 = pd.DataFrame(df_temp[(df_temp.index >= datetime(2022, 1, 1)) & (df_temp.index <= datetime(2022, 12, 1))]).reset_index(drop=True)
    df_forcast_2024.index = ind
    
    df_forecast = pd.concat([df_forcast_2023,df_forcast_2024])
    
    df_copy = df.set_index('Date').copy()
    
    comp_model = SARIMAX(df_copy['Residential'], exog=df_copy['Mean Temp'], order=om3_order, seasonal_order = om3_seasonal_order, trend='c')
    comp_model_fit = comp_model.fit()
    forecast = comp_model_fit.forecast(steps=16, exog=df_forecast['Mean Temp'])
    forecast=pd.DataFrame(forecast).reset_index()
    return  comp_model_fit, forecast, pd.DataFrame(df_forecast).reset_index()