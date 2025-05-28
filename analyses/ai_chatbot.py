import os
import random
import pandas as pd
import streamlit as st

# ─── Cached Data Loaders ────────────────────────────────────────────────────
@st.cache_data
def load_workout_data():
    """Load the mega gym workout dataset."""
    root = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root, "../data/processed/megaGymDataset.csv")
    return pd.read_csv(path)

@st.cache_data
def load_exercises_data():
    """Load the exercises dataset."""
    root = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root, "../data/processed/exercises4.csv")
    return pd.read_csv(path)

@st.cache_data
def load_tracker_data():
    """Load the workout fitness tracker dataset."""
    root = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root, "../data/processed/workout_fitness_tracker_data.csv")
    return pd.read_csv(path)

@st.cache_data
def load_nutrition_data():
    """Load and clean the nutrition dataset."""
    root = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(root, "../data/processed/products_w_ing.csv")
    df = pd.read_csv(path)
    # Clean protein and calories
    if 'PROTEIN' in df.columns:
        df['PROTEIN'] = df['PROTEIN'].astype(str).str.replace('g', '').astype(float, errors='ignore')
        df['protein2'] = df['PROTEIN']
    if 'CALORIES' in df.columns:
        df['CALORIES'] = pd.to_numeric(df['CALORIES'], errors='coerce')
    return df.dropna(subset=['CALORIES'])

# ─── Chatbot Helpers ─────────────────────────────────────────────────────────
def get_workout_plan(body_parts=None, workout_type=None):
    """
    Fetch workout plans based on user's body part and workout type preferences.
    Returns a list of dicts with keys: title, description, type, body_part.
    """
    workout_data = load_workout_data()
    print (workout_data["Type"].unique())
    plans = []
    if body_parts:
        parts = [p.strip() for p in body_parts.split('and')]
        for part in parts:
            df = workout_data.copy()
            if 'BodyPart' in df.columns:
                df = df[df['BodyPart'].str.lower() == part.lower()]
            if workout_type and 'Type' in df.columns:
                df = df[df['Type'].str.lower() == workout_type.lower()]
            if not df.empty:
                sample = df.sample(1).iloc[0]
                plans.append({
                    'title': sample.get('Title', ''),
                    'description': sample.get('Desc', ''),
                    'type': sample.get('Type', ''),
                    'body_part': sample.get('BodyPart', '')
                })
    return plans or [{'message': 'No workouts found for those preferences.'}]


def calculate_daily_calories(weight_lbs, height_in, age, gender, activity_level, bmi):
    """
    Harris-Benedict equation with activity factor and BMI adjustment.
    `weight_lbs` in pounds, `height_in` in inches, `age` in years.
    Activity levels: sedentary, light, moderate, active, very active.
    """
    # Convert to metric
    weight = weight_lbs * 0.453592  # kg
    height = height_in * 2.54       # cm

    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very active': 1.9
    }
    calories = bmr * factors.get(activity_level.lower(), 1.2)
    # Adjust by BMI
    if bmi > 25:
        calories *= 0.85
    elif bmi < 18.5:
        calories *= 1.15
    return round(calories)



def get_meal_plan(calories_target, goal):
    """
    Suggest a meal based on calorie target and goal (e.g., muscle gain, fat loss).
    Returns a dict with meal details or a message.
    """
    df = load_nutrition_data()
    if goal.lower() == 'muscle gain':
        min_protein = 25
    elif goal.lower() == 'fat loss':
        min_protein = 20
    else:
        min_protein = 15
    candidates = df[
        (df['CALORIES'] >= calories_target - 200) &
        (df['CALORIES'] <= calories_target + 200) &
        (df.get('protein2', pd.Series()).fillna(0) >= min_protein)
    ]
    if not candidates.empty:
        meal = candidates.sample(1).iloc[0]
        return {
            'name': meal.get('Name', ''),
            'category': meal.get('Category', ''),
            'calories': meal.get('CALORIES', 0),
            'protein': meal.get('PROTEIN', 0),
            'fat': meal.get('FAT', 0),
            'target_calories': calories_target,
            'min_protein': min_protein
        }
    return {'message': f'No meals found for target {calories_target} kcal and min protein {min_protein}g.'}

def calculate_bmi(weight_lbs, height_in):
    """
    Calculate BMI from weight (pounds) and height (inches).
    """
    # Convert to metric
    weight = weight_lbs * 0.453592  # kg
    height = height_in * 2.54       # cm
    h_m = height / 100.0
    return weight / (h_m * h_m)
