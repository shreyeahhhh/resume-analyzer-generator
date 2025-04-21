import spacy
import PyPDF2
import docx
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class ResumeAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
        
    def extract_text(self, file_path):
        """Extract text from PDF or DOCX file"""
        if file_path.endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def _extract_from_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_skills(self, text):
        """Extract skills from text using spaCy"""
        doc = self.nlp(text)
        skills = []
        
        # Extract skills using pattern matching
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECH']:
                skills.append(ent.text.lower())
        
        # Extract skills using keyword matching
        skill_keywords = ['skill', 'experience', 'proficient', 'knowledge', 'expertise']
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in skill_keywords):
                for token in sent:
                    if token.pos_ in ['NOUN', 'PROPN'] and token.text.lower() not in self.stop_words:
                        skills.append(token.text.lower())
        
        return list(set(skills))
    
    def extract_keywords(self, text):
        """Extract keywords using TF-IDF"""
        # Preprocess text
        words = re.findall(r'\w+', text.lower())
        words = [word for word in words if word not in self.stop_words]
        
        # Count word frequencies
        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(20)]
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts using cosine similarity"""
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    def analyze_resume(self, resume_path, job_description):
        """Analyze resume against job description"""
        # Extract text
        resume_text = self.extract_text(resume_path)
        
        # Extract skills and keywords
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        resume_keywords = self.extract_keywords(resume_text)
        job_keywords = self.extract_keywords(job_description)
        
        # Calculate scores
        skill_match = len(set(resume_skills) & set(job_skills)) / len(set(job_skills)) * 100
        keyword_match = len(set(resume_keywords) & set(job_keywords)) / len(set(job_keywords)) * 100
        ats_score = (skill_match * 0.6 + keyword_match * 0.4)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(resume_skills, job_skills, resume_keywords, job_keywords)
        
        return {
            'ats_score': round(ats_score, 2),
            'skill_match': round(skill_match, 2),
            'keyword_match': round(keyword_match, 2),
            'your_skills': resume_skills,
            'required_skills': job_skills,
            'suggestions': suggestions
        }
    
    def _generate_suggestions(self, resume_skills, job_skills, resume_keywords, job_keywords):
        """Generate improvement suggestions"""
        suggestions = []
        
        # Missing skills
        missing_skills = set(job_skills) - set(resume_skills)
        if missing_skills:
            suggestions.append(f"Add these missing skills: {', '.join(missing_skills)}")
        
        # Missing keywords
        missing_keywords = set(job_keywords) - set(resume_keywords)
        if missing_keywords:
            suggestions.append(f"Incorporate these keywords: {', '.join(missing_keywords)}")
        
        # Format suggestions
        if not suggestions:
            suggestions.append("Your resume looks good! Consider adding more specific achievements.")
        
        return suggestions 