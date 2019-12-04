import pandas as pd
import datetime
import os
import time
import tensorflow as tf
import numpy as np

from Helper import helper

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

tensorflow_version = tf.__version__

if int(tensorflow_version.split('.')[0]) <= 1:
    raise RuntimeError('Version Error, need to be greater than 1')


def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    dataset = tf.data.Dataset.from_tensor_slices(series)
    dataset = dataset.window(window_size, shift=24, drop_remainder=True)
    dataset = dataset.flat_map(lambda window: window.batch(window_size))
    dataset = dataset.shuffle(shuffle_buffer).map(lambda window: (window[:-40], window[-40:]))
    dataset = dataset.batch(batch_size).prefetch(1)
    return dataset


class NN(object):

    def __init__(self, dataframe):
        df = dataframe.copy()
        self.data = helper.NN_Temp_data_cleaning(df)
        self.name = 'Neural Network'
        self.window_size = 337 + 40
        self.batch_size = 30
        self.shuffle_buffer_size = 30

    def set_date(self, date):
        self.date = date

    def model_selection_mape_rmse(self):
        date = self.date
        # self.station = station

        self.training_days = 1

        self.datetime = pd.to_datetime(date) + datetime.timedelta(hours=7)
        self.test_start_date = self.datetime - datetime.timedelta(days=self.training_days + 1)
        self.train_end_date = self.test_start_date - datetime.timedelta(hours=8)
        self.test_end_date = self.datetime - datetime.timedelta(hours=8)

        # print(self.temp['2014-01-01 07:00':str(self.train_end_date)])

        x_train = self.data['2014-01-01 07:00':str(self.train_end_date)]['Load'].tolist()
        self.dataset = windowed_dataset(x_train, self.window_size, self.batch_size, self.shuffle_buffer_size)
        series = np.array(self.data[str(self.test_start_date):str(self.test_end_date)]['Load'].tolist())

        this_date = self.test_start_date
        forecast = []
        x_test = []
        for counter in range(self.training_days):
            print('days', counter + 1)
            start = time.time()
            self.train_end_date = this_date - datetime.timedelta(hours=8)
            x_train = self.data['2014-01-01 07:00':str(self.train_end_date)]['Load'].tolist()

            self.dataset = windowed_dataset(x_train, self.window_size, self.batch_size, self.shuffle_buffer_size)

            X_start, X_end = this_date - datetime.timedelta(days=14), this_date
            Y_start, Y_end = this_date + datetime.timedelta(hours=1), this_date + datetime.timedelta(hours=40)
            series = np.array(self.data[str(X_start):str(Y_end)]['Load'].tolist())

            print('now', this_date)

            print('train time', '2014-01-01 07:00', str(self.train_end_date))

            print('predict', Y_start, Y_end)

            self.model_building(None)

            forecast.append(self.model.predict(series[0:0 + self.window_size - 40][np.newaxis]))
            x_test.append(series[0 + self.window_size - 40:0 + self.window_size])
            this_date = this_date + datetime.timedelta(hours=24)
            print('mape', helper.mape(np.array(x_test[-1]), np.array(forecast[-1][0])))
            print('rmse', helper.rmse(np.array(x_test[-1]), np.array(forecast[-1][0])))
            end = time.time()
            print('using', end - start)

        # for time in range(0, len(series) - self.window_size, 24):
        #     forecast.append(self.model.predict(series[time:time + self.window_size - 40][np.newaxis]))
        #     x_test.append(series[time + self.window_size - 40:time + self.window_size])
        #
        self.result_mape = []
        self.result_rmse = []

        for index in range(len(forecast)):
            self.result_mape.append(helper.mape(np.array(x_test[index]), np.array(forecast[index][0])))
            self.result_rmse.append(helper.rmse(np.array(x_test[index]), np.array(forecast[index][0])))

        self.mape = np.mean(self.result_mape)
        self.rmse = np.mean(self.result_rmse)

        return self.mape, self.rmse

    def model_building(self, training_data):
        l0 = tf.keras.layers.Dense(100)
        # l0_5 = tf.keras.layers.Dense(70)
        l1 = tf.keras.layers.Dense(40)
        self.model = tf.keras.models.Sequential([l0, l1])
        # self.model = tf.keras.models.Sequential([l0, l0_5, l1])
        # self.model = tf.keras.models.Sequential([l1])
        # l0 = tf.keras.layers.Dense(40)
        # self.model = tf.keras.models.Sequential([l0])

        self.model.compile(loss='mean_absolute_percentage_error',
                           optimizer=tf.keras.optimizers.SGD(lr=1e-5, momentum=0.9))
        # self.model.compile(loss='mean_absolute_percentage_error',
        #                    optimizer=tf.keras.optimizers.Adam(lr=1e-6))
        self.model.fit(self.dataset, epochs=30, verbose=0)

    def predict_next_40hours(self):
        today = self.date

        self.train_end_date = self.datetime - datetime.timedelta(hours=8)

        x_train = self.data['2014-01-01 07:00':str(self.train_end_date)]['Load'].tolist()

        self.dataset = windowed_dataset(x_train, self.window_size, self.batch_size, self.shuffle_buffer_size)

        print('building the latest model')
        self.model_building(None)
        print('building process complete')
        X_start = today - datetime.timedelta(days=14)
        X_end = today
        X = np.array(self.data[str(X_start):str(X_end)]['Load'].tolist())

        self.forecast = self.model.predict(X[np.newaxis])
        return self.forecast


if __name__ == '__main__':
    path = '../Data/Hourly_Temp_Humi_Load-6.csv'
    df = pd.read_csv(path)

    model_NN = NN(df)
    model_NN.set_date('2018-02-15')
    model_NN.model_selection_mape_rmse()
    model_NN.predict_next_40hours()

    print(f'mape: {model_NN.mape}, rmse: {model_NN.rmse}')

    print(model_NN.forecast)
