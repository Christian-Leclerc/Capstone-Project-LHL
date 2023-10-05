import pandas as pd

def load_train_data():
    return pd.read_csv('../data/all_houses_combined.csv')

def load_test_data():
    return pd.read_csv('../data/houses_test.csv')

def load_full_data():
    return pd.read_csv('../data/custom_listings.csv')