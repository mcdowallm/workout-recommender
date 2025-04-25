import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd



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
# from analyses.chatbot3 import load_chatbot, get_chatbot_response

st.title("Personal Health Assistant")

# Create tabs for the main interface and chat
tab1, tab2, tab3, tab4 = st.tabs(["Workout Finder", "Calorie Chatbot", "Nutition Calculator", "Personal Tracker"])

with tab1:
    st.header("Exercise Recommender")
    # Sort equipment options alphabetically, keeping 'None' at the beginning
    equipment_options = ['None'] + sorted(['Parallel Bars', 'Chairs', 'Pull-up Bar', 'Dumbbell', 'Barbell',
     'Bench', 'Platform', 'Kettlebell', 'Step', 'Box', 'Resistance Band', 'Cable Machine', 
     'Low Bar', 'TRX', 'Wall', 'Sturdy Surface'])

    # Sort muscle group options alphabetically
    muscle_group_options = ['All'] + sorted(['Triceps', 'Chest', 'Back', 'Biceps', 'Core', 'Obliques',
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

# # -------------------------
# # Calorie Advice Chatbot Section
# # -------------------------
with tab2:
    st.header("Nutritional Assistant")
    st.write("Ask any question about nutrition, calories, or dietary advice:")

# # -------------------------
# # Calorie Advice API Section
# # -------------------------

with tab3:
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
        with mid_col:
            st.write(f"Page {st.session_state.page_index+1} of {num_pages}")
        with next_col:
            if st.button("Next →", key="next") and st.session_state.page_index < num_pages - 1:
                st.session_state.page_index += 1

        # slice for current page
        start = st.session_state.page_index * PAGE_SIZE
        end = start + PAGE_SIZE
        page_results = results[start:end]

        

        # 3) Render each result as before
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
    # — New Entry Form —
    with st.form("progress_form"):
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
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
            df_progress.loc[len(df_progress)] = [date.isoformat(), weight, steps, sleep_time]
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
        "Steps": df_progress["steps"],
        "Sleep Duration": df_progress["sleep_time"]
    })

    st.subheader("Progress Data")
    st.dataframe(display_df, use_container_width=True)

    # — Inline Deletion Controls —
    st.markdown("**Select rows to delete:**")
    # Build options by zipping the two series
    options = [
        f"{d} — {w} lbs"
        for d, w, s, t in zip(display_df["Date"], display_df["Weight (lbs)"], display_df["Steps"], display_df["Sleep Duration"])
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

        # Reload and re-display
        df_progress["date"] = pd.to_datetime(df_progress["date"])
        df_progress = df_progress.sort_values("date").reset_index(drop=True)
        display_df = pd.DataFrame({
            "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
            "Weight (lbs)": df_progress["weight"],
            "Steps": df_progress["steps"],
            "Sleep Duration": df_progress["sleep_time"]
        })
        st.dataframe(display_df, use_container_width=True)

    # — Plot Weight Over Time —
    fig, ax = plt.subplots()
    dates = df_progress["date"]
    weights = df_progress["weight"]

    ax.plot(dates, weights, marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (lbs)")
    ax.set_title("Weight Over Time")

    # 1 day margin on each end
    ax.margins(x=0.05)

    # Tick exactly at each date
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))

    # Rotate for readability
    fig.autofmt_xdate()

    st.pyplot(fig)
