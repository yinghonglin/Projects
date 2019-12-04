from Helper import helper

import pandas as pd
import numpy as np
import holidays
from pandas.tseries.holiday import USFederalHolidayCalendar
import datetime
import statsmodels.formula.api as sm
import time


class DR(object):

    def __init__(self, dataframe):
        df = dataframe.copy()
        self.lm_data = helper.DR_data_cleaning(df)
        self.name = 'Dynamic Regression'

    def set_date(self, date):
        self.date = date

    def model_selection_mape_rmse(self):
        date = self.date
        self.training_days = 30

        self.datetime = pd.to_datetime(date) + datetime.timedelta(hours=7)
        self.test_start_date = self.datetime - datetime.timedelta(days=self.training_days + 1)
        self.train_end_date = self.test_start_date - datetime.timedelta(hours=8)
        self.test_end_date = self.datetime - datetime.timedelta(hours=8)

        forecast = []
        x_test = []
        this_date = self.test_start_date
        for counter in range(self.training_days):
            self.train_end_date = this_date
            Y_start, Y_end = this_date + datetime.timedelta(hours=1), this_date + datetime.timedelta(hours=40)

            start = time.time()

            x_train = self.lm_data['2014-01-03 01:00':str(self.train_end_date)]

            ml = self.model_building(x_train)
            test = self.lm_data[str(Y_start):str(Y_end)]
            p = ml.predict(test)
            p = pd.DataFrame(p)
            forecast.append(np.array(np.exp(p[0])))
            x_test.append(np.array(test['Load']))

            end = time.time()
            this_date = this_date + datetime.timedelta(hours=24)

        self.result_mape = []
        self.result_rmse = []

        for index in range(len(forecast)):
            self.result_mape.append(helper.mape(np.array(x_test[index]), np.array(forecast[index])))
            self.result_rmse.append(helper.rmse(np.array(x_test[index]), np.array(forecast[index])))

        self.mape = np.mean(self.result_mape)
        self.rmse = np.mean(self.result_rmse)

        return self.mape, self.rmse

    def model_building(self, training_data):
        ml = sm.ols(formula="Load_Log~Temp_Lag_48+Humi_Lag_48+I(Temp_Lag_48**2)+I(Humi_Lag_48**2)+\
                                   Hour+Weekday+Month+Holiday+\
                                       Month:Temp_Lag_48+Month:Humi_Lag_48+\
                                       Hour:Temp_Lag_48+Hour:Humi_Lag_48+\
                                       Holiday:Temp_Lag_48+Holiday:Humi_Lag_48", data=training_data).fit()
        return ml

    def predict_next_40hours(self):
        today = self.datetime

        self.train_end_date = self.datetime - datetime.timedelta(hours=1)

        x_train = self.lm_data['2014-01-03 01:00':str(self.train_end_date)]

        print('building the latest model')
        ml = self.model_building(x_train)
        print('building process complete')

        Y_start, Y_end = today + datetime.timedelta(hours=1), today + datetime.timedelta(hours=40)
        X = self.lm_data[str(Y_start):str(Y_end)]
        p = ml.predict(X)
        p = pd.DataFrame(p)
        p = np.exp(p[0])
        self.forecast = p.tolist()
        return self.forecast


if __name__ == '__main__':
    path = '../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)

    model_DR = DR(df)
    model_DR.set_date('2018-07-15')
    model_DR.model_selection_mape_rmse()
    model_DR.predict_next_40hours()

    print(f'mape: {model_DR.mape}, rmse: {model_DR.rmse}')

    print(model_DR.forecast)
