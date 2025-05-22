from flask import Flask, render_template, request, jsonify
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

app = Flask(__name__)

# Platform-specific prompt templates
PLATFORM_PROMPTS = {
    "Stack Overflow": {
        "Short": "Generate a concise, technical bio for a Stack Overflow profile. Use the description: '{description}'. If empty, use keywords: tech, coding, problem-solving. Focus on expertise and contributions. Keep it around {max_tokens} words.",
        "Medium": "Generate a technical bio for a Stack Overflow profile. Use the description: '{description}'. If empty, use keywords: tech, coding, problem-solving. Highlight expertise, contributions, and a helpful tone. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, technical bio for a Stack Overflow profile. Use the description: '{description}'. If empty, use keywords: tech, coding, problem-solving. Emphasize expertise, contributions, and community engagement with a professional tone. Keep it around {max_tokens} words."
    },
    "GitHub": {
        "Short": "Generate a concise, project-focused bio for a GitHub profile. Use the description: '{description}'. If empty, use keywords: open-source, coding, innovation. Highlight projects and contributions. Keep it around {max_tokens} words.",
        "Medium": "Generate a project-focused bio for a GitHub profile. Use the description: '{description}'. If empty, use keywords: open-source, coding, innovation. Showcase projects, contributions, and technical skills. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed bio for a GitHub profile. Use the description: '{description}'. If empty, use keywords: open-source, coding, innovation. Detail projects, contributions, and technical passions with a collaborative tone. Keep it around {max_tokens} words."
    },
    "Dev.to": {
        "Short": "Generate a concise, community-driven bio for a Dev.to profile. Use the description: '{description}'. If empty, use keywords: tech, blogging, community. Focus on sharing knowledge and enthusiasm. Keep it around {max_tokens} words.",
        "Medium": "Generate a community-driven bio for a Dev.to profile. Use the description: '{description}'. If empty, use keywords: tech, blogging, community. Highlight knowledge sharing and developer engagement. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, storytelling bio for a Dev.to profile. Use the description: '{description}'. If empty, use keywords: tech, blogging, community. Emphasize knowledge sharing, experiences, and community passion. Keep it around {max_tokens} words."
    },
    "LinkedIn": {
        "Short": "Generate a concise, professional bio for a LinkedIn profile. Use the description: '{description}'. If empty, use keywords: tech, leadership, innovation. Focus on career highlights and professionalism. Keep it around {max_tokens} words.",
        "Medium": "Generate a professional bio for a LinkedIn profile. Use the description: '{description}'. If empty, use keywords: tech, leadership, innovation. Highlight career achievements and skills with a polished tone. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, professional bio for a LinkedIn profile. Use the description: '{description}'. If empty, use keywords: tech, leadership, innovation. Detail career journey, achievements, and aspirations with a professional tone. Keep it around {max_tokens} words."
    },
    "Hashnode": {
        "Short": "Generate a concise, blogging-focused bio for a Hashnode profile. Use the description: '{description}'. If empty, use keywords: tech, writing, community. Focus on tech writing and passion. Keep it around {max_tokens} words.",
        "Medium": "Generate a blogging-focused bio for a Hashnode profile. Use the description: '{description}'. If empty, use keywords: tech, writing, community. Highlight writing passion and tech insights. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, storytelling bio for a Hashnode profile. Use the description: '{description}'. If empty, use keywords: tech, writing, community. Emphasize writing journey, tech insights, and community engagement. Keep it around {max_tokens} words."
    },
    "Kaggle": {
        "Short": "Generate a concise, data-focused bio for a Kaggle profile. Use the description: '{description}'. If empty, use keywords: data science, machine learning, analytics. Focus on data skills and competitions. Keep it around {max_tokens} words.",
        "Medium": "Generate a data-focused bio for a Kaggle profile. Use the description: '{description}'. If empty, use keywords: data science, machine learning, analytics. Highlight data projects and expertise. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, data-centric bio for a Kaggle profile. Use the description: '{description}'. If empty, use keywords: data science, machine learning, analytics. Detail data projects, competitions, and insights. Keep it around {max_tokens} words."
    },
    "Devpost": {
        "Short": "Generate a concise, project-centric bio for a Devpost profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Focus on hackathon achievements. Keep it around {max_tokens} words.",
        "Medium": "Generate a project-centric bio for a Devpost profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Highlight hackathon projects and creativity. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, project-focused bio for a Devpost profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Detail hackathon experiences and creative solutions. Keep it around {max_tokens} words."
    },
    "HackerEarth": {
        "Short": "Generate a concise, competitive bio for a HackerEarth profile. Use the description: '{description}'. If empty, use keywords: coding, competitions, tech. Focus on coding challenges and skills. Keep it around {max_tokens} words.",
        "Medium": "Generate a competitive bio for a HackerEarth profile. Use the description: '{description}'. If empty, use keywords: coding, competitions, tech. Highlight coding challenges and technical prowess. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, competitive bio for a HackerEarth profile. Use the description: '{description}'. If empty, use keywords: coding, competitions, tech. Detail coding achievements and problem-solving passion. Keep it around {max_tokens} words."
    },
    "Major League Hacking (MLH)": {
        "Short": "Generate a concise, hackathon-focused bio for a Major League Hacking (MLH) profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, community. Focus on hackathon participation. Keep it around {max_tokens} words.",
        "Medium": "Generate a hackathon-focused bio for a Major League Hacking (MLH) profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, community. Highlight hackathon experiences and teamwork. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, community-driven bio for a Major League Hacking (MLH) profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, community. Detail hackathon journey and community involvement. Keep it around {max_tokens} words."
    },
    "Devfolio": {
        "Short": "Generate a concise, hackathon-centric bio for a Devfolio profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Focus on hackathon projects. Keep it around {max_tokens} words.",
        "Medium": "Generate a hackathon-centric bio for a Devfolio profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Highlight hackathon achievements and creativity. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, project-focused bio for a Devfolio profile. Use the description: '{description}'. If empty, use keywords: hackathons, projects, innovation. Detail hackathon projects and innovative solutions. Keep it around {max_tokens} words."
    },
    "DoraHacks": {
        "Short": "Generate a concise, innovation-focused bio for a DoraHacks profile. Use the description: '{description}'. If empty, use keywords: blockchain, hackathons, innovation. Focus on innovative projects. Keep it around {max_tokens} words.",
        "Medium": "Generate an innovation-focused bio for a DoraHacks profile. Use the description: '{description}'. If empty, use keywords: blockchain, hackathons, innovation. Highlight innovative projects and technical skills. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, innovation-driven bio for a DoraHacks profile. Use the description: '{description}'. If empty, use keywords: blockchain, hackathons, innovation. Detail innovative projects and blockchain expertise. Keep it around {max_tokens} words."
    },
    "Unstop": {
        "Short": "Generate a concise, competitive bio for an Unstop profile. Use the description: '{description}'. If empty, use keywords: competitions, skills, tech. Focus on competitive achievements. Keep it around {max_tokens} words.",
        "Medium": "Generate a competitive bio for an Unstop profile. Use the description: '{description}'. If empty, use keywords: competitions, skills, tech. Highlight competitive achievements and skills. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, competitive bio for an Unstop profile. Use the description: '{description}'. If empty, use keywords: competitions, skills, tech. Detail competitive journey and technical expertise. Keep it around {max_tokens} words."
    },
    "Hack2skill": {
        "Short": "Generate a concise, hackathon-focused bio for a Hack2skill profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, innovation. Focus on hackathon wins. Keep it around {max_tokens} words.",
        "Medium": "Generate a hackathon-focused bio for a Hack2skill profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, innovation. Highlight hackathon projects and creativity. Keep it around {max_tokens} words.",
        "Larger": "Generate a detailed, hackathon-centric bio for a Hack2skill profile. Use the description: '{description}'. If empty, use keywords: hackathons, coding, innovation. Detail hackathon achievements and innovative solutions. Keep it around {max_tokens} words."
    }
}

# Function to call Gemini API with retries
def call_gemini_api(description, platform, length, format_type):
    length_map = {"Short": 20, "Medium": 70, "Larger": 200}
    max_tokens = length_map.get(length, 100)
    
    # Get platform-specific prompt
    prompt_template = PLATFORM_PROMPTS.get(platform, {}).get(length, (
        f"Generate a professional bio for a {platform} profile. "
        f"Use the description: '{description}'. If empty, use keywords: tech, innovative, code. "
        f"Keep it {length.lower()} (around {max_tokens} words). "
        f"Make it engaging and professional with a creative twist."
    ))
    prompt = prompt_template.format(description=description, max_tokens=max_tokens)

    print("Generated prompt:", prompt)  # Debug logging

    # Retry logic for API calls
    for attempt in range(3):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            response = model.generate_content(prompt)

            # Extract generated text
            generated_text = ""
            if hasattr(response, 'text') and response.text:
                generated_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                generated_text = response.candidates[0].content.parts[0].text
            else:
                print(f"Attempt {attempt + 1}: No valid response from Gemini")
                continue

            # Clean ** and truncate
            cleaned_response = re.sub(r'\*\*', '', generated_text)
            words = cleaned_response.split()
            truncated_response = ' '.join(words[:max_tokens])

            if format_type == "Markdown":
                return f"### {platform} Bio\n{truncated_response}"
            return truncated_response

        except Exception as e:
            print(f"Attempt {attempt + 1}: Gemini API error: {str(e)}")
            if attempt < 2:
                time.sleep(2)  # Wait before retrying
            continue
    
    # Fallback response after retries
    print("All retries failed, using fallback")
    fallback_response = (
        f"Professional {platform} Bio: Creative coder with a passion for tech. "
        f"Building innovative solutions with code. "
        f"{length} bio for {platform}! Let's connect!"
    )
    words = fallback_response.split()
    fallback_trimmed = ' '.join(words[:max_tokens])
    if format_type == "Markdown":
        return f"### {platform} Bio\n{fallback_trimmed}"
    return fallback_trimmed

@app.route('/')
def index():
    platforms = [
        "Stack Overflow", "GitHub", "Dev.to", "LinkedIn", "Hashnode",
        "Kaggle", "Devpost", "HackerEarth", "Major League Hacking (MLH)",
        "Devfolio", "DoraHacks", "Unstop", "Hack2skill"
    ]
    return render_template('index.html', platforms=platforms)

@app.route('/generate_bio', methods=['POST'])
def generate_bio():
    description = request.form.get('description')
    length = request.form.get('length')
    format_type = request.form.get('format')
    platform = request.form.get('platform')

    print("Received description:", description)  # Debug logging

    bio = call_gemini_api(description, platform, length, format_type)
    return jsonify({'bio': bio})

if __name__ == '__main__':
    app.run(debug=False)