import streamlit as st
import pandas as pd
from utils.data_processing import load_food_data, filter_foods_by_preference, calculate_calorie_needs, calculate_macros
from utils.recommendations import  recommend_foods_by_goal,generate_meal_plan_with_cosine_similarity
from utils.user_management import get_user
from utils.visualization import create_macronutrient_chart, create_meal_plan_calories_chart, create_nutrient_comparison_chart

def main():
    st.title("🍽️ Meal Planner")
    
    # Check if user is logged in
    if 'current_user' not in st.session_state or st.session_state.current_user is None:
        st.error("Please log in to access the meal planner.")
        return
    # Get user data
    user_id = st.session_state.current_user
    user_data = get_user(user_id)
    
    if not user_data:
        st.error(f"User profile not found. Please create a new profile.")
        return
    
    # Display user info
    st.subheader(f"Meal Planning for {user_data.get('name', 'User').title()}")
    
    user_col1, user_col2, user_col3 = st.columns(3)
    
    with user_col1:
        st.markdown(f"**Goal:** {user_data.get('goal', 'Not specified')}")
    
    with user_col2:
        st.markdown(f"**Diet:** {user_data.get('diet', 'Not specified').capitalize()}")
    
    with user_col3:
        # Calculate estimated calorie needs
        weight = user_data.get('weight', 70)
        height = user_data.get('height', 170)
        gender = user_data.get('gender', 'male')
        goal = user_data.get('goal', 'Maintain Weight')
        age = user_data.get('age', 30)  # Default age if not available
        activity_level = user_data.get('activity_level', 'moderately_active')  # Default activity level
        
        daily_calories = calculate_calorie_needs(weight, height, age, gender, activity_level, goal)
        st.markdown(f"**Estimated Calories:** {daily_calories} kcal/day")
    
    # Calculate macronutrient distribution
    macros = calculate_macros(daily_calories, goal)
    
    # Display macronutrient chart
    st.subheader("Recommended Macronutrient Distribution")
    macro_fig = create_macronutrient_chart(macros)
    st.plotly_chart(macro_fig, use_container_width=True)
    
    # Meal plan generator form
    st.subheader("Generate Meal Plan")
    
    with st.form(key="meal_plan_form"):
        col1, col2 = st.columns(2)
        days = st.slider("Number of Days", min_value=1, max_value=30, value=7)
        meals_per_day = st.slider("Meals per Day", min_value=3, max_value=6, value=3)
    
           
        
        generate_button = st.form_submit_button(label="Generate Meal Plan")
        
        if generate_button:
        
            # Update user data with overrides
            user_data_copy = user_data.copy()
            
            # Generate meal plan
            with st.spinner("Generating your personalized meal plan..."):
                st.session_state.current_meal_plan = generate_meal_plan_with_cosine_similarity(
                    user_data_copy,
                    st.session_state.food_data,
                    days=days,
                    meals_per_day=meals_per_day
                )
                
    # Display meal plan outside the form
    if 'current_meal_plan' in st.session_state:
        meal_plan = st.session_state.current_meal_plan
        
        if "error" in meal_plan:
            st.error(meal_plan["error"])
        else:
            display_meal_plan(meal_plan)
            
            # Add download buttons outside the form and display_meal_plan function
            st.subheader("Save Your Meal Plan")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Create text data for download
                plan_text = convert_plan_to_text(meal_plan)
                
                st.download_button(
                    label="Download as Text",
                    data=plan_text,
                    file_name="meal_plan.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Create shopping list for download
                shopping_list = create_shopping_list(meal_plan)
                
                st.download_button(
                    label="Download Shopping List",
                    data=shopping_list,
                    file_name="shopping_list.txt",
                    mime="text/plain"
                )
            
            with col3:
                if st.button("Print Meal Plan"):
                    st.info("Use your browser's print function (Ctrl+P or ⌘+P) to print this page.")
                    
            # Display shopping list in a collapsible section
            with st.expander("View Shopping List"):
                st.markdown("### Shopping List for Your Meal Plan")
                st.text(shopping_list)
    
    # Food recommendations based on goal
    st.subheader("Recommended Foods Based on Your Goal")
    
    with st.spinner("Finding the best foods for your goal..."):
        recommended_foods = recommend_foods_by_goal(user_data, st.session_state.food_data, num_recommendations=10)
    
    if recommended_foods:
        # Display top recommended foods
        st.markdown(f"Here are some foods that align well with your **{user_data.get('goal', 'goal')}**:")
        
        # Create columns for food cards
        food_cols = st.columns(2)
        
        for i, food in enumerate(recommended_foods[:6]):  # Show top 6 foods
            with food_cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"### {food['name']}")
                    st.markdown(f"**Calories:** {food['calories']:.0f} kcal")
                    st.markdown(f"**Protein:** {food['protein']:.1f}g")
                    st.markdown(f"**Carbs:** {food['carbs']:.1f}g")
                    st.markdown(f"**Fat:** {food['fat']:.1f}g")
        
        # Show protein comparison for all recommended foods
        st.subheader("Protein Content Comparison")
        protein_fig = create_nutrient_comparison_chart(recommended_foods, "Protein")
        st.plotly_chart(protein_fig, use_container_width=True)
    else:
        st.info("No food recommendations available. Try updating your profile with more information.")
    
    # Search food database
    st.subheader("Food Database Search")
    
    search_query = st.text_input("Search for a food:", placeholder="e.g., chicken, apple, rice")
    
    if search_query:
        # Filter foods based on query
        query_lower = search_query.lower()
        filtered_foods = st.session_state.food_data[
            st.session_state.food_data["Food Name"].str.lower().str.contains(query_lower, na=False)
        ]
        
        if filtered_foods.empty:
            st.info(f"No foods found matching '{search_query}'.")
        else:
            # Display results
            st.markdown(f"Found {len(filtered_foods)} results for '{search_query}':")
            
            # Create a DataFrame for display
            display_df = filtered_foods[['Food Name', 'Calories', 'Protein', 'Carbs', 'Total Fat']].copy()
            display_df.columns = ['Food Name', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)']
            
            # Round numeric columns
            for col in ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)']:
                display_df[col] = display_df[col].round(1)
            
            st.dataframe(display_df, use_container_width=True)

def display_meal_plan(meal_plan):
    """
    Display the generated meal plan
    """
    st.subheader(f"Your {len(meal_plan['days'])}-Day Meal Plan")
    
    # Display overall plan metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("Daily Calorie Target", f"{meal_plan['daily_calories']} kcal")
    
    with metrics_col2:
        avg_calories = sum(day['total_calories'] for day in meal_plan['days']) / len(meal_plan['days'])
        st.metric("Average Daily Calories", f"{avg_calories:.0f} kcal")
    
    with metrics_col3:
        avg_protein = sum(day['total_protein'] for day in meal_plan['days']) / len(meal_plan['days'])
        st.metric("Average Daily Protein", f"{avg_protein:.1f} g")
    
    # Display calories chart
    calories_fig = create_meal_plan_calories_chart(meal_plan)
    st.plotly_chart(calories_fig, use_container_width=True)
    
    # Display meal plan details with tabs for each day
    day_tabs = st.tabs([f"Day {day['day']}" for day in meal_plan['days']])
    
    for i, day in enumerate(meal_plan['days']):
        with day_tabs[i]:
            # Display day summary
            st.markdown(f"**Total Calories:** {day['total_calories']:.0f} kcal")
            st.markdown(f"**Macros:** Protein: {day['total_protein']:.1f}g, Carbs: {day['total_carbs']:.1f}g, Fat: {day['total_fat']:.1f}g")
            
            if 'exercise_focus' in day:
                st.markdown(f"**Exercise Focus:** {day['exercise_focus']}")
            
            # Display meals
            for meal in day['meals']:
                with st.expander(f"{meal['meal_name']}  kcal"):
                    # Create a table for the foods in this meal
                    if meal['foods']:
                        food_data = []
                        for food in meal['foods']:
                            food_data.append([
                                food['name'],
                                f"{food['calories']:.0f} kcal",
                                f"{food['protein']:.1f}g",
                                f"{food['carbs']:.1f}g",
                                f"{food['fat']:.1f}g"
                            ])
                        
                        food_df = pd.DataFrame(
                            food_data,
                            columns=['Food', 'Calories', 'Protein', 'Carbs', 'Fat']
                        )
                        
                        st.table(food_df)
                    else:
                        st.info("No foods selected for this meal.")
    # Meal plan display contains only visualization, no download buttons to avoid form issues

def convert_plan_to_text(meal_plan):
    """
    Convert the meal plan to a text format for download
    """
    text = f"MEAL PLAN FOR {meal_plan['user'].upper()}\n"
    text += "=" * 50 + "\n\n"
    
    text += f"Daily Calorie Target: {meal_plan['daily_calories']} kcal\n"
    text += f"Protein: {meal_plan['macros']['protein']}g, Carbs: {meal_plan['macros']['carbs']}g, Fat: {meal_plan['macros']['fat']}g\n\n"
    
    for day in meal_plan['days']:
        text += f"DAY {day['day']}\n"
        text += "-" * 30 + "\n"
        text += f"Total Calories: {day['total_calories']:.0f} kcal\n"
        text += f"Protein: {day['total_protein']:.1f}g, Carbs: {day['total_carbs']:.1f}g, Fat: {day['total_fat']:.1f}g\n"
        
        if 'exercise_focus' in day:
            text += f"Exercise Focus: {day['exercise_focus']}\n"
        
        text += "\n"
        
        for meal in day['meals']:
            text += f"{meal['meal_name']}\n"
            
            for food in meal['foods']:
                text += f"  • {food['name']} - {food['calories']:.0f} kcal (P: {food['protein']:.1f}g, C: {food['carbs']:.1f}g, F: {food['fat']:.1f}g)\n"
            
            text += "\n"
        
        text += "\n"
    
    return text

def create_shopping_list(meal_plan):
    """
    Create a shopping list from the meal plan
    
    Parameters:
    - meal_plan: The generated meal plan dictionary
    
    Returns:
    - A formatted shopping list as a string
    """
    # Dictionary to track all unique food items and their quantities
    shopping_items = {}
    
    # Process each day in the meal plan
    for day in meal_plan['days']:
        for meal in day['meals']:
            for food in meal['foods']:
                food_name = food['name']
                
                # If the food is already in our list, just increment the count
                if food_name in shopping_items:
                    shopping_items[food_name]['count'] += 1
                else:
                    # Otherwise, add it as a new item
                    shopping_items[food_name] = {
                        'count': 1,
                        'category': categorize_food(food_name)
                    }
    
    # Create the shopping list text
    text = "SHOPPING LIST\n"
    text += "=" * 50 + "\n\n"
    
    # Group by category
    categorized_items = {}
    
    for food_name, details in shopping_items.items():
        category = details['category']
        if category not in categorized_items:
            categorized_items[category] = []
        
        categorized_items[category].append((food_name, details['count']))
    
    # Sort categories alphabetically
    for category in sorted(categorized_items.keys()):
        text += f"--- {category.upper()} ---\n"
        
        # Sort items within each category alphabetically
        items = sorted(categorized_items[category], key=lambda x: x[0])
        
        for item, count in items:
            text += f"[ ] {item} (x{count})\n"
        
        text += "\n"
    
    # Add a note about checking quantities
    text += "\nNote: This shopping list shows the number of times each item appears in your meal plan.\n"
    text += "You may need to adjust quantities based on your specific recipes and portion sizes.\n"
    
    return text

def categorize_food(food_name):
    """
    Categorize a food item for the shopping list
    
    Parameters:
    - food_name: The name of the food
    
    Returns:
    - Category string
    """
    # Convert to lowercase for case-insensitive matching
    food_lower = food_name.lower()
    
    # Define categories and their keywords
    categories = {
        'Fruits': ['apple', 'banana', 'orange', 'berries', 'fruit', 'pear', 'peach', 'grape'],
        'Vegetables': ['broccoli', 'spinach', 'lettuce', 'carrot', 'tomato', 'onion', 'potato', 'vegetable', 'salad', 'pepper', 'cucumber'],
        'Meat & Seafood': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'tuna', 'meat', 'turkey', 'lamb'],
        'Dairy & Eggs': ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'egg'],
        'Grains & Bread': ['bread', 'rice', 'pasta', 'oats', 'cereal', 'flour', 'grain', 'wheat', 'barley', 'quinoa'],
        'Legumes & Nuts': ['beans', 'lentils', 'peanut', 'almond', 'cashew', 'nut', 'seed', 'tofu'],
        'Snacks & Sweets': ['chocolate', 'cookie', 'cake', 'snack', 'chips', 'candy', 'dessert', 'sweet'],
        'Beverages': ['water', 'juice', 'coffee', 'tea', 'drink', 'beverage', 'smoothie'],
        'Oils & Condiments': ['oil', 'vinegar', 'sauce', 'dressing', 'mayonnaise', 'ketchup', 'mustard', 'honey', 'syrup']
    }
    
    # Check each category for matches
    for category, keywords in categories.items():
        if any(keyword in food_lower for keyword in keywords):
            return category
    
    # Default category for unmatched items
    return "Other"

if __name__ == "__main__":
    main()
