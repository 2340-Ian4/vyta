import google.generativeai as genai
from django.conf import settings
import os
import logging
import json

logger = logging.getLogger(__name__)

def get_workout_suggestions(user_profile, goals_info):
    """
    Generate personalized workout suggestions using Gemini API
    """
    try:
        # Configure the Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
        
        # Create a model instance with the correct version
        model = genai.GenerativeModel('gemini-1.5-pro', generation_config={
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
        })
        
        # Prepare the prompt with user context
        goals_text = "\n".join([f"- {goal}" for goal in goals_info]) if goals_info else "- No active goals"
        
        prompt = f"""
        You are a fitness expert. Generate 3 personalized workout suggestions for a user with the following profile:
        
        User Profile:
        - Fitness Level: {user_profile.get_fitness_level_display()}
        - Recent Workouts: {user_profile.workouts_completed}
        - Active Minutes: {user_profile.active_minutes}
        - Calories Burned: {user_profile.calories_burned}
        
        Active Goals:
        {goals_text}
        
        For each workout, provide:
        1. Name that is a short description of the workout in less than 40 characters
        2. Description that MUST follow this exact format:
           "This workout targets [specific goal from user's goals].
           
           Warm-up (5-10 minutes):
           - [List specific warm-up exercises with duration/reps]
           
           Main Workout:
           1. [Exercise Name]
              - Sets: [number]
              - Reps: [number] or Duration: [time]
              - Weight: [specific weight or bodyweight]
              - Rest: [time between sets]
              - Form cues: [specific form instructions]
           
           2. [Exercise Name]
              - Sets: [number]
              - Reps: [number] or Duration: [time]
              - Weight: [specific weight or bodyweight]
              - Rest: [time between sets]
              - Form cues: [specific form instructions]
           
           [Continue for all exercises]
           
           Cool-down (5 minutes):
           - [List specific cool-down exercises with duration/reps]
           
           Notes:
           - [Any specific modifications based on fitness level]
           - [Equipment needed]
           - [Progression tips]"
        3. Duration (in minutes)
        4. Estimated calories burned
        
        IMPORTANT RULES:
        - Each workout must focus on ONE specific goal
        - You MUST provide the exact number of sets, reps, and rest periods
        - You MUST include specific weights or bodyweight modifications
        - You MUST include form cues for each exercise
        - You MUST include warm-up and cool-down exercises
        - You MUST specify equipment needed
        - You MUST include progression tips
        - Make the workout appropriate for the user's fitness level
        - For cardio workouts, specify exact intervals and intensities
        - For strength workouts, specify exact weights and rep ranges
        - For flexibility workouts, specify exact hold times and number of repetitions
        
        IMPORTANT: Your response must be a valid JSON array with exactly this format:
        [
            {{
                "name": "Workout Name",
                "description": "Workout Description",
                "duration": duration_in_minutes,
                "calories": estimated_calories
            }}
        ]
        
        Only return the JSON array, no other text.
        """
        
        logger.info("Sending prompt to Gemini API")
        # Generate response
        response = model.generate_content(prompt)
        logger.info("Received response from Gemini API")
        
        # Get the text from the response
        response_text = response.text.strip()
        logger.info(f"Raw response: {response_text}")
        
        # Try to parse the response as JSON
        try:
            suggestions = json.loads(response_text)
            logger.info(f"Successfully parsed {len(suggestions)} workout suggestions")
            return suggestions
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            # If JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                try:
                    suggestions = json.loads(json_match.group())
                    logger.info(f"Successfully parsed {len(suggestions)} workout suggestions from extracted JSON")
                    return suggestions
                except json.JSONDecodeError:
                    logger.error("Failed to parse extracted JSON")
                    raise
            
            # If all parsing attempts fail, raise the original error
            raise
        
    except Exception as e:
        logger.error(f"Error in get_workout_suggestions: {str(e)}")
        # Fallback to default suggestions if API fails
        return [
            {
                "name": "Full Body Workout",
                "description": "A 30-minute full-body workout focusing on strength and endurance.",
                "duration": 30,
                "calories": 150
            },
            {
                "name": "Cardio Blast",
                "description": "A 20-minute high-intensity cardio session to boost metabolism.",
                "duration": 20,
                "calories": 180
            },
            {
                "name": "Strength Training",
                "description": "A 40-minute strength training session targeting major muscle groups.",
                "duration": 40,
                "calories": 200
            }
        ] 