import pandas as pd
# Define file paths
raw_data_path = "../data/raw/exercises_raw.csv"  # Change this if needed

processed_data_path = "../data/processed/exercises_cleaned.csv"
# Read in raw data
df = pd.read_csv(raw_data_path)
# Clean data (Update yourself)
df.drop_duplicates(inplace=True)  # Remove duplicates
df.dropna(inplace=True)  # Drop missing values
df.reset_index(drop=True, inplace=True)  # Reset index after cleaning
# Add to processed folder
df.to_csv(processed_data_path, index=False)
print(f"✅ Data cleaning complete! Cleaned dataset saved to '{processed_data_path}'")f
