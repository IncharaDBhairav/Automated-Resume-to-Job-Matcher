import os
import re
from flask import Flask, request, jsonify, render_template
import pdfplumber
import spacy

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

# Ensure uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the NLP model (this is the brain you downloaded earlier!)
print("Loading AI Model...")
nlp = spacy.load("en_core_web_sm")
print("Model Loaded. SkillSync is ready.")

# Define the domains and their keywords
CAREER_DOMAINS = {
    "Web Development": ["html", "css", "javascript", "react", "node", "flask", "django", "tailwind", "frontend", "backend", "full stack"],
    "AI/ML": ["python", "machine learning", "ai", "opencv", "computer vision", "nlp", "spacy", "deep learning", "tensorflow", "pytorch"],
    "Data Science": ["sql", "python", "pandas", "numpy", "data analysis", "tableau", "statistics", "database", "dbms"],
    "Cloud Computing": ["aws", "azure", "gcp", "docker", "kubernetes", "cloud", "deployment"],
    "DevOps": ["jenkins", "ci/cd", "git", "linux", "bash", "automation", "docker"]
}

# Master list of skills to look out for
KNOWN_SKILLS = ["python", "java", "c++", "sql", "javascript", "html", "css", "react", "flask", "django", "machine learning", "artificial intelligence", "computer vision", "nlp", "opencv", "dbms", "git"]

def analyze_text(text):
    text_lower = text.lower()
    
    # 1. Extract Skills
    found_skills = list(set([skill.title() for skill in KNOWN_SKILLS if skill in text_lower]))
    
    # 2. Calculate Domain Matching Score
    domain_scores = {}
    for domain, keywords in CAREER_DOMAINS.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        # Normalize score (max 5 points gives 100%)
        domain_scores[domain] = min(score / 5.0, 1.0) 
    
    # 3. Extract Projects (Basic keyword matching for demo)
    projects = []
    if "management system" in text_lower:
        projects.append({"description": "Database Management / Information System Project"})
    if "ai" in text_lower or "recognition" in text_lower or "invigilator" in text_lower:
        projects.append({"description": "Artificial Intelligence / Computer Vision Application"})
    if "3d" in text_lower or "model" in text_lower:
        projects.append({"description": "Modeling / Generation Tool"})
        
    # 4. Extract Experience (Basic matching)
    experiences = []
    if "intern" in text_lower or "internship" in text_lower:
        experiences.append({"title": "Technical Intern", "company": "Tech Industry"})

    return found_skills, domain_scores, projects, experiences


@app.route('/')
def home():
    # Renders your beautiful index.html
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['resume']
    job_type = request.form.get('jobType', 'job') # Defaults to job if not found
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Extract text from PDF
        extracted_text = ""
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() + " "
                    
            # Run the AI Analysis
            skills, domains, projects, experiences = analyze_text(extracted_text)
            
            # Prepare the exact JSON structure the frontend expects
            response_data = {
                "analysis": {
                    "job_type": job_type,
                    "skills": skills,
                    "career_domains": domains,
                    "projects": projects,
                    "experiences": experiences
                }
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
            
    return jsonify({'error': 'Invalid file format. Please upload a PDF.'}), 400

if __name__ == '__main__':
    app.run(debug=True)