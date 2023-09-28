import pandas as pd

def load_train_data():
    return pd.read_csv('../data/train.csv')

def load_test_data():
    return pd.read_csv('../data/test.csv')

def load_full_data():
    return pd.read_csv('../data/full_data.csv')