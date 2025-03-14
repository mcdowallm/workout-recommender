import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define file paths
processed_data_path = "../data/processed/exercises_cleaned.csv"  # Change if needed
# Read in processed data
df = pd.read_csv(processed_data_path)
# Basic information
print("🔍 Dataset Overview:")
print(df.info())
print(df.describe())
# Check for missing values
print("\n🛑 Missing Values:")
print(df.isnull().sum())
# Plot distribution of numerical features
numerical_columns = df.select_dtypes(include=["number"]).columns
for col in numerical_columns:
    plt.figure(figsize=(6, 4))
    sns.histplot(df[col], bins=20, kde=True)
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.show()
# Correlation heatmap (if numerical data exists)
if len(numerical_columns) > 1:
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[numerical_columns].corr(), annot=True, cmap="coolwarm")
    plt.title("Feature Correlation Heatmap")
    plt.show()
print("✅ EDA complete! Check the generated plots.")
