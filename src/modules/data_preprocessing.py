from modules.data_loading import load_train_data, load_test_data
import pandas as pd
import numpy as np
import ydata_profiling
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import re
from datetime import datetime

def clean_data(df):

    # Column naming
    df.rename(columns={
        'Prix': 'price',
        'Un. rés.': 'units',
        'Rev. brut. pot.': 'income',
        'Type de bâtiment':'build_type',
        'Éval. bâtiment': 'build_eval',
        'Éval. terrain': 'land_eval',
        'Remarques - Courtier': 'remarks',
        'Rénovations': 'renovations',
        'Inclusions': 'inclusions',
        'Exclusions': 'exclusions',
        'Addenda': 'addenda',
        'Nbre pièces': 'rooms'
    }, inplace=True)

    # Datatypes
    for col in ['price', 'income', 'build_eval', 'land_eval']:
        df[col] = df[col].str.replace('[\$, ]', '', regex=True).fillna(0).astype(int)

    # Remove outliers in income
    df = df[df['income'] >= 2000]

    # Extract year of construction
    def extract_year(row):
        year_match = re.search(r'\b\d{4}\b', row)
        return int(year_match.group()) if year_match else None

    ## Extract year and create a new column
    df['year_built'] = df['YearBuilt'].apply(extract_year)

    ## Drop rows where 'year_built' is None
    df.dropna(subset=['year_built'], inplace=True)

    ## Convert 'year_built' to integer
    df['year_built'] = df['year_built'].astype(int)

    # Filling missing value for living_area using building dimension
    def extract_living_area(row):
        # Extract living area if available
        if pd.notna(row['Superficie habitable']):
            match = re.search(r'([\d\s,]+)', row['Superficie habitable'].split('/')[0])
            if match and match.group(1).strip():
                return float(match.group(1).replace(',', '.').replace(' ', ''))
    
        # If living area is not available, use dimensions to calculate it
        if pd.notna(row['Dimensions du bâtiment']):
            match = re.findall(r'(\d+,\d+|\d+)', row['Dimensions du bâtiment'].split('/')[0])
            if len(match) >= 2:
                return float(match[0].replace(',', '.')) * float(match[1].replace(',', '.'))
        
        return np.nan
    
    ## Drop rows where 'living_area' is NaN
    df.dropna(subset=['living_area'], inplace=True)

    # Filling missing value for yard_area using land dimension
    def extract_yard_area(row):
        # Extract yard area if available
        if pd.notna(row['Superficie du terrain']):
            match = re.search(r'([\d\s,]+)', row['Superficie du terrain'].split('/')[0])
            if match and match.group(1).strip():
                return float(match.group(1).replace(',', '.').replace(' ', ''))
    
        # If yard area is not available, use dimensions to calculate it
        if pd.notna(row['Dimensions du terrain']):
            match = re.findall(r'(\d+,\d+|\d+)', row['Dimensions du terrain'].split('/')[0])
            if len(match) >= 2:
                return float(match[0].replace(',', '.')) * float(match[1].replace(',', '.'))
    
        return np.nan

    ## Drop rows where 'yard_area' is NaN
    df.dropna(subset=['yard_area'], inplace=True)

    # Extract certificate boolean and year (and overdue status)
    def extract_certificate_info(row):
        has_certificate = 0
        year_certificate = 0
        due_certificate = 0
    
        if 'Oui' in row:
            has_certificate = 1
            match = re.search(r'\((\d{4})\)', row)
            if match:
                year_certificate = int(match.group(1))
                current_year = datetime.now().year
                if current_year - year_certificate > 10:
                    due_certificate = 1
                
        return pd.Series([has_certificate, year_certificate, due_certificate], index=['has_certificate', 'year_certificate', 'due_certificate'])

    ## Create new columns
    df[['has_certificate', 'year_certificate', 'due_certificate']] = df['Cert. de localisation'].apply(extract_certificate_info)

    # Standardize near water names
    standard_names = ['Fleuve St-Laurent', 'Canal de Lachine', 'Rivière des Prairies', 'Louis Veuillot', 'Municipal', 'Ville']

    ## Mapping of similar or translated terms to standard names
    mapping = {
        'fleuve st-laurent': 'Fleuve St-Laurent',
        'st-lawrence river': 'Fleuve St-Laurent',
        'st-laurent river': 'Fleuve St-Laurent',
        'st lawrence': 'Fleuve St-Laurent',
        'st-lawrence': 'Fleuve St-Laurent',
        'canal de lachine': 'Canal de Lachine',
        'canal lachine': 'Canal de Lachine',
        'canal de l\'aqueduc': 'Canal de Lachine',
        'Lachine canal': 'Canal de Lachine',
        'lachine canal': 'Canal de Lachine',
        'rivière des prairies': 'Rivière des Prairies',
        'rivière-des-prairies': 'Rivière des Prairies',
        'municipal': 'Municipal',
        'rue municipal': 'Municipal',
        'municipality': 'Municipal',
        'municipalité': 'Municipal',
        'city': 'Ville',
        'ville': 'Ville',
        'louis veuillot': 'Louis Veuillot'
    }

    def standardize_water(row):
        near_water = 0
        water_name = None
    
        if pd.notna(row):
            row_lower = row.lower()
            if row_lower != 'none':
                near_water = 1
                for key, value in mapping.items():
                    if key in row_lower:
                        water_name = value
                        break
                
        return pd.Series([near_water, water_name], index=['near_water', 'water_name'])

    ## Create new columns
    df[['near_water', 'water_name']] = df['Plan d\'eau'].apply(standardize_water)
    
    ## Cast to appropriate data types
    df['near_water'] = df['near_water'].astype(int)

    return df_cleaned

def feature_engineering(df):
    # Feature engineering steps here
    return df_engineered