import pandas as pd

def load_train_data():
    return pd.read_csv('../data/train.csv', index_col=None)

def load_listings_data():
    return pd.read_csv('../data/listings.csv', index_col=None)

def load_full_data():
    return pd.read_csv('../data/custom_listings.csv', index_col=None)