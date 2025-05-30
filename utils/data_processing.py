import pandas as pd
import json
import os
from datetime import datetime

def load_food_data():
    """
    Load the food dataset
    """
    try:
        food_data = pd.read_csv('attached_assets/cleaned_food_data_refined.csv')
        # Clean up column names and data
        food_data.columns = food_data.columns.str.strip()
        # Ensure numeric columns are treated as numeric
        numeric_cols = ['Calories', 'Total Fat', 'Saturated Fat', 'Monounsaturated Fat', 
                       'Polyunsaturated Fat', 'Carbs', 'Sugar', 'Protein', 'Dietary Fiber', 
                       'Cholesterol', 'Sodium', 'Water']
        for col in numeric_cols:
            if col in food_data.columns:
                food_data[col] = pd.to_numeric(food_data[col], errors='coerce')
        
        return food_data
    except Exception as e:
        print(f"Error loading food data: {e}")
        # Return empty DataFrame if file not found or other error
        return pd.DataFrame()

def load_exercise_data():
    """
    Load the exercise dataset
    """
    try:
        exercise_data = pd.read_csv('attached_assets/cleaned_exercise_data_refined.csv')
        # Clean up column names
        exercise_data.columns = exercise_data.columns.str.strip()
        return exercise_data
    except Exception as e:
        print(f"Error loading exercise data: {e}")
        # Return empty DataFrame if file not found or other error
        return pd.DataFrame()

def load_user_records():
    """
    Load user records from JSON file
    """
    try:
        with open('attached_assets/records.json', 'r') as f:
            user_records = json.load(f)
        return user_records
    except Exception as e:
        print(f"Error loading user records: {e}")
        # Return empty dict if file not found or other error
        return {"records": {}}

def save_user_records(user_records):
    """
    Save user records to JSON file
    """
    try:
        with open('attached_assets/records.json', 'w') as f:
            json.dump(user_records, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving user records: {e}")
        return False

def calculate_bmi(weight, height):
    """
    Calculate BMI given weight in kg and height in cm
    """
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    
    # Determine BMI status
    if bmi < 18.5:
        status = "Underweight"
    elif 18.5 <= bmi < 25:
        status = "Healthy"
    elif 25 <= bmi < 30:
        status = "Overweight"
    else:
        status = "Obese"
        
    return round(bmi, 2), status

def calculate_calorie_needs(weight, height, age, gender, activity_level, goal):
    """
    Calculate daily calorie needs based on user data
    
    Parameters:
    - weight: in kg
    - height: in cm
    - age: in years
    - gender: 'male' or 'female'
    - activity_level: 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'
    - goal: 'Weight Loss', 'Weight Gain', 'Maintain Weight', 'Muscle Gain', 'Not specified'
    
    Returns:
    - Daily calorie needs
    """
    # Calculate BMR using Mifflin-St Jeor Equation
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Apply activity multiplier
    activity_multipliers = {
        'sedentary': 1.2,  # Little or no exercise
        'lightly_active': 1.375,  # Light exercise 1-3 days per week
        'moderately_active': 1.55,  # Moderate exercise 3-5 days per week
        'very_active': 1.725,  # Hard exercise 6-7 days per week
        'extra_active': 1.9  # Very hard exercise & physical job or training twice a day
    }
    
    # Default to moderately active if not specified
    activity_multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    
    tdee = bmr * activity_multiplier
    
    # Adjust based on goal
    goal_adjustments = {
        'weight loss': -500,  # 500 calorie deficit
        'weight gain': 500,   # 500 calorie surplus
        'maintain weight': 0,
        'muscle gain': 300,   # Moderate surplus for muscle gain
        'not specified': 0
    }
    
    # Clean up goal text and default to no adjustment if goal not recognized
    clean_goal = goal.lower().strip()
    calorie_adjustment = 0
    
    for key, value in goal_adjustments.items():
        if key in clean_goal:
            calorie_adjustment = value
            break
    
    daily_calories = tdee + calorie_adjustment
    
    # Round to nearest 50 calories
    return round(daily_calories / 50) * 50

def calculate_macros(calories, goal):
    """
    Calculate macronutrient distribution based on calorie needs and goal
    
    Returns:
    - Dict containing protein, carbs, and fat in grams
    """
    goal = goal.lower() if goal else ""
    
    if "muscle gain" in goal:
        # Higher protein for muscle gain
        protein_pct = 0.30
        fat_pct = 0.25
        carbs_pct = 0.45
    elif "weight loss" in goal:
        # Higher protein, moderate fat, lower carbs for weight loss
        protein_pct = 0.35
        fat_pct = 0.30
        carbs_pct = 0.35
    elif "weight gain" in goal:
        # Balanced macros with emphasis on carbs for weight gain
        protein_pct = 0.20
        fat_pct = 0.30
        carbs_pct = 0.50
    else:
        # Balanced distribution for maintenance or unspecified
        protein_pct = 0.25
        fat_pct = 0.30
        carbs_pct = 0.45
    
    # Calculate grams of each macronutrient
    protein_grams = (calories * protein_pct) / 4  # 4 calories per gram of protein
    carbs_grams = (calories * carbs_pct) / 4      # 4 calories per gram of carbs
    fat_grams = (calories * fat_pct) / 9          # 9 calories per gram of fat
    
    # Round to nearest whole number
    return {
        "protein": round(protein_grams),
        "carbs": round(carbs_grams),
        "fat": round(fat_grams)
    }

def filter_foods_by_preference(food_data, diet_preference):
    """
    Filter foods based on user's dietary preference
    """
    # For simplicity, we'll use some keywords to filter foods
    if diet_preference.lower() == 'vegetarian':
        # Filter out obvious meat-containing foods
        meat_keywords = ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'duck', 'veal', 
                        'ham', 'bacon', 'sausage', 'salmon', 'fish', 'seafood', 'shrimp',
                        'crab', 'lobster', 'meatball', 'meatloaf', 'steak']
        
        # Create a filter condition based on food names not containing meat keywords
        filter_condition = ~food_data['Food Name'].str.lower().str.contains('|'.join(meat_keywords), na=False)
        
        return food_data[filter_condition]
        
    elif diet_preference.lower() == 'vegan':
        # Filter out animal products
        animal_keywords = ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'duck', 'veal', 
                          'ham', 'bacon', 'sausage', 'salmon', 'fish', 'seafood', 'shrimp',
                          'crab', 'lobster', 'cheese', 'milk', 'cream', 'butter', 'egg',
                          'yogurt', 'honey', 'meat', 'whey', 'casein', 'gelatin']
        
        filter_condition = ~food_data['Food Name'].str.lower().str.contains('|'.join(animal_keywords), na=False)
        
        return food_data[filter_condition]
        
    else:
        # Return all foods for 'both' or any other preference
        return food_data
