from Models import NN, DR, TM
from Helper import helper

import pandas as pd
import datetime
import time
import numpy as np
import json


class LoadPred(object):

    def __init__(self, dataframe):
        self.data = dataframe.copy()
        self.NN = NN.NN(self.data)
        self.DR = DR.DR(self.data)
        self.TM = TM.TM(self.data)
        self.models = [self.NN, self.DR, self.TM]

    def create_validation_df(self):
        self.validation_df = helper.validation_dataframe_cleaning(self.data)

    def model_building(self, date):
        self.date = date
        self.MAPE = []
        self.RMSE = []
        exclude_model = [self.NN.name]
        # exclude_model = [self.NN.name, self.TM.name]
        for model in self.models:
            print(f'-----------------------Running {model.name}-----------------------')
            print(f'Date is {date}')
            if model.name in exclude_model:
                self.MAPE.append(float('inf'))
                self.RMSE.append(float('inf'))
                print(f'-----------------------{model.name} Complete-----------------------')
                continue
            start = time.time()
            model.set_date(date)
            model.model_selection_mape_rmse()
            model.predict_next_40hours()
            self.MAPE.append(model.mape)
            self.RMSE.append(model.rmse)
            end = time.time()
            print(f'-----------------------{model.name} Complete-----------------------')
            print(f'Status report: using {end - start} seconds')
            print('************************************************************************************')

    def ensemble_models(self):
        index = self.MAPE.index(min(self.MAPE))
        self.model = self.models[index]

    def return_result(self):
        self.forecast = self.model.predict_next_40hours()
        return self.forecast

    def get_error(self):
        start = pd.to_datetime(self.date) + datetime.timedelta(hours=8)
        end = pd.to_datetime(self.date) + datetime.timedelta(hours=47)
        validation_list = self.validation_df[start:end]['Load'].tolist()
        predict = self.forecast
        res = predict
        print(f'predict result: \n {predict}')
        self.this_mape = helper.mape(validation_list, res)
        self.this_rmse = helper.rmse(validation_list, res)
        print(f'satrt time: {start}, end time: {end}')
        print(f'future mape: {self.this_mape}')
        print(f'future rmse: {self.this_rmse}')

    def peakhour(self):
        start = pd.to_datetime(self.date) + datetime.timedelta(hours=8)
        end = pd.to_datetime(self.date) + datetime.timedelta(hours=47)
        validation_list = self.validation_df[start:end]['Load'].tolist()
        predict = self.forecast
        validation_list = validation_list[-24:]
        predict = predict[-24:]
        validation_peak_index = validation_list.index(max(validation_list))
        predict_peak_index = predict.index(max(predict))
        if validation_peak_index == predict_peak_index:
            self.peak_detected = 1
            return 1
        else:
            self.peak_detected = 0
            return 0


def main(data, date, length):
    LP = LoadPred(data)
    results_dict = dict()
    datelist = list(map(str, pd.date_range(pd.to_datetime(date), periods=length).tolist()))
    for date in datelist:
        print('####################################################################################################')
        print(f'Making prediction for {date}')

        results_dict[date] = dict()
        results_dict[date]['error'] = dict()

        start = time.time()

        LP.model_building(date)
        LP.create_validation_df()
        LP.ensemble_models()
        LP.return_result()
        LP.get_error()
        LP.peakhour()

        results_dict[date]['prediction'] = LP.forecast
        results_dict[date]['error']['MAPE'] = LP.this_mape
        results_dict[date]['error']['RMSE'] = LP.this_rmse
        results_dict[date]['peak_detected'] = LP.peak_detected

        print(f'peak hour: {LP.peak_detected}')
        end = time.time()
        print(f'used {end - start}')
        results_dict[date]['time'] = end - start
        print('####################################################################################################')
    with open('predicted_results_2018Q4.json', 'w') as f:
        json.dump(results_dict, f)
    print('Results file generated')


if __name__ == '__main__':
    path = 'Data/Hourly_Temp_Humi_Load-7.csv'
    df = pd.read_csv(path)
    main(df, '2018-10-01', 92)
