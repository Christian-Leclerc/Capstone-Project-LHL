import pandas as pd

def load_train_data():
    return pd.read_csv('../data/train.csv', index_col=None)

def load_test_data():
    return pd.read_csv('../data/test.csv', index_col=None)

def load_full_data():
    return pd.read_csv('../data/custom_listings.csv', index_col=None)