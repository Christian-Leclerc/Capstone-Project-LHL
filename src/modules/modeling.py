import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from joblib import dump, load

def train_linear_regression(X, y):
    regressor = LinearRegression()
    regressor.fit(X, y)

    return regressor

def evaluate_model(model, X, y):
    y_pred = model.predict(X)
    
    # Compute and print metrics
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    print(f"Mean Squared Error: {mse}")
    print(f"Root Mean Squared Error: {rmse}")
    print(f"R^2 Score: {r2}")

    residuals = y - y_pred

    return residuals

def feature_selection(X, y, significance_level=0.05):
    X_with_constant = sm.add_constant(X)
    
    regressor_OLS = sm.OLS(y, X_with_constant).fit()
    
    print(regressor_OLS.summary())
    
    # Drop the constant column and return the selected features
    return X_with_constant.drop(columns=['const'], errors='ignore')

def main(df):

    X = df.drop('price', axis=1)
    y = df['price']

    # Splitting dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Feature selection
    X_train = feature_selection(X_train, y_train)
    
    # Feature scaling
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train the model using the training set
    regressor = train_linear_regression(X_train, y_train)

    # Evaluate the model using the test set
    evaluate_model(regressor, X_test, y_test)
    
    # Generate predictions for the entire dataset
    X_all = scaler.transform(X)  # Scale the entire dataset
    predictions = regressor.predict(X_all).astype(int) 

    # Calculate the difference between actual and predicted prices
    residuals = (df['price'] - predictions).astype(int)

    # Saving trained model and scaler
    dump(regressor, 'trained_model.joblib')
    dump(scaler, 'trained_scaler.joblib')

    # Return the original dataframe with appended predictions, residuals and the model
    return df.assign(Predicted_Price=predictions, Residuals=residuals)

def predict_price(listings):
    # Load the trained model from the file
    model = load('trained_model.joblib')
    scaler = load('trained_scaler.joblib')

    # Select predominant features
    X = listings[['units', 'income', 'build_eval', 'yard_area', 'mean_price', 'build_age']].copy()

   # Scaling the new data
    X_scaled = scaler.transform(X)

    # Predict price with trained model
    predicted_prices = model.predict(X_scaled)

    # Caluclate residuals
    residuals = listings['price'] - predicted_prices

    return listings.assign(Predicted_Price=predicted_prices, Residuals=residuals)