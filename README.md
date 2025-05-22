# devbio.com

**Generate Funky Developer Bios with Ease**

devbio.com is a lightweight Micro SaaS application that creates personalized, platform-specific developer bios using the Gemini AI API. Users input a description, select a bio length (Short, Medium, Larger), format (Plain Text or Markdown), and a developer platform (e.g., Stack Overflow, GitHub, LinkedIn), and the app generates a tailored bio with a creative twist.

## Features
- **Platform-Specific Bios**: Custom prompts for 13 platforms (Stack Overflow, GitHub, Dev.to, LinkedIn, Hashnode, Kaggle, Devpost, HackerEarth, MLH, Devfolio, DoraHacks, Unstop).
- **Flexible Lengths**: Short (~50 words), Medium (~100 words), or Larger (~200 words) bios.
- **Sleek UI**: Dark-themed interface with animated particles, responsive design, and a scrollable textarea.
- **Lightweight Backend**: Flask-based, no heavy NLP models, uses raw user descriptions with Gemini API.
- **Deployment-Ready**: Optimized for Heroku, Render, or AWS Lambda with minimal dependencies.

## Tech Stack
- **Backend**: Flask, Python, Google Gemini API (`gemini-2.5-preview`)
- **Frontend**: HTML, Tailwind CSS, custom CSS with animated particles
- **Dependencies**: `Flask`, `google-generativeai`, `python-dotenv`
- **Folder Structure**:
  ```
  devbiodotcom/
  ├── app.py
  ├── templates/index.html
  ├── static/styles.css
  ├── .env
  ├── requirements.txt
  ```

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd devbiodotcom
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment**:
   - Create `.env` in the root:
     ```
     GEMINI_API_KEY=your-api-key-here
     ```
   - Get the API key from [Google AI Studio](https://makersuite.google.com).

4. **Add Platform Logos**:
   - Place 32x32 PNG logos in `static/images/` (e.g., `stackoverflow.png`, `github.png`).

5. **Run Locally**:
   ```bash
   python app.py
   ```
   - Access at `http://localhost:5000`.


## Usage
- Enter a description (e.g., "Python, web dev, AI enthusiast").
- Choose bio length and format.
- Select a platform via buttons.
- View the generated bio in a styled output box.

## Future Enhancements
- Freemium model with Stripe for unlimited bios.
- Redis caching to reduce API calls.
- Neon PostgreSQL for user history.
- Additional platforms and bio styles.

---

Built with 💌 by ```Abhiraj Adhiakry``` for developers who want standout bios. Contributions welcome!