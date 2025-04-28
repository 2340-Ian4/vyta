import google.generativeai as genai
from django.conf import settings
import os
import logging
import json

logger = logging.getLogger(__name__)

def get_workout_suggestions(context):
    """Get personalized workout suggestions using Gemini API."""
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
        
        # Prepare the prompt for Gemini
        prompt = f"""
        You are a fitness expert. Generate 3 personalized workout suggestions for a user with the following profile:
        
        User Profile:
        - Fitness Level: {context['fitness_level']}
        - Goals: {', '.join(context['goals'])}
        - Preferences: {context['preferences']}
        
        For each workout, provide:
        1. Name (short description, less than 40 characters)
        2. Description (detailed workout plan)
        3. Duration (in minutes)
        4. Estimated calories burned
        
        Return the response as a JSON array with exactly this format:
        [
            {{
                "name": "Workout Name",
                "description": "Workout Description",
                "duration": duration_in_minutes,
                "calories": estimated_calories
            }}
        ]
        
        IMPORTANT: Your response must be a valid JSON array. Do not include any other text or explanations.
        """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        logger.info(f"Raw API response: {response.text}")
        
        # Parse the response
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                suggestions = json.loads(json_str)
                logger.info(f"Successfully parsed {len(suggestions)} workout suggestions")
                return suggestions
            else:
                logger.error("No JSON array found in API response")
                raise ValueError("Invalid API response format")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini API response as JSON: {str(e)}")
            logger.error(f"Response text: {response.text}")
            raise ValueError(f"Invalid JSON response from API: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in get_workout_suggestions: {str(e)}")
        raise 