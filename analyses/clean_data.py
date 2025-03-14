import pandas as pd
import os

# Define file paths
raw_data_path = "../data/raw/exercises_raw.csv"
processed_data_path = "../data/processed/exercises_cleaned.csv"

try:
    print(f"Reading data from {os.path.abspath(raw_data_path)}")
    # Read in raw data
    df = pd.read_csv(raw_data_path)
    print(f"Found {len(df)} rows in raw data")
    
    # Clean data
    df.drop_duplicates(inplace=True)  # Remove duplicates
    df.dropna(inplace=True)  # Drop missing values
    df.reset_index(drop=True, inplace=True)  # Reset index after cleaning
    print(f"After cleaning: {len(df)} rows")
    
    # Add to processed folder
    os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
    df.to_csv(processed_data_path, index=False)
    print(f"✅ Data cleaning complete! Cleaned dataset saved to '{os.path.abspath(processed_data_path)}'")
except Exception as e:
    print(f"❌ Error: {str(e)}")
