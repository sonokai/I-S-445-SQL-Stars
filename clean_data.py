import pandas as pd
import numpy as np
import os

# 0. load data
# Prompt the user to type the name of the file in the terminal
file_name = input("Enter the exact name of the CSV file to clean: ")

# Safety check: Verify the file exists in the folder before proceeding
if not os.path.exists(file_name):
    print(f"Error: Could not find '{file_name}'. Please ensure it is in the exact same folder as this script.")
    exit()

# Load the user-specified dataset
df = pd.read_csv(file_name)

# 1. handle non-numeric symbols
df['discounted_price'] = df['discounted_price'].str.replace('₹', '', regex=False).str.replace(',', '', regex=False).astype(float)
df['actual_price'] = df['actual_price'].str.replace('₹', '', regex=False).str.replace(',', '', regex=False).astype(float)

# Remove '%' from percentages and convert to float
df['discount_percentage'] = df['discount_percentage'].str.replace('%', '', regex=False).astype(float)

# Remove ',' from rating counts. 
df['rating_count'] = df['rating_count'].astype(str).str.replace(',', '', regex=False)
df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')


# 2. clean rating column
def clean_rating(value):
    try:
        # Attempt to convert the value into a decimal number
        num = float(value)
        # Check if it is within the valid 0.0 to 5.0 range
        if 0.0 <= num <= 5.0:
            return round(num, 1) # Force it to 1 decimal point
        else:
            return np.nan # If it's outside the range, mark it as missing
    except (ValueError, TypeError):
        # If the value is a weird string like "|" that crashes the float() function, mark as missing
        return np.nan

# Apply the function to the rating column
df['rating'] = df['rating'].apply(clean_rating)


# 3. handle missing popularity data ---

# Approach A: Drop records completely (Use this if you want absolute accuracy)
df_dropped = df.dropna(subset=['rating_count']).copy()

# Approach B: Impute with Median (Use this if you want to keep as many products as possible)
df_imputed = df.copy()
median_popularity = df_imputed['rating_count'].median()
df_imputed['rating_count'] = df_imputed['rating_count'].fillna(median_popularity)


# 4. export cleaned dataset dynamically
# Extract the base name (e.g., 'amazon' from 'amazon.csv') and append '_cleaned.csv'
base_name = os.path.splitext(file_name)[0]
output_filename = f"{base_name}_cleaned.csv"

df_imputed.to_csv(output_filename, index=False)

print(f"Cleaning complete! Saved as '{output_filename}'.")