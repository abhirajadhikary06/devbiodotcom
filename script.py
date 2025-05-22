import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure the Gemini client
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Send a test prompt to verify if the model works
try:
    response = model.generate_content("Hello Gemini! Are you working?")
    print("✅ Gemini API is working.")
    print("Response:", response.text)
except Exception as e:
    print("❌ Failed to connect to Gemini API or generate response.")
    print("Error:", e)

#3b82f6