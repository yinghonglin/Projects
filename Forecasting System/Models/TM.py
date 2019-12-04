from Helper import helper
from Temperature_Prediction.TempPred import TempPred

import pandas as pd
import datetime
from sklearn.ensemble import GradientBoostingRegressor
import time


class TM(object):

    def __init__(self, dataframe):
        df = dataframe.copy()
        self.data = helper.TM_Temp_data_cleaning(df)
        self.TempPred = TempPred(dataframe)
        self.name = 'Time Series and Machine Learning'

    def set_date(self, date):
        self.date = date

    def model_selection_mape_rmse(self):
        # df2 = self.data.copy()
        # date = self.date
        # x_train2, y_train, x_test2, y_test = helper.TM_split_train_test(df2, date, self.TempPred)
        # training_data = [x_train2, y_train]
        # GB = self.model_building(training_data)
        # predict_GB = GB.predict(x_test2)
        # self.mape = helper.mape(y_test, predict_GB)
        # self.rmse = helper.rmse(y_test, predict_GB)
        df2 = self.data.copy()
        date = self.date
        date_hour = pd.to_datetime(date) + datetime.timedelta(hours=7)
        test_start_date = date_hour - datetime.timedelta(days=2)
        train_end_date = test_start_date - datetime.timedelta(hours=8)
        test_end_date = date_hour - datetime.timedelta(hours=8)
        date_for_test = pd.to_datetime(date) - datetime.timedelta(days=1)

        x_train = df2[df2['new_date'] <= train_end_date].drop(columns='Load')
        x_test = df2[(df2['new_date'] > test_start_date) & (df2['new_date'] <= test_end_date)].drop(columns='Load')
        y_train = df2[df2['new_date'] <= train_end_date]['Load']
        y_test = df2[(df2['new_date'] > test_start_date) & (df2['new_date'] <= test_end_date)]['Load']

        stations = ['RIV', 'LAX', 'USC', 'WJF', 'TRM']
        for station in stations:
            # temp = TempPred('Hourly_Temp_Humi_Load-6.csv', date_for_test)
            # pred = temp.return_result(station)
            self.TempPred.model_building(date_for_test, station)
            self.TempPred.ensemble_models()
            pred = self.TempPred.predict_next_40hours_temp(station)
            # print(f'station {station}')
            # print(f'predict: {pred}')
            # print(pred)
            # print(len(pred))
            x_test[station + '_Temp'] = pred


        x_train2 = x_train.drop(columns=['Date', 'new_date'])
        x_test2 = x_test.drop(columns=['Date', 'new_date'])
        # print(x_test2.head())
        # Model Building & Prediction#
        params = {'n_estimators': 300, 'max_depth': 6, 'min_samples_split': 20, 'learning_rate': .2,
                  'loss': 'ls'}
        GB = self.model_building(None)
        GB.fit(x_train2, y_train)
        predict_GB = GB.predict(x_test2)

        # MAPE & RMSE
        self.mape = helper.mape(y_test, predict_GB)
        self.rmse = helper.rmse(y_test, predict_GB)
        pass

    def model_building(self, training_data):
        # x_train2 = training_data[0]
        # y_train = training_data[1]
        #
        # params = {'n_estimators': 300, 'max_depth': 6, 'min_samples_split': 20, 'learning_rate': .2,
        #           'loss': 'ls'}
        # GB = GradientBoostingRegressor(**params)
        # GB.fit(x_train2, y_train)
        # return GB
        params = {'n_estimators': 300, 'max_depth': 6, 'min_samples_split': 20, 'learning_rate': .2,
                  'loss': 'ls'}
        GB = GradientBoostingRegressor(**params)
        return GB

    def predict_next_40hours(self):
        date = self.date
        df2 = self.data.copy()

        date_hour = pd.to_datetime(date) + datetime.timedelta(hours=7)
        prediction_end = date_hour + datetime.timedelta(hours=40)

        # Predict Next 40 hours
        x_next40 = df2[(df2['new_date'] > date_hour) & (df2['new_date'] <= prediction_end)]
        x_next40_new = x_next40.drop(columns=['Date', 'new_date', 'Load'])

        stations = ['RIV', 'LAX', 'USC', 'WJF', 'TRM']
        for station in stations:
            self.TempPred.model_building(date, station)
            self.TempPred.ensemble_models()
            pred = self.TempPred.predict_next_40hours_temp(station)

            x_next40_new[station + '_Temp'] = pred

        x_train_new = df2[(df2['new_date'] < date_hour)].drop(columns=['Date', 'new_date', 'Load'])
        y_train_new = df2[(df2['new_date'] < date_hour)]['Load']

        GB_40 = self.model_building(None)
        GB_40.fit(x_train_new, y_train_new)
        predict_next40 = GB_40.predict(x_next40_new)
        self.forecast = list(predict_next40)

        return self.forecast


if __name__ == '__main__':
    start = time.time()
    path = '../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)

    model_TM = TM(df)
    model_TM.set_date('2018-11-05')
    model_TM.model_selection_mape_rmse()
    model_TM.predict_next_40hours()

    end = time.time()
    print(model_TM.forecast)
    print(f'mape: {model_TM.mape}, rmse: {model_TM.rmse}')
    print(f'using {end - start}')
