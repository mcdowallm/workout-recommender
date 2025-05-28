import os
import pandas as pd
import re

# Get the absolute path to the CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")

df = pd.read_csv(csv_path)
df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

def filter_data(df, calories_min=0, calories_max=None, difficulty=None, equipment_include=None,equipment_exclude=None, muscle_group=None):
    df = df[df["Burns Calories"] >= calories_min]
    df = df[df["Burns Calories"] <= calories_max]
    df = df[df["Difficulty Level"] == difficulty] if difficulty != "All" else df
    # df = df[df["Equipment Needed"].str.contains(equipment_include, case=False, na=False)] if equipment_include != "None" else df
    # if equipment_exclude is not None and equipment_exclude != "None":
    #     mask = ~df["Equipment Needed"].str.contains("or", case=False, na=False)
    #     df_filtered = df.loc[mask].copy()
    #     df_filtered = df_filtered[~df_filtered["Equipment Needed"].str.contains(equipment_exclude, case=False, na=False)]
    #     df.loc[mask] = df_filtered
    if equipment_include:
        # build regex “Dumbbell|Barbell|…”
        include_pattern = "|".join(re.escape(eq) for eq in equipment_include)
        df = df[df["Equipment Needed"]
                .str.contains(include_pattern, case=False, na=False)]

    # — Exclude filter (drop any row that mentions any excluded item) —
    if equipment_exclude:
        exclude_pattern = "|".join(re.escape(eq) for eq in equipment_exclude)
        df = df[~df["Equipment Needed"]
                .str.contains(exclude_pattern, case=False, na=False)]
    if muscle_group != "All":
        if isinstance(muscle_group, list):
            df = df[df["Target Muscle Group"].isin(muscle_group)]
        else:
            df = df[df["Target Muscle Group"] == str(muscle_group)]

    
    return df
# print(f"Filtered data: {filter_data(df, calories_min=100, calories_max=1000, difficulty="Beginner", equipment_include="None", equipment_exclude="None", muscle_group="Back").head()}")

