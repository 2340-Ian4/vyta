import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=api_key)

# List all models
print("\nAvailable Models:")
print("----------------")
for model in genai.list_models():
    print(f"\nModel: {model.name}")
    print(f"Display Name: {model.display_name}")
    print(f"Description: {model.description}")
    print(f"Generation Methods: {model.supported_generation_methods}")
    print("-" * 50) 