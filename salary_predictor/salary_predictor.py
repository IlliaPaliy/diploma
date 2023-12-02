import os
import pickle
import sqlite3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint

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
regions = ["Україна", "АР Крим", "Вінницька", "Волинська", "Дніпропетровська",
           "Донецька", "Житомирська", "Закарпатська", "Запорізька", "Івано-Франківська",
           "Київська", "Кіровоградська", "Луганська", "Львівська", "Миколаївська",
           "Одеська", "Полтавська", "Сумська", "Тернопільська", "Харківська", "Херсонська", "Хмельницька",
           "Черкаська", "Чернівецька", "Чернігівська", "м.Київ", "м.Севастополь"]


def load_data(year, region=None):
    region_filter = f"AND salary_data.region = '{region}'" if region else ""
    query = f'''
        SELECT salary_data.region, salary_data.month, salary_data.average_salary,
               unemployment_rate.rate AS unemployment_rate,
               dollar_rate_data.buy_rate, dollar_rate_data.sell_rate
        FROM salary_data
        JOIN unemployment_rate ON salary_data.year = unemployment_rate.year
        JOIN dollar_rate_data ON salary_data.year = dollar_rate_data.year AND salary_data.month = dollar_rate_data.month
        WHERE salary_data.year = {year}
        {region_filter};
    '''
    connection = sqlite3.connect('../data/salary_data.db')
    df = pd.read_sql_query(query, connection)

    # Convert 'month' column to numeric values
    df['month'] = df['month'].map(month_mapping)

    return df


def preprocess_data(df):
    X = df[['month', 'unemployment_rate', 'buy_rate', 'sell_rate']].values
    y = df['average_salary'].values
    return X, y


def normalize_output(y):
    # Normalize output independently
    y_scaler = MinMaxScaler()
    y_scaled = y_scaler.fit_transform(y.reshape(-1, 1))  # Assuming y is your output variable
    return y_scaled, y_scaler


def build_model(input_dim):
    model = Sequential()
    model.add(Dense(64, input_dim=input_dim, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def scale_data(X_train, X_val, y_train, y_val):
    # Create and fit the scaler for X
    scaler_X = MinMaxScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_val_scaled = scaler_X.transform(X_val)

    # Create and fit the scaler for y
    scaler_y = MinMaxScaler()
    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_val_scaled = scaler_y.transform(y_val.reshape(-1, 1)).flatten()

    return X_train_scaled, X_val_scaled, y_train_scaled, y_val_scaled, scaler_X, scaler_y


def inverse_scale_predictions(predictions, scaler):
    # Use the original min and max values from the training data
    original_min = scaler.data_min_[0]
    original_max = scaler.data_max_[0]

    predictions_normalized = predictions.flatten()
    predictions_original_scale = predictions_normalized * (original_max - original_min) + original_min
    return predictions_original_scale

def save_scalers(scaler_X, scaler_y):

    with open('scalers/scaler_X.pkl', 'wb') as file:
        pickle.dump(scaler_X, file)

    with open('scalers/scaler_y.pkl', 'wb') as file:
        pickle.dump(scaler_y, file)

def load_scalers():
    with open('scalers/scaler_X.pkl', 'rb') as file:
        scaler_X = pickle.load(file)

    with open('scalers/scaler_y.pkl', 'rb') as file:
        scaler_y = pickle.load(file)

    return scaler_X, scaler_y

def train_model(X_train, y_train, X_val, y_val, model_checkpoint_path='best_model.h5', scaler_dir='scalers'):
    model = build_model(X_train.shape[1])

    # Save the best model and scalers during training
    model_checkpoint = ModelCheckpoint(
        model_checkpoint_path,
        save_best_only=True,
        monitor='val_loss',
        mode='min',
        verbose=1,
        save_weights_only=False  # Save the entire model, including architecture and optimizer state
    )

    # Scale the data
    X_train_scaled, X_val_scaled, y_train_scaled, y_val_scaled, scaler_X, scaler_y = scale_data(X_train, X_val, y_train,
                                                                                                y_val)

    if len(X_train_scaled) != 12:
        print(f"Incomplete data. Skipping training.")
        return None, None, None, None

    # Train the model
    history = model.fit(
        X_train_scaled, y_train_scaled,
        epochs=50,
        batch_size=32,
        validation_data=(X_val_scaled, y_val_scaled),
        callbacks=[model_checkpoint]
    )

    print(f"Model trained successfully for {X_train[0, 0]}")

    # Save the scalers only when the model is saved
    if os.path.exists(model_checkpoint_path):
        save_scalers(scaler_X, scaler_y)

    return model, history, scaler_X, scaler_y



def test_model(X_test, y_test, model_path='best_model.h5', scaler_X=None, scaler_y=None):
    model = load_model(model_path)
    y_pred_normalized = model.predict(X_test)

    # Inverse scale the predictions
    y_pred = inverse_scale_predictions(y_pred_normalized, scaler_y)

    mse_test = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error on Test Set: {mse_test}')


def predict_salary_for_region(year, region, model_path='best_model.h5', scaler_path='scaler.pkl'):
    # Load data for the specified year and region
    df = load_data(year, region)
    df_region = df[df['region'] == region]

    if df_region.empty:
        print(f"No data available for {region} in {year}.")
        return

    # Preprocess the data
    X, y = preprocess_data(df_region)

    # Load the trained model
    model = load_model(model_path)

    # Load the single scaler
    with open(scaler_path, 'rb') as file:
        scaler = pickle.load(file)

    # Scale the data using the loaded scaler
    X_scaled = scaler.transform(X)

    # Predict salaries
    predicted_salaries_normalized = model.predict(X_scaled)

    # Inverse scale the predictions
    predicted_salaries = inverse_scale_predictions(predicted_salaries_normalized, scaler)

    # Create a dictionary with salaries for each month
    months = list(month_mapping.keys())
    predicted_salaries_dict = {month: salary for month, salary in zip(months, predicted_salaries)}

    return predicted_salaries_dict




def get_predicted_salaries(year, region, model_path='best_model.h5', scaler_X=None, scaler_y=None):
    # Load data for the specified year and region
    df = load_data(year, region)
    df_region = df[df['region'] == region]

    if df_region.empty:
        print(f"No data available for {region} in {year}.")
        return None

    # Preprocess the data
    X, y = preprocess_data(df_region)

    if X is None or y is None:
        print("No data for preprocessing.")
        return None

    # Load the trained model
    model = load_model(model_path)

    # Scale the data using the existing scalers
    X_scaled = scaler_X.transform(X)

    # Predict salaries for the next year
    predicted_salaries_normalized = model.predict(X_scaled)

    # Inverse scale the predictions
    predicted_salaries = inverse_scale_predictions(predicted_salaries_normalized, scaler_y)

    # Create a dictionary with salaries for each month
    months = list(month_mapping.keys())
    predicted_salaries_dict = {month: salary for month, salary in zip(months, predicted_salaries)}

    return predicted_salaries_dict



def region_data_is_complete(year, region):
    df = load_data(year, region)
    return not (df.empty or df.shape[0] != 12)

def main():
    complete_regions = []

    for region in regions:
        is_complete = all(region_data_is_complete(year, region) for year in range(2010, 2022))
        if is_complete:
            complete_regions.append(region)

    for region in complete_regions:
        for year in range(2010, 2021):  # Update the range based on your requirement
            X_train_region, y_train_region = preprocess_data(load_data(year, region))
            X_val_region, y_val_region = preprocess_data(load_data(year + 1, region))

            trained_model, history, scaler_X, scaler_y = train_model(X_train_region, y_train_region, X_val_region, y_val_region)

            # Test the model on the validation set
            test_model(X_val_region, y_val_region, model_path='best_model.h5', scaler_X=scaler_X, scaler_y=scaler_y)

            # Use the trained model to predict salaries for the next year
            predicted_salaries = get_predicted_salaries(year, region, scaler_X=scaler_X, scaler_y=scaler_y)

            if predicted_salaries is not None:
                print(f"Predicted Salaries for {region} in {year + 1}:\n{predicted_salaries}")


if __name__ == "__main__":
    main()
    scaler_X, scaler_y = load_scalers()
    predicted_salaries = get_predicted_salaries(2020, "м.Київ", scaler_X=scaler_X, scaler_y=scaler_y)

    if predicted_salaries is not None:
        print(f"Predicted Salaries for Україна in 2021:\n{predicted_salaries}")

