import streamlit as st
import os
from dashboard.dashboard import DashboardManager
from utils.analyzer import ResumeAnalyzer
from utils.generator import ResumeGenerator
import tempfile
import traceback

class ResumeApp:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()
        self.generator = ResumeGenerator()
        self.dashboard = DashboardManager()
        
    def run(self):
        st.set_page_config(
            page_title="Resume Analyzer & Generator",
            page_icon="📄",
            layout="wide"
        )
        
        st.title("📄 Resume Analyzer & Generator")
        st.markdown("""
        <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px;'>
            <h3>Welcome to the Resume Analyzer & Generator!</h3>
            <p>Upload your resume and job description to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File Upload
        col1, col2 = st.columns(2)
        with col1:
            resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf', 'docx'])
        with col2:
            job_desc = st.text_area("Job Description", height=200)
            
        if resume_file and job_desc:
            try:
                # Save uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp_file:
                    tmp_file.write(resume_file.getvalue())
                    resume_path = tmp_file.name
                
                # Analyze Resume
                with st.spinner("Analyzing resume..."):
                    analysis = self.analyzer.analyze_resume(resume_path, job_desc)
                
                # Display Results
                self._display_results(analysis)
                
                # Generate Optimized Resume
                if st.button("Generate Optimized Resume"):
                    with st.spinner("Generating optimized resume..."):
                        self._generate_optimized_resume(analysis)
                
                # Clean up
                os.unlink(resume_path)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error(traceback.format_exc())
    
    def _display_results(self, analysis):
        st.subheader("Analysis Results")
        
        # ATS Score
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ATS Score", f"{analysis['ats_score']}%")
        with col2:
            st.metric("Skill Match", f"{analysis['skill_match']}%")
        with col3:
            st.metric("Keyword Match", f"{analysis['keyword_match']}%")
        
        # Skills Analysis
        st.subheader("Skills Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Your Skills**")
            st.write(analysis['your_skills'])
        with col2:
            st.write("**Required Skills**")
            st.write(analysis['required_skills'])
        
        # Suggestions
        st.subheader("Suggestions")
        for suggestion in analysis['suggestions']:
            st.write(f"- {suggestion}")
    
    def _generate_optimized_resume(self, analysis):
        try:
            optimized_resume = self.generator.generate_resume(analysis)
            st.success("Optimized resume generated successfully!")
            
            # Download button
            st.download_button(
                label="Download Optimized Resume",
                data=optimized_resume,
                file_name="optimized_resume.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate optimized resume: {str(e)}")

if __name__ == "__main__":
    app = ResumeApp()
    app.run() 