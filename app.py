from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
from neuralprophet import NeuralProphet
import streamlit as st
import sqlite3

st.title('SmartForecast')

option = st.radio('Выберите источник данных:', ('Yahoo Finance', 'База данных'))

if option == 'Yahoo Finance':
    user_input = st.text_input('Введите тикер акций', 'TSLA')
    year_selection = st.slider('Выберите год:', 2010, 2024, (2010, 2024))
    data_source = yf.download(user_input, start=f'{year_selection[0]}-01-01', end=f'{year_selection[1]}-01-01')
    # Показываем доступные данные для прогноза
    st.subheader('Доступные данные для прогноза')
    st.write(data_source.describe())
    
    st.subheader('Визуализация развития цены')
    plt.figure(figsize=(12, 6))
    plt.plot(data_source['Close'])
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Развитие цены')
    st.pyplot(plt)
    
    st.subheader('Среднеквадратичная ошибка за 100 дней')
    ma100 = data_source['Close'].rolling(100).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(ma100)
    plt.plot(data_source['Close'])
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Среднеквадратичная ошибка за 100 дней')
    st.pyplot(plt)
    
    st.subheader('Среднеквадратичная ошибка за 200 дней')
    ma200 = data_source['Close'].rolling(200).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(ma100, 'r')
    plt.plot(ma200, 'g')
    plt.plot(data_source['Close'], 'b')
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Среднеквадратичная ошибка за 200 дней')
    st.pyplot(plt)

    if st.button('Начать прогнозирование', key='start_forecasting_button', help='Нажмите, чтобы начать прогнозирование'):
    #Обучение модели
        start = '2010-06-29'
        end = '2024-05-05'

        stock_data = yf.download(user_input, start=start, end=end)
        print(stock_data.head())
        stock_data.to_csv('stock_data.csv')

        stocks = pd.read_csv('stock_data.csv')
        stocks['Date'] = pd.to_datetime(stocks['Date'])
        stocks = stocks[['Date', 'Close']]
        stocks.columns = ['ds', 'y']

        plt.plot(stocks['ds'], stocks['y'], label='actual', c='g')
        plt.show()

        st.subheader('Прогноз развития цены')
        st.text('Это займет время')
        model = NeuralProphet()
        model.fit(stocks)

        # Теперь модель готова к работе
        future = model.make_future_dataframe(stocks, periods=300)
        forecast = model.predict(future)

        actual_prediction = model.predict(stocks)
        fig5 = plt.figure(figsize=(12, 6))
        plt.plot(data_source.Close, 'b')
        plt.plot(actual_prediction['ds'], actual_prediction['yhat1'], label="Среднее развитие цены", c='r')
        plt.plot(forecast['ds'], forecast['yhat1'], label='Прогноз развития цены', c='y')
        plt.plot(stocks['ds'], stocks['y'], label='Развитие цены', c='g')
        plt.legend()
        st.pyplot(fig5)

elif option == 'База данных':
    # Установка соединения с базой данных
    conn = sqlite3.connect('forecast.db')
    cursor = conn.cursor()
    
    # Получение результатов запроса и сохранение их в переменной data_source
    cursor.execute("SELECT Date, Close FROM forecast")
    data_source = cursor.fetchall()
    
    # Проверяем, что данные извлечены из базы данных
    if data_source:
        data_source_df = pd.DataFrame(data_source, columns=['Date', 'Close'])
        data_source_df['Date'] = pd.to_datetime(data_source_df['Date'])
        
        st.subheader('Доступные данные для прогноза')
        st.write(data_source_df.describe())

        st.subheader('Визуализация развития цены')
        plt.figure(figsize=(12, 6))
        plt.plot(data_source_df['Date'], data_source_df['Close'])
        plt.xlabel('Дата')
        plt.ylabel('Цена')
        plt.title('Развитие цены')
        st.pyplot(plt)
    else:
        st.write("Нет данных для отображения")
        
    st.subheader('Среднеквадратичная ошибка за 100 дней')
    ma100 = data_source_df['Close'].rolling(100).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(data_source_df['Date'], ma100)
    plt.plot(data_source_df['Date'], data_source_df['Close'])
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Среднеквадратичная ошибка за 100 дней')
    st.pyplot(plt)

    st.subheader('Среднеквадратичная ошибка за 200 дней')
    ma200 = data_source_df['Close'].rolling(200).mean()
    plt.figure(figsize=(12, 6))
    plt.plot(data_source_df['Date'], ma100, 'r')
    plt.plot(data_source_df['Date'], ma200, 'g')
    plt.plot(data_source_df['Date'], data_source_df['Close'], 'b')
    plt.xlabel('Дата')
    plt.ylabel('Цена')
    plt.title('Среднеквадратичная ошибка за 200 дней')
    st.pyplot(plt)

    # Кнопка для начала прогнозирования
    if st.button('Начать прогнозирование', key='start_forecasting_button', help='Нажмите, чтобы начать прогнозирование'):
        # Извлекаем первую и последнюю дату из данных
        start_date = data_source_df['Date'].min()
        end_date = data_source_df['Date'].max()

        # Обучение модели
        stocks = data_source_df.copy()
        stocks = stocks[['Date', 'Close']]
        stocks.columns = ['ds', 'y']

        plt.plot(stocks['ds'], stocks['y'], label='actual', c='g')
        plt.show()

        st.subheader('Прогноз развития цены')
        st.text('Это займет время')
        model = NeuralProphet()
        model.fit(stocks)

        # Теперь модель готова к работе
        future = model.make_future_dataframe(stocks, periods=300)
        forecast = model.predict(future)

        actual_prediction = model.predict(stocks)
        fig5 = plt.figure(figsize=(12, 6))
        plt.plot(data_source_df['Date'], data_source_df['Close'], 'b')
        plt.plot(actual_prediction['ds'], actual_prediction['yhat1'], label="Среднее развитие цены", c='r')
        plt.plot(forecast['ds'], forecast['yhat1'], label='Прогноз развития цены', c='y')
        plt.plot(stocks['ds'], stocks['y'], label='Развитие цены', c='g')
        plt.legend()
        st.pyplot(fig5)
        conn.close()