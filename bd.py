import sqlite3
import pandas as pd
# Установка соединения с базой данных
conn = sqlite3.connect('forecast.db')
cursor = conn.cursor()

# Создаем таблицу, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS forecast
                  (Date TEXT, Close REAL)''')

# Создаем список кортежей с данными
data_to_insert = []
start_date = '2023-01-25'
for i in range(50):
    date = (pd.to_datetime(start_date) + pd.DateOffset(days=i)).strftime('%Y-%m-%d')
    data_to_insert.append((date, 200 + i))  # Close начинается с 200 и увеличивается на 1 для каждой даты

# Вставляем данные в таблицу
cursor.executemany('INSERT INTO forecast VALUES (?, ?)', data_to_insert)

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()
