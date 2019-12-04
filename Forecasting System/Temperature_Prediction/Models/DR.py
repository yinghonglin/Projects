import pandas as pd
import numpy as np
import holidays
import statsmodels.formula.api as sm
import time
from Helper import helper
import datetime


class DR(object):

    def __init__(self, dataframe):
        df = dataframe.copy()
        self.lm_data = helper.DR_Temp_data_cleaning(df)
        self.name = 'DR'

    def set_date(self, date):
        self.date = date

    def model_building(self, training_data, station):
        ml = sm.ols(formula=station + "_Temp_Log~Load_Lag_48+Humi_Lag_48+I(Load_Lag_48**2)+I(Humi_Lag_48**2)+\
                                           Hour+Weekday+Month+Holiday+ RIV_Temp_Log_Lag_48+I(RIV_Temp_Log_Lag_48**2)+\
                                               Month:Load_Lag_48+Month:Humi_Lag_48+\
                                               Hour:Load_Lag_48+Hour:Humi_Lag_48+\
                                               Holiday:Load_Lag_48+Holiday:Humi_Lag_48", data=training_data).fit()
        return ml

    def model_selection_mape_rmse(self, station):
        training_days = 30

        date_time = pd.to_datetime(self.date) + datetime.timedelta(hours=7)
        test_start_date = date_time - datetime.timedelta(days=training_days + 1)
        train_end_date = test_start_date - datetime.timedelta(hours=8)
        test_end_date = date_time - datetime.timedelta(hours=8)

        forecast = []
        x_test = []
        this_date = test_start_date
        for counter in range(training_days):
            train_end_date = this_date
            # print(train_end_date)
            Y_start, Y_end = this_date + datetime.timedelta(hours=1), this_date + datetime.timedelta(hours=40)

            start = time.time()

            x_train = self.lm_data['2014-01-03 01:00':str(train_end_date)]

            ml = self.model_building(x_train, station)
            test = self.lm_data[str(Y_start):str(Y_end)]
            p = ml.predict(test)
            p = pd.DataFrame(p)
            forecast.append(np.array(np.exp(p[0])))
            x_test.append(np.array(test[station + '_Temp']))

            end = time.time()
            this_date = this_date + datetime.timedelta(hours=24)

        result_mape = []
        result_rmse = []
        for index in range(len(forecast)):
            result_mape.append(helper.mape(np.array(x_test[index]), np.array(forecast[index])))
            result_rmse.append(helper.rmse(np.array(x_test[index]), np.array(forecast[index])))

        self.mape = np.mean(result_mape)
        self.rmse = np.mean(result_rmse)

        return self.mape, self.rmse

    def predict_next_40hours_temp(self, station):
        today = pd.to_datetime(self.date) + datetime.timedelta(hours=7)

        train_end_date = today - datetime.timedelta(hours=1)

        x_train = self.lm_data['2014-01-03 01:00':str(train_end_date)]

        # print('building the latest model')
        ml = self.model_building(x_train, station)
        # print('building process complete')

        Y_start, Y_end = today + datetime.timedelta(hours=1), today + datetime.timedelta(hours=40)
        # print(f'Y_start {Y_start}, Y_end: {Y_end}')
        X = self.lm_data[str(Y_start):str(Y_end)]
        p = ml.predict(X)
        p = pd.DataFrame(p)
        p = np.exp(p[0])
        # print('with time stamp: ', p)
        self.forecast = p.tolist()
        return self.forecast


if __name__ == '__main__':
    path = '../../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)
    model_DR = DR(df)
    model_DR.set_date('2018-11-04')
    station = 'TRM'
    model_DR.model_selection_mape_rmse(station)
    print(f'MAPE: {model_DR.mape}, RMSE: {model_DR.rmse}')
    model_DR.predict_next_40hours_temp(station)
    print(model_DR.forecast)
