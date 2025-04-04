from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np
import PyPDF2
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
 
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_and_split_text(text):
    text = re.sub(r'\n+', '\n', text)
    skills_match = re.search(r'(Skills|SKILLS)(.*?)(Education|EDUCATION|$)', text, re.DOTALL)
    education_match = re.search(r'(Education|EDUCATION)(.*?)($)', text, re.DOTALL)
    skills = skills_match.group(2).strip() if skills_match else ""
    education = education_match.group(2).strip() if education_match else ""
    return skills, education

@app.route('/process_resumes', methods=['POST'])
def process_resumes():
    files = request.files.getlist("files")
    job_skills = request.form['skills']
    job_education = request.form['education']
    print("Hey in process_resumes")
    
    scores = []
    for file in files:
        text = extract_text_from_pdf(file)
        skills, education = clean_and_split_text(text)
        vectorizer = CountVectorizer().fit_transform([job_skills, skills])
        vectors = vectorizer.toarray()
        cosine_sim = cosine_similarity(vectors)[0][1]
        scores.append({'name': file.filename, 'score': cosine_sim * 100})
    
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_scores)

if __name__ == '__main__':
    app.run(port=5000)
