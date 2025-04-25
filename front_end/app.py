import sys
import os
import streamlit as st
import pandas as pd
# Print sys.path to debug where Python is looking for modules
st.write(sys.path)

# Add the parent directory to sys.path manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# set up the dataframe
# Get the absolute path to the CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
df = pd.read_csv(csv_path)
df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

from analyses.filter_data import filter_data

st.title("Workout Recommender")

# Sort equipment options alphabetically, keeping 'None' at the beginning
equipment_options = ['None'] + sorted(['Parallel Bars', 'Chairs', 'Pull-up Bar', 'Dumbbell', 'Barbell',
 'Bench', 'Platform', 'Kettlebell', 'Step', 'Box', 'Resistance Band', 'Cable Machine', 
 'Low Bar', 'TRX', 'Wall', 'Sturdy Surface'])

# Sort muscle group options alphabetically
muscle_group_options = sorted(['Triceps', 'Chest', 'Back', 'Biceps', 'Core', 'Obliques',
 'Hamstrings', 'Glutes', 'Quadriceps', 'Rear Deltoids', 'Upper Back',
 'Shoulders', 'Calves', 'Forearms', 'Full Core', 'Full Body', 'Legs',
 'Upper Chest', 'Lower Chest'])

# User Inputs
calories_min = st.slider("Minimum calories burned", 10, 1000, 100)
calories_max = st.slider("Maximum calories burned", 10, 1000, 1000)
difficulty = st.selectbox("Select Difficulty Level", ["All","Beginner", "Intermediate", "Advanced"])
equipment_include = st.selectbox("Include Equipment", equipment_options)
equipment_exclude = st.selectbox("Exclude Equipment", equipment_options)
muscle_group = st.selectbox("Select Muscle Group", muscle_group_options)

# Run the filter function when the user interacts
if st.button("Find Workouts"):
    results = filter_data(df, int(calories_min), int(calories_max), difficulty, equipment_include, equipment_exclude, muscle_group)
    if not results.empty:
        st.write("Recommended Workouts:")
        st.dataframe(results)
    else:
        st.warning("No workouts found for the selected criteria. Try adjusting the filters!")
