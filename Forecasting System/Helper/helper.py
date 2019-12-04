import numpy as np
from pandas.tseries.holiday import USFederalHolidayCalendar
import datetime
import pandas as pd


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def rmse(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def DR_Temp_data_cleaning(dataframe):
    '''
        inplace change of the dataframe, for the structure purpose, return this dataframe
    '''
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    test = dataframe[
        ['Date', 'Hour', 'Weekday', 'Month', 'Load', 'Mean_Temp', 'Mean_Humi', 'RIV_Temp', 'RIV_Humi', 'LAX_Temp',
         'LAX_Humi', 'USC_Temp', 'USC_Humi', 'WJF_Temp', 'WJF_Humi', 'TRM_Temp', 'TRM_Humi']]

    test.loc[:, 'RIV_Temp_Log'] = np.log(dataframe['RIV_Temp'])
    test.loc[:, 'LAX_Temp_Log'] = np.log(dataframe['LAX_Temp'])
    test.loc[:, 'USC_Temp_Log'] = np.log(dataframe['USC_Temp'])
    test.loc[:, 'WJF_Temp_Log'] = np.log(dataframe['WJF_Temp'])
    test.loc[:, 'TRM_Temp_Log'] = np.log(dataframe['TRM_Temp'])

    test.loc[:, 'Load_Log'] = np.log(dataframe['Load'])
    test['Load_Lag_48'] = test['Load_Log'].shift(48, axis=0)
    test['Humi_Lag_48'] = test['Mean_Humi'].shift(48, axis=0)

    test['RIV_Temp_Log_Lag_48'] = test['RIV_Temp_Log'].shift(48, axis=0)
    test['LAX_Temp_Log_Lag_48'] = test['LAX_Temp_Log'].shift(48, axis=0)
    test['USC_Temp_Log_Lag_48'] = test['USC_Temp_Log'].shift(48, axis=0)
    test['WJF_Temp_Log_Lag_48'] = test['WJF_Temp_Log'].shift(48, axis=0)
    test['TRM_Temp_Log_Lag_48'] = test['TRM_Temp_Log'].shift(48, axis=0)

    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2014-01-01', end=str(datetime.datetime.now()), return_name=True)
    holidays = pd.DataFrame(holidays)
    holidays = holidays.reset_index()
    holidays = holidays.rename(columns={'index': "Date", 0: 'Holiday'})
    holidays['Date'] = pd.to_datetime(holidays['Date'])
    test['Date'] = pd.to_datetime(test['Date'])
    lm_data = test.loc[49:len(test), ].merge(holidays, how='left', on='Date')
    lm_data['Holiday'] = lm_data['Holiday'].fillna("Not Holiday")
    lm_data[["Hour", "Weekday", "Month", "Holiday"]] = lm_data[["Hour", "Weekday", "Month", "Holiday"]].astype(
        'category')
    DateTime = pd.DataFrame(
        lm_data.apply(lambda line: pd.to_datetime(line['Date']) + datetime.timedelta(hours=line['Hour']), axis=1))
    DateTime.columns = ['DateTime']
    lm_data = pd.concat([DateTime, lm_data], axis=1)
    lm_data.set_index('DateTime', inplace=True)

    return lm_data


def HW_Temp_data_cleaning(dataframe):
    DateTime = pd.DataFrame(
        dataframe.apply(lambda line: pd.to_datetime(line['Date']) + datetime.timedelta(hours=line['Hour']), axis=1))
    DateTime.columns = ['DateTime']
    temp = pd.concat(
        [DateTime, dataframe.iloc[:, 2], dataframe.loc[:, dataframe.columns.str.contains("Temp")]], axis=1)
    temp.set_index('DateTime', inplace=True)
    return temp


def TM_Temp_data_cleaning(dataframe):
    df = dataframe[
        ['Date', 'Hour', 'Load', 'RIV_Temp', 'LAX_Temp', 'USC_Temp', 'WJF_Temp', 'TRM_Temp', 'Weekday', 'Month']]
    df['Date'] = pd.to_datetime(df['Date'])
    df['new_date'] = df.apply(lambda a: a['Date'] + datetime.timedelta(hours=int(a['Hour'])), axis=1)

    Weekday_Dummies = pd.get_dummies(df['Weekday'])
    Month_Dummies = pd.get_dummies(df['Month'])
    df2 = pd.concat([df.drop(columns=['Weekday', 'Month']), Weekday_Dummies, Month_Dummies], axis=1)
    return df2


def TM_split_train_test(dataframe, date, TempPred):
    df2 = dataframe.copy()

    date_hour = pd.to_datetime(date) + datetime.timedelta(hours=7)
    test_start_date = date_hour - datetime.timedelta(days=2)
    train_end_date = test_start_date - datetime.timedelta(hours=8)
    test_end_date = date_hour - datetime.timedelta(hours=8)
    date_for_test = pd.to_datetime(date) - datetime.timedelta(days=1)
    # prediction_end = date_hour + datetime.timedelta(hours=40)

    x_train = df2[df2['new_date'] <= train_end_date].drop(columns='Load')
    x_test = df2[(df2['new_date'] > test_start_date) & (df2['new_date'] <= test_end_date)].drop(columns='Load')
    y_train = df2[df2['new_date'] <= train_end_date]['Load']
    y_test = df2[(df2['new_date'] > test_start_date) & (df2['new_date'] <= test_end_date)]['Load']

    x_train2 = x_train.drop(columns=['Date', 'new_date'])
    x_test2 = x_test.drop(columns=['Date', 'new_date'])
    stations = ['RIV', 'LAX', 'USC', 'WJF', 'TRM']
    for station in stations:
        TempPred.model_building(date_for_test, station)
        TempPred.ensemble_models()
        pred = TempPred.predict_next_40hours_temp(station)
        x_test[station + '_Temp'] = pred

    return x_train2, y_train, x_test2, y_test


def NN_Temp_data_cleaning(dataframe):
    data = dataframe.copy()
    DateTime = pd.DataFrame(
        data.apply(lambda line: pd.to_datetime(line['Date']) + datetime.timedelta(hours=line['Hour']), axis=1))
    DateTime.columns = ['DateTime']
    temp = pd.concat(
        [DateTime, data.iloc[:, 2]], axis=1)
    temp.set_index('DateTime', inplace=True)
    return temp


def DR_data_cleaning(dataframe):
    df = dataframe.copy()
    test = df[['Date', 'Hour', 'Weekday', 'Month', 'Load', 'Mean_Temp', 'Mean_Humi']]

    test.loc[:, 'Load_Log'] = np.log(df['Load'])

    test['Load_Lag_48'] = test['Load_Log'].shift(48, axis=0)
    test['Temp_Lag_48'] = test['Mean_Temp'].shift(48, axis=0)
    test['Humi_Lag_48'] = test['Mean_Humi'].shift(48, axis=0)

    cal = USFederalHolidayCalendar()

    holidays = cal.holidays(start='2014-01-01', end=str(datetime.datetime.now()), return_name=True)

    holidays = pd.DataFrame(holidays)

    holidays = holidays.reset_index()
    holidays = holidays.rename(columns={'index': "Date", 0: 'Holiday'})
    holidays['Date'] = pd.to_datetime(holidays['Date'])
    holidays.head(2)

    test['Date'] = pd.to_datetime(test['Date'])
    lm_data = test.loc[49:len(test), ].merge(holidays, how='left', on='Date')
    lm_data['Holiday'] = lm_data['Holiday'].fillna("Not Holiday")

    lm_data[["Hour", "Weekday", "Month", "Holiday"]] = lm_data[["Hour", "Weekday", "Month", "Holiday"]].astype(
        'category')

    DateTime = pd.DataFrame(
        lm_data.apply(lambda line: pd.to_datetime(line['Date']) + datetime.timedelta(hours=line['Hour']), axis=1))
    DateTime.columns = ['DateTime']

    lm_data = pd.concat([DateTime, lm_data], axis=1)
    lm_data.set_index('DateTime', inplace=True)
    return lm_data


def validation_dataframe_cleaning(dataframe):
    validation_df = dataframe.copy()
    DateTime = pd.DataFrame(
        validation_df.apply(lambda line: pd.to_datetime(line['Date']) + datetime.timedelta(hours=line['Hour']), axis=1))
    DateTime.columns = ['DateTime']
    validation_df = pd.concat([DateTime, dataframe], axis=1)
    validation_df = validation_df[['DateTime', 'Load']]
    validation_df.set_index('DateTime', inplace=True)
    return validation_df
