from datetime import timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import numpy as np

from Helper import helper


class HW(object):

    def __init__(self, dataframe):
        df = dataframe.copy()
        self.data = helper.HW_Temp_data_cleaning(df)
        self.name = 'HW'

    def set_date(self, date):
        self.date = date

    def model_building(self, training_data, station=None):
        model = ExponentialSmoothing(training_data, seasonal='add', seasonal_periods=24 * 365)
        model_fit = model.fit()
        return model_fit

    def model_selection_mape_rmse(self, station):
        datetime = pd.to_datetime(self.date) - timedelta(days=2)
        train_end = datetime + timedelta(hours=7)
        test_start = datetime + timedelta(hours=8)
        test_end = datetime + timedelta(days=1) + timedelta(hours=23)

        train = self.data[station + '_Temp'].loc[:train_end]
        test = self.data[station + '_Temp'].loc[test_start:test_end]
        model = self.model_building(train, station)
        yhat = model.forecast(40)
        # yhat.index = test.index
        # self.mape = abs((yhat - test) / test).mean()
        # self.rmse = np.sqrt(((yhat - test) ** 2).mean())
        self.mape = helper.mape(test, yhat)
        self.rmse = helper.rmse(test, yhat)

    def predict_next_40hours_temp(self, station):
        train_end2 = pd.to_datetime(self.date) + timedelta(hours=7)
        train2 = self.data[station + '_Temp'].loc[:train_end2]
        model2 = self.model_building(train2, station)
        y_predict = model2.forecast(40)
        self.forecast = y_predict.to_list()
        return self.forecast


if __name__ == '__main__':
    path = '../../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)
    model_DR = HW(df)
    model_DR.set_date('2018-09-01')
    station = 'TRM'
    model_DR.model_selection_mape_rmse(station)
    print(f'MAPE: {model_DR.mape}, RMSE: {model_DR.rmse}')
    model_DR.predict_next_40hours_temp(station)
    print(model_DR.forecast)
