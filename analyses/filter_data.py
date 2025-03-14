import pandas as pd

df = pd.read_csv("../data/processed/exercises_cleaned.csv")
print(df.head())
print(df.columns)

def filter_data(df, calories_min, calories_max):
    df = df[df["Burns Calories"] >= calories_min]
    df = df[df["Burns Calories"] <= calories_max]
    return df
print(f"Filtered data: {filter_data(df, 100, 200).head()}")