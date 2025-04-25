import pandas as pd
import random
import os

def check_file(filepath):
    exists = os.path.exists(filepath)
    print(f"Checking file: {filepath}")
    print(f"File exists: {exists}")
    return exists

try:
    print("Loading datasets and analyzing their structure...")
    
    
    workout_data = pd.read_csv("C:/Users/murna/Downloads/archive (3)/megaGymDataset.csv")
    print("\n=== Workout Dataset ===")
    print("Total columns:", len(workout_data.columns))
    print("First 5 column names:", list(workout_data.columns[:5]))
    print("\nSample data (first 2 rows, first 5 columns):")
    print(workout_data.iloc[:2, :5])
    
   
    yes = pd.read_csv("C:/Users/murna/Downloads/archive (4)/exercises4 - Copy.csv")
    print("\n=== Exercises Dataset ===")
    print("Total columns:", len(yes.columns))
    print("First 5 column names:", list(yes.columns[:5]))
    print("\nSample data (first 2 rows, first 5 columns):")
    print(yes.iloc[:2, :5])
    
    
    yesagain = pd.read_csv("C:/Users/murna/Downloads/archive (5)/workout_fitness_tracker_data.csv")
    print("\n=== Workout Tracker Dataset ===")
    print("Total columns:", len(yesagain.columns))
    print("First 5 column names:", list(yesagain.columns[:5]))
    print("\nSample data (first 2 rows, first 5 columns):")
    print(yesagain.iloc[:2, :5])
    
    
    nutrition_data = pd.read_csv("C:/Users/murna/Downloads/archive (6)/products_w_ing.csv")
    print("\n=== Nutrition Dataset ===")
    print("Total columns:", len(nutrition_data.columns))
    print("Important columns:", [col for col in nutrition_data.columns if col.lower() in ['category', 'name', 'calories', 'protein', 'carbs', 'fat']])
    print("\nSample data (first 2 rows of important columns):")
    important_cols = [col for col in nutrition_data.columns if col.lower() in ['category', 'name', 'calories', 'protein', 'carbs', 'fat']]
    print(nutrition_data[important_cols].head(2))

    # Clean the nutrition data columns
    nutrition_data['PROTEIN'] = nutrition_data['PROTEIN'].str.replace('g', '').astype(float)
    nutrition_data['protein2'] = nutrition_data['PROTEIN'].astype(float)  # Create new column with just numeric values
    nutrition_data['CALORIES'] = pd.to_numeric(nutrition_data['CALORIES'], errors='coerce')
    nutrition_data = nutrition_data.dropna(subset=['CALORIES'])  # Remove rows with invalid calorie values

except Exception as e:
    print(f"\nError occurred: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    exit()

print("\nData loading complete!")

def get_workout_plan(body_parts=None, workout_type=None):
    """Fetch workout plans based on the user's preferences"""
    all_workouts = []
    
    if body_parts:
        
        body_part_list = [part.strip() for part in body_parts.split('and')]
        
        
        for body_part in body_part_list:
            filtered_workouts = workout_data[workout_data['BodyPart'].str.lower() == body_part.lower()]
            if workout_type:
                filtered_workouts = filtered_workouts[filtered_workouts['Type'].str.lower() == workout_type.lower()]
            
            if not filtered_workouts.empty:
                workout = filtered_workouts.sample(1).iloc[0]
                all_workouts.append({
                    'title': workout['Title'],
                    'description': workout['Desc'],
                    'type': workout['Type'],
                    'body_part': workout['BodyPart']
                })
    
    if all_workouts:
        return all_workouts
    return [{'message': 'No specific workout found for your preferences. Try different options!'}]

def calculate_daily_calories(weight, height, age, gender, activity_level, bmi):
    """Calculate daily calorie needs using Harris-Benedict equation with activity factor"""
    
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    
    activity_factors = {
        'sedentary': 1.2,     
        'light': 1.375,       
        'moderate': 1.55,      
        'active': 1.725,      
        'very active': 1.9     
    }
    
    calories = bmr * activity_factors.get(activity_level.lower(), 1.2)
    
    
    if bmi > 25: 
        calories *= 0.85  
    elif bmi < 18.5: 
        calories *= 1.15  
    
    return round(calories)

def get_meal_plan(calories_target, goal):
    """Fetch meal plans based on caloric needs and goals"""
    
    if goal.lower() == 'muscle gain':
        min_protein = 25  
    elif goal.lower() == 'fat loss':
        min_protein = 20 
    else:
        min_protein = 15  
    print("nutrition_data")
    print(nutrition_data)
    # filtered_meals = nutrition_data[
    #     (nutrition_data['CALORIES'] >= calories_target - 200) &
    #     (nutrition_data['CALORIES'] <= calories_target + 1000) &
    #     (nutrition_data['protein2'] >= 0)
    # ]
    filtered_meals = nutrition_data[
        (nutrition_data['protein2'] == 24)
    ]
    
    if not filtered_meals.empty:
        meal = filtered_meals.sample(1).iloc[0]
        return {
            'name': meal['Name'],
            'category': meal['Category'],
            'calories': meal['CALORIES'],
            'protein': meal['PROTEIN'],
            'fat': meal['FAT'],
            'target_calories': calories_target,
            'min_protein': min_protein
        }
    return {'message': f'No specific meal found for your needs (Target: {calories_target} calories, {min_protein}g protein minimum). Try adjusting your goals!'}

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height / 100  
    return weight / (height_m * height_m)

def chatbot():
    """Interactive AI Fitness Chatbot"""
    print("\nWelcome to the AI Fitness Chatbot! Let's create your personalized fitness plan.\n")
    
    try:
        
        height = float(input("Enter your height in cm: "))
        weight = float(input("Enter your weight in kg: "))
        age = float(input("Enter your age: "))
        gender = input("Enter your gender (male/female): ").strip().lower()
        
        print("\nHow active are you?")
        print("Options: sedentary (little/no exercise)")
        print("         light (exercise 1-3 days/week)")
        print("         moderate (exercise 3-5 days/week)")
        print("         active (exercise 6-7 days/week)")
        print("         very active (very hard exercise & physical job)")
        activity_level = input("Enter activity level: ").strip().lower()
        
        bmi = calculate_bmi(weight, height)
        print(f"\nYour BMI is: {bmi:.2f}")
        
        print("\nWhat is your primary goal?")
        print("Options: muscle gain, fat loss, maintenance")
        goal = input("Enter your goal: ").strip().lower()
        
        
        print("\nWhat body parts would you like to focus on?")
        print("Options: Abdominals, Arms, Back, Chest, Legs, Shoulders")
        print("You can combine multiple body parts using 'and' (e.g., 'Arms and Chest')")
        body_parts = input("Enter body part(s): ").strip()
        
        print("\nWhat type of workout would you like?")
        print("Options: Strength, Cardio, Flexibility")
        workout_type = input("Enter workout type: ").strip()
        
        
        calories_target = calculate_daily_calories(weight, height, age, gender, activity_level, bmi)
        
        
        workout_plans = get_workout_plan(body_parts, workout_type)
        meal_plan = get_meal_plan(calories_target, goal)
        
        
        print("\nHere's your personalized fitness plan:")
        print(f"\nBased on your profile (BMI: {bmi:.1f}, Activity: {activity_level})")
        print(f"Recommended daily calories: {calories_target}")
        
        print("\nWorkout Plans:")
        for i, workout_plan in enumerate(workout_plans, 1):
            print(f"\nWorkout {i}:")
            if 'message' in workout_plan:
                print(workout_plan['message'])
            else:
                print(f"Exercise: {workout_plan['title']}")
                print(f"Description: {workout_plan['description']}")
                print(f"Type: {workout_plan['type']}")
                print(f"Body Part: {workout_plan['body_part']}")
        
        print("\nNutrition Plan:")
        if 'message' in meal_plan:
            print(meal_plan['message'])
        else:
            print(f"Recommended Food: {meal_plan['name']}")
            print(f"Category: {meal_plan['category']}")
            print(f"Calories: {meal_plan['calories']} (Target: {meal_plan['target_calories']})")
            print(f"Protein: {meal_plan['protein']}g (Minimum target: {meal_plan['min_protein']}g)")
            print(f"Fat: {meal_plan['fat']}g")
            
    except ValueError as e:
        print("\nPlease enter valid numbers for height, weight, and age!")
        return
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return

if __name__ == "__main__":
    chatbot()
