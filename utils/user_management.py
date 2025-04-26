import json
import pandas as pd
import numpy as np
from datetime import datetime
from utils.data_processing import calculate_bmi, save_user_records, load_user_records

def create_new_user(first_name, last_name, gender, age, height, weight, diet, goal, activity_level, allergies, preferred_cuisines, health_conditions):
    """
    Create a new user record
    
    Parameters:
    - first_name: User's first name
    - last_name: User's last name
    - gender: User's gender
    - age: User's age
    - height: Height in cm
    - weight: Weight in kg
    - diet: Diet preference
    - goal: Fitness goal
    - activity_level: Activity level (Sedentary, Lightly Active, etc.)
    - allergies: List of food allergies
    - preferred_cuisines: List of preferred cuisines
    - health_conditions: Any health conditions
    
    Returns:
    - Tuple: (success, message, user_id)
    """
    try:
        # Load existing records
        user_records = load_user_records()
        
        # Create name
        name = f"{first_name.strip().lower()} {last_name.strip().lower()}"
        
        # Calculate BMI
        bmi, health_status = calculate_bmi(weight, height)
        
        # Generate a new user ID
        records = user_records.get("records", {})
        new_id = str(len(records) + 1)
        
        # Create new user record
        new_user = {
            "name": name,
            "gender": gender.lower(),
            "age": int(age),
            "height": float(height),
            "weight": float(weight),
            "bmi": bmi,
            "goal": goal,
            "diet": diet,
            "activity_level": activity_level,
            "allergies": allergies,
            "preferred_cuisines": preferred_cuisines,
            "health_conditions": health_conditions,
            "progress_history": [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "weight": float(weight),
                    "bmi": bmi
                }
            ],
            "health_status": health_status
        }
        
        # Add to records
        records[new_id] = new_user
        user_records["records"] = records
        
        # Save updated records
        save_success = save_user_records(user_records)
        
        if save_success:
            return True, f"Record {new_id} inserted successfully!", new_id
        else:
            return False, "Failed to save user record.", None
            
    except Exception as e:
        return False, f"Error creating user: {str(e)}", None

def update_user(user_id, data):
    """
    Update an existing user record
    
    Parameters:
    - user_id: ID of the user to update
    - data: Dict containing fields to update
    
    Returns:
    - Tuple: (success, message)
    """
    try:
        # Load existing records
        user_records = load_user_records()
        
        # Check if user exists
        records = user_records.get("records", {})
        if user_id not in records:
            return False, f"User ID {user_id} not found."
        
        # Get current user data
        user_data = records[user_id]
        
        # Update fields
        for key, value in data.items():
            user_data[key] = value
        
        # Recalculate BMI if height or weight were updated
        if 'height' in data or 'weight' in data:
            height = user_data['height']
            weight = user_data['weight']
            # Calculate new BMI
            height = user_data['height']
            age = user_data['age']  
            gender = user_data['gender']
            bmi = weight / ((height / 100) ** 2)
            health_status = "Healthy" if 18.5 <= bmi < 24.9 else "Underweight" if bmi < 18.5 else "Overweight" if 24.9 <= bmi < 29.9 else "Obese"
            user_data['bmi'] = bmi
            user_data['health_status'] = health_status
        
        # Update record
        records[user_id] = user_data
        user_records["records"] = records
        
        # Save updated records
        save_success = save_user_records(user_records)
        
        if save_success:
            return True, f"User {user_id} updated successfully!"
        else:
            return False, "Failed to save user record."
            
    except Exception as e:
        return False, f"Error updating user: {str(e)}"

def delete_user(user_id):
    """
    Delete a user record
    
    Parameters:
    - user_id: ID of the user to delete
    
    Returns:
    - Tuple: (success, message)
    """
    try:
        # Load existing records
        user_records = load_user_records()
        
        # Check if user exists
        records = user_records.get("records", {})
        if user_id not in records:
            return False, f"User ID {user_id} not found."
        
        # Delete record
        del records[user_id]
        user_records["records"] = records
        
        # Save updated records
        save_success = save_user_records(user_records)
        
        if save_success:
            return True, f"User {user_id} deleted successfully!"
        else:
            return False, "Failed to save user record."
            
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"

def get_user(user_id):
    """
    Get a user record
    
    Parameters:
    - user_id: ID of the user to retrieve
    
    Returns:
    - User data dict or None if not found
    """
    try:
        # Load records
        user_records = load_user_records()
        
        # Get user data
        records = user_records.get("records", {})
        return records.get(user_id)
            
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def update_user_progress(user_id, weight):
    """
    Add a new progress entry for a user
    
    Parameters:
    - user_id: ID of the user
    - weight: New weight in kg
    
    Returns:
    - Tuple: (success, message)
    """
    try:
        # Load existing records
        user_records = load_user_records()
        
        # Check if user exists
        records = user_records.get("records", {})
        if user_id not in records:
            return False, f"User ID {user_id} not found."
        
        # Get current user data
        user_data = records[user_id]
        
        # Calculate new BMI
        height = user_data['height']
        age = user_data['age']  
        gender = user_data['gender']
        bmi = weight / ((height / 100) ** 2)
        health_status = "Healthy" if 18.5 <= bmi < 24.9 else "Underweight" if bmi < 18.5 else "Overweight" if 24.9 <= bmi < 29.9 else "Obese"
    
        
        # Create progress entry
        progress_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "weight": float(weight),
            "bmi": bmi
        }
        
        # Add to progress history
        if 'progress_history' not in user_data:
            user_data['progress_history'] = []
        
        user_data['progress_history'].append(progress_entry)
        
        # Update current weight and BMI
        old_weight = user_data.get('weight', 0)
        old_bmi = user_data.get('bmi', 0)
        
        user_data['weight'] = float(weight)
        user_data['bmi'] = bmi
        user_data['health_status'] = health_status
        
        # Update record
        records[user_id] = user_data
        user_records["records"] = records
        
        # Save updated records
        save_success = save_user_records(user_records)
        
        if save_success:
            return True, f"Progress updated! Previous: {old_weight}kg (BMI: {old_bmi}), New: {weight}kg (BMI: {bmi})"
        else:
            return False, "Failed to save progress."
            
    except Exception as e:
        return False, f"Error updating progress: {str(e)}"

def get_all_users():
    """
    Get all user records
    
    Returns:
    - Dict of all user records
    """
    try:
        # Load records
        user_records = load_user_records()
        
        # Return all records
        return user_records.get("records", {})
            
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return {}
