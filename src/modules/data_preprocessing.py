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

# Mix of cleaning and feature engineering
def clean_data(df):
    df_cleaned = df.copy()
    # Column naming
    df_cleaned.rename(columns={
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
        'Nbre pièces': 'rooms',
        'Nbre chambres (hors-sol + sous-sol)': 'bedrooms',
        "Nbre salles de bains + salles d'eau": 'washrooms'
    }, inplace=True)

    # Datatypes
    for col in ['price', 'income', 'build_eval', 'land_eval']:
        df_cleaned[col] = df_cleaned[col].str.replace('[\$, ]', '', regex=True).fillna(0).astype(int)

    # Remove outliers in income
    df_cleaned = df_cleaned[df_cleaned['income'] >= 2000].copy()

    # Extract year of construction
    def extract_year(row):
        year_match = re.search(r'\b\d{4}\b', row)

        return int(year_match.group()) if year_match else None

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

    ## Mapping of similar or translated terms to standard names
    map_water = {
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
                for key, value in map_water.items():
                    if key in row_lower:
                        water_name = value
                        break
                
        return pd.Series([near_water, water_name], index=['near_water', 'water_name'])
    
    # Pool info
    map_pool = {
        'chauffée': 'Chauffée',
        'creusée': 'Creusée', 
        'hors terre': 'Hors-Terre',
        'au locataire': 'Au locataire', 
        'semi-creusée': 'Semi-creusée', 
        'spa': 'Spa',
        'semi hors terre': 'Hors-terre', 
        'Étang à poisson': 'Étang à poisson',
        'béton 30 x 16': 'Creusée', 
        'toile 2021': 'Inconnu', 
        'semi-creusé / sel': 'Au sel',
        '2020': 'Inconnu',
        'thermopompe': 'Chaufée',
        'chauffée au mazout': 'Chauffée au mazout'
    }
    
    def standardize_pool(row):
        has_pool = 0
        pool_type = None
    
        if pd.notna(row):
            row_lower = row.lower()
            if row_lower != 'none':
                has_pool = 1
                for key, value in map_pool.items():
                    if key in row_lower:
                        pool_type = value
                        break
                
        return pd.Series([has_pool, pool_type], index=['has_pool', 'pool_type'])

    # Extract total parking lot
    def total_parking(row):
        if pd.isna(row):
            return 1
        numbers = re.findall(r'\((\d+)\)', row)

        return sum(int(num) for num in numbers)

    # Cleaning type of heating
    map_heating = {
        'plinthes électriques': 'Plinthes électriques',
        'plinthes à convection': 'Convecteurs',
        'eau chaude': 'Eau chaude',
        'air soufflé': 'Air soufflé (pulsé)',
        'air soufflé (pulsé)': 'Air soufflé (pulsé)',
        'radiant': 'Radiant',
        'thermopom': 'Thermopompe',
        'themo pomp mural': 'Thermopompe',
        'gaz naturel': 'Gaz naturel',
        'poêle à bois': 'Poêle à bois',
        'foyer ayu gaz': 'Foyer au gaz'
    }

    # Standardize the 'Chauffage' column and fill NaN with 'Plinthes électriques'
    df_cleaned['Chauffage'] = (
        df_cleaned['Chauffage']
        .apply(lambda x: ', '.join([map_heating.get(item.strip().lower(), item.strip()) for item in x.split(',')]) if pd.notna(x) else 'Plinthes électriques')
    )

    # Total washrooms
    df_cleaned['washrooms'] = df_cleaned['washrooms'].apply(lambda x: sum(int(item) for item in x.split('+')) if pd.notna(x) else 0)

    # Apply custom functions
    df_cleaned['year_built'] = df_cleaned['YearBuilt'].apply(extract_year)
    df_cleaned['living_area'] = df_cleaned.apply(extract_living_area, axis=1)
    df_cleaned['yard_area'] = df_cleaned.apply(extract_yard_area, axis=1)
    df_cleaned[['has_certificate', 'year_certificate', 'due_certificate']] = df_cleaned['Cert. de localisation'].apply(extract_certificate_info)
    df_cleaned[['near_water', 'water_name']] = df_cleaned['Plan d\'eau'].apply(standardize_water)
    df_cleaned[['has_pool', 'pool_type']] = df_cleaned['Piscine'].apply(standardize_pool)
    df_cleaned['total_parking'] = df_cleaned['Stationnement (total)'].apply(total_parking)

    # Drop rows where certain columns are NaN
    df_cleaned = df_cleaned.dropna(subset=['year_built', 'living_area', 'yard_area'])
    
    # Cast to appropriate data types
    df_cleaned['year_built'] = df_cleaned['year_built'].astype(int)
    df_cleaned['near_water'] = df_cleaned['near_water'].astype(int)
    df_cleaned['has_pool'] = df_cleaned['has_pool'].astype(int)
   

    return df_cleaned


# New features
def feature_engineering(df):
    
    df_engineered = df.copy()

    # List of unique heating types you want to consider
    unique_heating_types = ['Plinthes électriques', 'Convecteurs', 'Eau chaude', 'Air soufflé (pulsé)', 'Radiant', 'Thermopompe', 'Gaz naturel', 'Poêle à bois', 'Foyer au gaz']

    # Create new columns for each heating type
    for heating_type in unique_heating_types:
        df_engineered[heating_type] = df_engineered['Chauffage'].apply(lambda x: 1 if heating_type.lower() in x.lower() else 0)

    # Water_access boolean
    df_engineered['water_access'] = df_engineered['Eau (accès)'].apply(lambda x: 1 if pd.notna(x) and x != 'Non navigable' else 0)

    # Fireplace boolean and condition
    df_engineered['has_fireplace'] = df_engineered['Foyers-Poêles'].apply(lambda x: 0 if pd.isna(x) else 1)
    df_engineered['fireplace_func'] = df_engineered['Foyers-Poêles'].apply(lambda x: 0 if pd.isna(x) else (0 if 'non' in x.lower() else 1))

    # Services
    custom_services = ['Porte de garage électrique', 'Buanderie', 'Climatiseur', 'Aspirateur centrale' , 'Spa', "Détecteur d'incendie(relié)", 
                       "Détecteur d'incendie(non relié)", 'Adapté pour personne à mobilité réduite', 'Interphone', 'Fournaise', 'Thermopompe', 
                       'Planchers chauffant', 'Ascenseur', "Échangeur d'air", 'Fournaise', "Système d'alarme",'Borne de recharge']
    
    keyword_mapping = {
        'garage': 'Porte de garage électrique',
        'climatiseur': 'Climatiseur',
        'climatisation': 'Climatiseur',
        'buanderie': 'Buanderie',
        'aspirateur': 'Aspirateur centrale',
        'thermo': 'Thermopompe',
        'thermopompe': 'Thermopompe',
        'planchers chauffant': 'Planchers chauffant',
        'fournaise': 'Fournaise',
        'spa': 'Spa',
        'ascenseur(s)': 'Ascenseur',
        'borne': 'Borne de recharge',

    }

    ## Initialize new columns with zeros
    for service in custom_services:
        df_engineered[service] = 0

    def populate_service_columns(row):
        if pd.notna(row):
            for service in row.split(','):
                service_stripped = service.strip()
                # Check for exact match first
                if service_stripped in custom_services:
                    df_engineered.loc[df_engineered['Équip./Serv.'] == row, service_stripped] = 1
                else:
                    # Check for keyword match
                    for keyword, mapped_service in keyword_mapping.items():
                        if keyword in service_stripped.lower():
                            df_engineered.loc[df_engineered['Équip./Serv.'] == row, mapped_service] = 1
    # Renovations

    ## Initialize new columns
    df_engineered['has_reno'] = 0
    df_engineered['last_year_reno'] = 0  # Initialize with zeros instead of np.nan

    ## Update new columns based on 'Rénovations'
    for idx, row in df_engineered.iterrows():
        if pd.notna(row['Rénovations']):
            df_engineered.loc[idx, 'has_reno'] = 1
            years = [int(year) for year in re.findall(r'\b\d{4}\b', row['Rénovations'])]
            if years:
                df_engineered.loc[idx, 'last_year_reno'] = max(years)

    # Apply functions
    df_engineered['Équip./Serv.'].apply(populate_service_columns)

    return df_engineered