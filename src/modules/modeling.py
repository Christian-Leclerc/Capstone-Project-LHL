import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

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
    max_p_value = max(regressor_OLS.pvalues)
    
    while max_p_value > significance_level:
        drop_column = regressor_OLS.pvalues.idxmax()  # Get the feature with the highest p-value
        X_with_constant = X_with_constant.drop(columns=[drop_column])  # Drop this feature
        
        regressor_OLS = sm.OLS(y, X_with_constant).fit()
        max_p_value = max(regressor_OLS.pvalues)  # Re-compute the highest p-value
    
    # After the loop, print the summary of the final model
    print(regressor_OLS.summary())
    
    # Drop the constant column and return the selected features
    return X_with_constant.drop(columns=['const'], errors='ignore')

def main(df):

    X = df.drop('price', axis=1)
    y = df['price']

    # Splitting dataset into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Feature selection
    X_train_selected = feature_selection(X_train, y_train)

    # Train the model using the training set
    regressor = train_linear_regression(X_train_selected, y_train)

    # Evaluate the model using the test set
    evaluate_model(regressor, X_test[X_train_selected.columns], y_test)
    
    # Generate predictions for the entire dataset
    predictions = regressor.predict(df[X_train_selected.columns])

    # Calculate the difference between actual and predicted prices
    residuals = df['price'] - predictions

    # Return the original dataframe with appended predictions and residuals
    return df.assign(Predicted_Price=predictions, Residuals=residuals)