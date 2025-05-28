import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd
import plotly.express as px
import random



# Add the parent directory to sys.path manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# set up the dataframe
# Get the absolute path to the CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
progress_file = os.path.join(BASE_DIR, "../data/user/progress.csv")
os.makedirs(os.path.dirname(progress_file), exist_ok=True)
if not os.path.isfile(progress_file):
    pd.DataFrame(columns=["date", "weight"]).to_csv(progress_file, index=False)
df = pd.read_csv(csv_path)

df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

from analyses.filter_data import filter_data
from analyses.nutrition_search import search_foods
from analyses.recipe_search import search_recipes_by_calories
from analyses.ai_chatbot import (
    get_workout_plan,
    calculate_daily_calories,
    get_meal_plan,
    calculate_bmi,
)
# from analyses.chatbot3 import load_chatbot, get_chatbot_response

st.title("Personal Health Assistant")


# Create tabs for the main interface and chat
tab1, tab2, tab3, tab4 = st.tabs([
    "Workout Finder",
    "Nutrition Calculator",
    "AI Fitness Plan",
    "Personal Tracker"
])

with tab1:
    st.header("Exercise Recommender")
    # Sort equipment options alphabetically, keeping 'None' at the beginning
    equipment_options = sorted(['Parallel Bars', 'Chairs', 'Pull-up Bar', 'Dumbbell', 'Barbell',
     'Bench', 'Platform', 'Kettlebell', 'Step', 'Box', 'Resistance Band', 'Cable Machine', 
     'Low Bar', 'TRX', 'Wall', 'Sturdy Surface'])

    # Sort muscle group options alphabetically
    muscle_group_options = sorted([
        'Triceps','Chest','Back','Biceps','Core','Obliques',
        'Hamstrings','Glutes','Quadriceps','Rear Deltoids','Upper Back',
        'Shoulders','Calves','Forearms','Full Core','Full Body','Legs',
        'Upper Chest','Lower Chest'
    ])

    # User Inputs
    calories_min = st.slider("Minimum calories burned", 10, 1000, 100)
    calories_max = st.slider("Maximum calories burned", 10, 1000, 1000)
    difficulty = st.selectbox("Select Difficulty Level", ["All","Beginner", "Intermediate", "Advanced"])
    equipment_include = st.multiselect("Include Equipment", equipment_options, default=[])
    equipment_exclude = st.multiselect("Exclude Equipment", equipment_options, default=[])
    selected_muscles = st.multiselect(
        "Select Muscle Group(s)",
        options=muscle_group_options,
        default=[]
    )

    if not selected_muscles:
        muscle_group = "All"
    else:
        muscle_group = selected_muscles
    print(muscle_group)

    # Run the filter function when the user interacts
    if st.button("Find Workouts"):
        results = filter_data(
            df,
            int(calories_min),
            int(calories_max),
            difficulty,
            equipment_include,
            equipment_exclude,
            muscle_group
        )
        if not results.empty:
            st.write("Recommended Workouts:")
            st.dataframe(results)
        else:
            st.warning("No workouts found for the selected criteria. Try adjusting the filters!")

# # -------------------------
# # Calorie Advice API Section
# # -------------------------

with tab2:
    st.header("Nutrition Calculator")

    # 1) Input & Search Trigger
    food_query = st.text_input("Enter a food name to search:", key="food_query")
    if st.button("Search Foods", key="search"):
        st.session_state.results = search_foods(food_query)
        st.session_state.page_index = 0
        st.session_state.query = food_query

    # 2) Render & Paginate (outside of the search-button `if`)
    if "results" in st.session_state and st.session_state.results:
        st.subheader(f'Search Results for "{st.session_state.query}"')
        results = st.session_state.results
        total = len(results)
        PAGE_SIZE = 5
        num_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

        # safety init
        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

        # Page Controls
        prev_col, mid_col, next_col = st.columns([1,2,1])
        with prev_col:
            if st.button("← Previous", key="prev") and st.session_state.page_index > 0:
                st.session_state.page_index -= 1
        with next_col:
            if st.button("Next →", key="next") and st.session_state.page_index < num_pages - 1:
                st.session_state.page_index += 1
        with mid_col:
            st.write(f"Page {st.session_state.page_index+1} of {num_pages}")

        # slice for current page
        start = st.session_state.page_index * PAGE_SIZE
        end = start + PAGE_SIZE
        page_results = results[start:end]

        

        # Render each result as before
        for food in page_results:
            name = food.get("food_name", "")
            url = food.get("food_url", "#")
            info_string = food.get("food_description", "")

            if " - " in info_string:
                weight_info, macros_part = info_string.split(" - ", 1)
            else:
                weight_info, macros_part = None, info_string

            macros = {}
            for chunk in macros_part.split("|"):
                if ":" in chunk:
                    label, val = chunk.split(":", 1)
                    macros[label.strip()] = val.strip()

            with st.expander(name):
                if weight_info:
                    st.caption(weight_info)
                cols = st.columns(4)
                for col, key in zip(cols, ["Calories", "Fat", "Carbs", "Protein"]):
                    val = macros.get(key, "—")
                    if key == "Calories" and val.endswith("kcal"):
                        val = val[:-4].strip() + " kcal"
                    col.metric(label=key, value=val)
                st.markdown(f"[More info ➞]({url})", unsafe_allow_html=True)

        st.markdown("---")

 
with tab4:
    st.header("Personal Tracker")
    # New Entry Form 
    with st.form("progress_form"):
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        calories_burned = st.number_input("Calories Burned", min_value=0, step=5)
        steps = st.number_input("Total Steps", min_value=0, step=10)
        sleep_time = st.number_input("Sleep Duration (hr)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Add Entry")

    if submitted:
        # Load existing entries
        df_progress = pd.read_csv(progress_file)
        # Check for duplicate date
        existing_dates = set(df_progress["date"])
        if date.isoformat() in existing_dates:
            st.warning(f"You already entered data for {date.strftime('%m/%d/%Y')}.")
        else:
            # Append new entry
            df_progress.loc[len(df_progress)] = [date.isoformat(), weight, calories_burned, steps, sleep_time]
            df_progress.to_csv(progress_file, index=False)
            st.success("Entry added!")

     # ─ load and prepare data ─────────────────────────────────────────────────
    df_progress = pd.read_csv(progress_file)
    df_progress["date"] = pd.to_datetime(df_progress["date"])
    df_progress = df_progress.sort_values("date").reset_index(drop=True)

     # — Prepare Display DataFrame —
    display_df = pd.DataFrame({
        "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
        "Weight (lbs)": df_progress["weight"],
        "Calories Burned": df_progress["calories_burned"],
        "Steps": df_progress["steps"],
        "Sleep Duration": df_progress["sleep_time"],
    })

    st.subheader("Progress Data")
    st.dataframe(display_df, use_container_width=True)

    # — Inline Deletion Controls —
    st.markdown("**Select rows to delete:**")
    # Build options by zipping the two series
    options = [
        f"{d} — {w} lbs"
        for d, w, c, s, t in zip(display_df["Date"], display_df["Weight (lbs)"], display_df["Calories Burned"], display_df["Steps"], display_df["Sleep Duration"])
    ]
    to_delete = st.multiselect("Entries to remove", options)

    if st.button("Delete Selected") and to_delete:
        # Construct a boolean mask: keep rows whose label is NOT in to_delete
        keep_mask = [
            f"{d} — {w} lbs" not in to_delete
            for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])
        ]
        # Apply mask to original df_progress
        df_progress = df_progress[keep_mask].reset_index(drop=True)
        df_progress.to_csv(progress_file, index=False)
        st.success(f"Deleted {len(to_delete)} entr{'y' if len(to_delete)==1 else 'ies'}.")
        st.rerun()

        # Reload and re-display
        df_progress["date"] = pd.to_datetime(df_progress["date"])
        df_progress = df_progress.sort_values("date").reset_index(drop=True)
        display_df = pd.DataFrame({
            "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
            "Weight (lbs)": df_progress["weight"],
            "Calories Burned": df_progress["calories_burned"],
            "Steps": df_progress["steps"],
            "Sleep Duration": df_progress["sleep_time"]
        })
        st.dataframe(display_df, use_container_width=True)
    values = ["date", "weight", "calories_burned", "steps", "sleep_time"]
    x_metric = st.selectbox(
        "Select the x value:",
        values
    )
    values.remove(x_metric)
    y_metric = st.selectbox(
        "Select the y value:",
        values
    )
    if not df_progress.empty:
        fig = px.line(
            df_progress,
            x=x_metric,
            y=y_metric,
            title=f"{y_metric.capitalize()} Over {x_metric.capitalize()}",
            markers=True,
            labels={x_metric: x_metric.capitalize(), y_metric: y_metric.capitalize()}
        )
        st.plotly_chart(fig, use_container_width=True)





with tab3:
    st.header("AI Fitness Plan")

    st.markdown("Fill in your details to get a personalized workout & meal plan:")

    # 1) Collect user profile
    col1, col2 = st.columns(2)
    with col1:
        weight_lbs = st.number_input("Weight (lbs)", min_value=1.0, step=0.1, value=130.0)
        height_in = st.number_input("Height (in)", min_value=20.0, step=0.5, value=65.0)
        age       = st.number_input("Age", min_value=10, max_value=120, value=30)
    with col2:
        gender = st.selectbox("Gender", ["male","female"])
        activity_level = st.selectbox("Activity Level", [
            "sedentary", "light", "moderate", "active", "very active"
        ],
        help="""
        **sedentary**: little or no exercise  
        **light**: exercise 1-3 days/week  
        **moderate**: exercise 3-5 days/week  
        **active**: exercise 6-7 days/week  
        **very active**: hard exercise daily or physical job
        """)
        goal = st.selectbox("Goal", ["maintenance","muscle gain","fat loss"])

    # 2) Workout preferences
    st.subheader("Workout Preferences")
    
    body_options = ['Abdominals', 'Adductors', 'Abductors', 'Biceps', 'Calves', 'Chest', 'Forearms', 'Glutes', 
    'Hamstrings', 'Lats', 'Lower Back', 'Middle Back', 'Traps', 'Neck', 'Quadriceps', 'Shoulders', 'Triceps']
    selected_parts = st.multiselect(
        "Body Parts (select one or more):",
        options=body_options,
        default=["Abdominals"]
    )
    # Join them into the format your helper expects:
    body_parts = " and ".join(selected_parts) if selected_parts else None
    workout_type = st.selectbox("Workout Type:", ['Strength', 'Plyometrics', 'Cardio', 'Stretching', 'Powerlifting', 
    'Strongman', 'Olympic Weightlifting'])

    # 3) Trigger
    if st.button("Generate Plan", key="gen"):
        bmi = calculate_bmi(weight_lbs, height_in)
        daily_cals = calculate_daily_calories(
        weight_lbs, height_in, age, gender, activity_level, bmi
        )
        plans = get_workout_plan(body_parts, workout_type)
        meal_info = get_meal_plan(daily_cals, goal)

        st.session_state.bmi         = bmi
        st.session_state.daily_cals  = daily_cals
        st.session_state.plans       = plans
        st.session_state.meal_info   = meal_info
        # clear any previous recipe search
        st.session_state.pop("recipes", None)

    # 2) If we have a plan in session_state, render it
    if "daily_cals" in st.session_state:
        st.metric("Your BMI", f"{st.session_state.bmi:.1f}")
        st.metric("Daily Calorie Target", f"{st.session_state.daily_cals} kcal")

        st.subheader("🏋️ Workout Plan")
        for i, p in enumerate(st.session_state.plans, 1):
            if p.get("message"):
                st.info(p["message"])
            else:
                st.markdown(f"**{i}. {p['title']}**")
                st.write(f"- Type: {p['type']}")
                st.write(f"- Body Part: {p['body_part']}")
                desc = p.get("description", "")
                if pd.notna(desc) and desc.strip():
                    st.write(desc)

        # 6) Recipe‑Based Meal Plan
        st.subheader("🍽️ Recipe Plan")

        # calories per meal ≈ 1/3 of the daily goal
        meal_cals = st.session_state.daily_cals / 3
        cal_min   = max(int(meal_cals - 600), 0)
        cal_max   = int(meal_cals + 800)
        st.markdown(f"Looking for a recipe between **{cal_min}–{cal_max} kcal** per serving…")

        # Perform the search once
        recipes = search_recipes_by_calories(
            cal_min=cal_min,
            cal_max=cal_max,
            # max_results=5,
            # sort_by="calories"
        )

        if not recipes:
            st.warning("No recipes found in that calorie range.")
        else:
            # pick one recipe at random
            rec = random.choice(recipes)
            # details = get_recipe_details(rec["id"])

            # # Display it
            # st.markdown(f"### [{details['name']}]({details['url']})")
            # st.markdown("**Ingredients:**")
            # for ing in details["ingredients"]:
            #     st.write(f"- {ing}")

            # if details.get("directions"):
            #     st.markdown("**Instructions:**")
            #     st.write(details["directions"])

            # if details.get("nutrition"):
            #     st.markdown("**Nutrition per serving:**")
            #     for nut, val in details["nutrition"].items():
            #         st.write(f"- {nut}: {val}")