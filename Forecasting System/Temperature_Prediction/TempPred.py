from Temperature_Prediction.Models.DR import DR
from Temperature_Prediction.Models.HW import HW
import pandas as pd


class TempPred(object):

    def __init__(self, dataframe):
        self.DR = DR(dataframe)
        self.HW = HW(dataframe)
        self.models = [self.DR, self.HW]

    def model_building(self, date, station):
        self.MAPE = []
        self.RMSE = []
        excelue_model = [self.HW.name]
        for model in self.models:
            if model.name in excelue_model:
                self.MAPE.append(float('inf'))
                self.RMSE.append(float('inf'))
                continue
            model.set_date(date)
            model.model_selection_mape_rmse(station)
            self.MAPE.append(model.mape)
            self.RMSE.append(model.rmse)

    def ensemble_models(self):
        index = self.MAPE.index(min(self.MAPE))
        # print(self.MAPE)
        # print(self.MAPE)
        # print(index)
        self.model = self.models[index]
        # print(self.model.name)

    def predict_next_40hours_temp(self, station):
        self.forecast = self.model.predict_next_40hours_temp(station)
        return self.forecast


if __name__ == '__main__':
    path = '../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)
    TP = TempPred(df)
    station = 'USC'
    TP.model_building('2018-09-01', station)
    TP.ensemble_models()
    TP.predict_next_40hours_temp(station)
    print(TP.forecast)
