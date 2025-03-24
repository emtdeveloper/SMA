import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.data_processing import calculate_calorie_needs, calculate_macros, filter_foods_by_preference

def generate_meal_plan(user_data, food_data, days=7, meals_per_day=3):
    """
    Generate a meal plan based on user preferences and nutritional needs
    
    Parameters:
    - user_data: Dict containing user information
    - food_data: DataFrame with food nutrition data
    - days: Number of days for the plan
    - meals_per_day: Number of meals per day
    
    Returns:
    - Dict containing meal plan information
    """
    # Filter foods based on dietary preference
    filtered_foods = filter_foods_by_preference(food_data, user_data.get('diet', 'both'))
    
    if filtered_foods.empty:
        return {"error": "No foods available that match your dietary preferences"}
    
    # Ensure 'Calories' column exists and is numeric
    if 'Calories' not in filtered_foods.columns:
        return {"error": "Food data is missing calorie information"}
    
    # Calculate daily calorie needs based on user profile
    weight = user_data.get('weight', 70)
    height = user_data.get('height', 170)
    gender = user_data.get('gender', 'male')
    goal = user_data.get('goal', 'Maintain Weight')
    
    # Assume a default age and activity level if not available
    age = user_data.get('age', 30)
    activity_level = user_data.get('activity_level', 'moderately_active')
    
    daily_calories = calculate_calorie_needs(weight, height, age, gender, activity_level, goal)
    macros = calculate_macros(daily_calories, goal)
    
    # Calculate calories per meal (with some variation)
    calories_per_meal = daily_calories / meals_per_day
    
    # Generate meal plan
    meal_plan = {
        "user": user_data.get('name', 'User'),
        "daily_calories": daily_calories,
        "macros": macros,
        "days": []
    }
    
    for day in range(1, days + 1):
        day_plan = {
            "day": day,
            "meals": [],
            "total_calories": 0,
            "total_protein": 0,
            "total_carbs": 0,
            "total_fat": 0
        }
        
        # Determine daily exercise based on day of the week
        day_of_week = day % 7  # Convert to 0-6 for days of the week
        
        if day_of_week in [1, 3, 5]:  # Monday, Wednesday, Friday
            day_plan["exercise_focus"] = "Strength Training"
        elif day_of_week in [2, 6]:  # Tuesday, Saturday
            day_plan["exercise_focus"] = "Cardio"
        elif day_of_week == 4:  # Thursday
            day_plan["exercise_focus"] = "Flexibility & Mobility"
        else:  # Sunday
            day_plan["exercise_focus"] = "Rest & Recovery"
        
        # Generate meals for the day
        remaining_calories = daily_calories
        
        for meal_num in range(1, meals_per_day + 1):
            # Calculate target calories for this meal
            if meal_num == meals_per_day:
                # Last meal gets remaining calories
                target_calories = remaining_calories
            else:
                # Add some variation to meal calories
                variation = np.random.uniform(0.8, 1.2)
                target_calories = (calories_per_meal * variation)
                # Ensure we don't exceed remaining calories
                target_calories = min(target_calories, remaining_calories)
            
            # Find foods that fit within the target calories
            # We'll use a simple approach: select foods randomly that add up to target calories
            meal_foods = []
            meal_calories = 0
            meal_protein = 0
            meal_carbs = 0
            meal_fat = 0
            
            # Shuffle the food list to get variety
            foods_shuffled = filtered_foods.sample(frac=1)
            
            # Select 2-4 foods for the meal
            num_foods = np.random.randint(2, 5)
            
            # Try to find foods that add up to target calories
            for i in range(min(len(foods_shuffled), 50)):  # Limit search to 50 foods
                food = foods_shuffled.iloc[i]
                food_calories = food.get('Calories', 0)
                
                # Skip foods with missing calorie data
                if pd.isna(food_calories) or food_calories <= 0:
                    continue
                
                # If adding this food keeps us within or close to target calories, add it
                if len(meal_foods) < num_foods and meal_calories + food_calories <= target_calories * 1.1:
                    meal_foods.append({
                        "name": food.get('Food Name', f"Food {i}"),
                        "calories": food_calories,
                        "protein": food.get('Protein', 0),
                        "carbs": food.get('Carbs', 0),
                        "fat": food.get('Total Fat', 0)
                    })
                    
                    meal_calories += food_calories
                    meal_protein += food.get('Protein', 0)
                    meal_carbs += food.get('Carbs', 0)
                    meal_fat += food.get('Total Fat', 0)
                
                # If we have enough foods or are close enough to target calories, stop
                if len(meal_foods) >= num_foods and meal_calories >= target_calories * 0.8:
                    break
            
            # Create meal object
            meal = {
                "meal_number": meal_num,
                "meal_name": get_meal_name(meal_num, meals_per_day),
                "foods": meal_foods,
                "calories": meal_calories,
                "protein": meal_protein,
                "carbs": meal_carbs,
                "fat": meal_fat
            }
            
            day_plan["meals"].append(meal)
            day_plan["total_calories"] += meal_calories
            day_plan["total_protein"] += meal_protein
            day_plan["total_carbs"] += meal_carbs
            day_plan["total_fat"] += meal_fat
            
            remaining_calories -= meal_calories
        
        meal_plan["days"].append(day_plan)
    
    return meal_plan

def get_meal_name(meal_number, total_meals):
    """
    Get a meal name based on the meal number and total meals per day
    """
    if total_meals == 3:
        meal_names = {1: "Breakfast", 2: "Lunch", 3: "Dinner"}
        return meal_names.get(meal_number, f"Meal {meal_number}")
    elif total_meals == 5:
        meal_names = {1: "Breakfast", 2: "Morning Snack", 3: "Lunch", 4: "Afternoon Snack", 5: "Dinner"}
        return meal_names.get(meal_number, f"Meal {meal_number}")
    else:
        if meal_number == 1:
            return "Breakfast"
        elif meal_number == total_meals:
            return "Dinner"
        elif meal_number == (total_meals // 2) + 1:
            return "Lunch"
        elif meal_number < (total_meals // 2) + 1:
            return f"Morning Meal {meal_number}"
        else:
            return f"Afternoon Meal {meal_number}"

def recommend_foods_by_goal(user_data, food_data, num_recommendations=10):
    """
    Recommend foods based on user's fitness goal
    
    Parameters:
    - user_data: Dict containing user information
    - food_data: DataFrame with food nutrition data
    - num_recommendations: Number of foods to recommend
    
    Returns:
    - List of recommended foods
    """
    # Filter foods based on dietary preference
    filtered_foods = filter_foods_by_preference(food_data, user_data.get('diet', 'both'))
    
    if filtered_foods.empty:
        return []
    
    goal = user_data.get('goal', '').lower()
    
    # Assign scores to each food based on goal
    scores = []
    
    for _, food in filtered_foods.iterrows():
        score = 0
        
        # Skip foods with missing data
        if pd.isna(food.get('Calories', 0)) or food.get('Calories', 0) <= 0:
            scores.append(-1)  # Low score for foods with missing data
            continue
        
        # Weight Loss: Favor foods with high protein, low calories, high fiber
        if 'weight loss' in goal:
            protein_per_calorie = food.get('Protein', 0) / max(food.get('Calories', 1), 1)
            fiber_per_calorie = food.get('Dietary Fiber', 0) / max(food.get('Calories', 1), 1)
            
            score = (protein_per_calorie * 5) + (fiber_per_calorie * 3) - (food.get('Sugar', 0) * 0.1)
        
        # Weight Gain: Favor foods with high calories, balanced macros
        elif 'weight gain' in goal:
            calorie_density = food.get('Calories', 0) / 100  # per 100g
            protein_ratio = food.get('Protein', 0) / max(food.get('Calories', 1), 1)
            
            score = (calorie_density * 3) + (protein_ratio * 2)
        
        # Muscle Gain: Favor foods high in protein and moderate calories
        elif 'muscle gain' in goal:
            protein_content = food.get('Protein', 0)
            protein_ratio = protein_content / max(food.get('Calories', 1), 1)
            
            score = (protein_content * 2) + (protein_ratio * 5)
        
        # Maintain Weight: Favor balanced, nutrient-dense foods
        else:
            nutrition_density = (
                food.get('Protein', 0) +
                food.get('Dietary Fiber', 0) * 2 +
                (food.get('Nutrition Density', 0) / 100)
            ) / max(food.get('Calories', 1), 1)
            
            score = nutrition_density * 5
        
        scores.append(score)
    
    # Add scores to the dataframe
    filtered_foods_with_scores = filtered_foods.copy()
    filtered_foods_with_scores['score'] = scores
    
    # Sort by score and get top recommendations
    top_recommendations = filtered_foods_with_scores.sort_values('score', ascending=False).head(num_recommendations)
    
    # Convert to list of dictionaries
    recommendations = []
    for _, food in top_recommendations.iterrows():
        if food.get('score', 0) > 0:  # Only include foods with positive scores
            recommendations.append({
                "name": food.get('Food Name', 'Unknown Food'),
                "calories": food.get('Calories', 0),
                "protein": food.get('Protein', 0),
                "carbs": food.get('Carbs', 0),
                "fat": food.get('Total Fat', 0),
                "score": food.get('score', 0)
            })
    
    return recommendations

def recommend_exercises(user_data, exercise_data, num_recommendations=5):
    """
    Recommend exercises based on user's fitness goal and health status
    
    Parameters:
    - user_data: Dict containing user information
    - exercise_data: DataFrame with exercise data
    - num_recommendations: Number of exercises to recommend
    
    Returns:
    - Dict containing recommended exercises by category
    """
    if exercise_data.empty:
        return {"error": "No exercise data available"}
    
    goal = user_data.get('goal', '').lower()
    health_status = user_data.get('health_status', '').lower()
    health_conditions = user_data.get('health_conditions', '').lower()
    
    # Determine appropriate exercise intensity based on health status
    low_intensity = ('underweight' in health_status or 
                    'obese' in health_status or 
                    any(condition in health_conditions for condition in ['heart', 'diabetes', 'respiratory', 'joint']))
    
    # Select exercises based on goal and intensity
    if 'weight loss' in goal:
        # Weight loss: mix of cardio, flexibility, and some strength
        weights = {'Cardio': 0.5, 'Flexibility': 0.3, 'Strength': 0.2}
    elif 'muscle gain' in goal:
        # Muscle gain: emphasis on strength training
        weights = {'Strength': 0.7, 'Cardio': 0.1, 'Flexibility': 0.2}
    else:
        # Balanced approach for maintenance or other goals
        weights = {'Cardio': 0.3, 'Strength': 0.4, 'Flexibility': 0.3}
    
    # Initialize recommendations
    recommendations = {
        "Cardio": [],
        "Strength": [],
        "Flexibility": []
    }
    
    # Map exercise types to categories
    exercise_categories = {
        'Cardio': ['Cardio', 'HIIT', 'Aerobic'],
        'Strength': ['Strength', 'Resistance', 'Weight', 'Bodyweight'],
        'Flexibility': ['Stretch', 'Yoga', 'Mobility', 'Flexibility']
    }
    
    # Categorize exercises
    for _, exercise in exercise_data.iterrows():
        exercise_type = exercise.get('Equipment Type', '').strip()
        exercise_name = exercise.get('Exercise', '').strip()
        main_muscle = exercise.get('Main Muscle', '').strip()
        
        # Skip exercises with empty names
        if not exercise_name:
            continue
        
        # Categorize the exercise
        category = None
        for cat, keywords in exercise_categories.items():
            if any(keyword.lower() in exercise_type.lower() for keyword in keywords):
                category = cat
                break
        
        # Default to Strength if not categorized
        if not category:
            category = 'Strength'
        
        # Add exercise to appropriate category
        if len(recommendations[category]) < int(num_recommendations * weights[category]):
            recommendations[category].append({
                "name": exercise_name,
                "type": exercise_type,
                "main_muscle": main_muscle,
                "preparation": exercise.get('Preparation', ''),
                "execution": exercise.get('Execution', ''),
                "target_muscles": exercise.get('Target Muscles', ''),
                "synergist_muscles": exercise.get('Synergist Muscles', '')
            })
    
    # If any category is empty, fill with random exercises of that type
    for category, exercises in recommendations.items():
        if not exercises:
            # Get random exercises for this category
            category_exercises = [
                {
                    "name": exercise.get('Exercise', 'Unknown Exercise'),
                    "type": exercise.get('Equipment Type', ''),
                    "main_muscle": exercise.get('Main Muscle', ''),
                    "preparation": exercise.get('Preparation', ''),
                    "execution": exercise.get('Execution', ''),
                    "target_muscles": exercise.get('Target Muscles', ''),
                    "synergist_muscles": exercise.get('Synergist Muscles', '')
                }
                for _, exercise in exercise_data.sample(min(5, len(exercise_data))).iterrows()
                if exercise.get('Exercise', '')
            ]
            
            recommendations[category] = category_exercises[:int(num_recommendations * weights[category])]
    
    return recommendations
