import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
import os
# Create a mapping for month names to their numeric representation
month_mapping = {
    'січень': 1,
    'лютий': 2,
    'березень': 3,
    'квітень': 4,
    'травень': 5,
    'червень': 6,
    'липень': 7,
    'серпень': 8,
    'вересень': 9,
    'жовтень': 10,
    'листопад': 11,
    'грудень': 12,
}

def load_data():
    # Load data from your SQLite database (replace the query with your actual data retrieval)
    query = '''
        SELECT salary_data.year, salary_data.month, salary_data.average_salary,
           unemployment_rate.rate AS unemployment_rate,
           dollar_rate_data.buy_rate, dollar_rate_data.sell_rate
            FROM salary_data
            JOIN unemployment_rate ON salary_data.year = unemployment_rate.year
            JOIN dollar_rate_data ON salary_data.year = dollar_rate_data.year AND salary_data.month = dollar_rate_data.month;
    '''
    connection = sqlite3.connect('../data/salary_data.db')
    df = pd.read_sql_query(query, connection)

    # Convert 'year' column to numeric values
    df['year'] = df['year'].astype(int)

    # Preprocess the data
    scaler = MinMaxScaler()
    df[['average_salary', 'unemployment_rate', 'buy_rate', 'sell_rate']] = scaler.fit_transform(df[['average_salary', 'unemployment_rate', 'buy_rate', 'sell_rate']])
    df['month'] = df['month'].map(month_mapping)

    # Replace any NaN values with a placeholder (you might want to handle this differently)
    df['month'].fillna(-1, inplace=True)

    df = df.sort_values(['year', 'month'])

    # Define input features and target
    X = df[['year', 'month', 'unemployment_rate', 'buy_rate', 'sell_rate']].values
    y = df['average_salary'].values

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Convert the 'month' column in X_train to float
    X_train[:, 1] = X_train[:, 1].astype(float)  # Assuming 'month' is at index 1

    return X_train, y_train, X_test, y_test

def train_neural_network(X_train, y_train):
    # Build the neural network model
    model = Sequential()
    model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1, activation='linear'))

    # Compile and train the model
    print("Training the neural network...")
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
    print("Neural network training completed.")
    model.save('trained_model.keras')
    return model

def test_neural_network(X_test, y_test):
    # Evaluate the model on the test set
    model = load_model('trained_model.keras')
    y_pred = model.predict(X_test)
    mse_test = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error on Test Set: {mse_test}')

if __name__ == "__main__":

    X_train, y_train, X_test, y_test = load_data()
    train_neural_network(X_train, y_train)
    test_neural_network(X_test, y_test)
