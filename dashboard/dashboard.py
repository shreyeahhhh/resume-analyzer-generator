import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime

class DashboardManager:
    def __init__(self):
        self.conn = sqlite3.connect('resume_analysis.db')
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Create resume_data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TIMESTAMP,
            ats_score FLOAT,
            skill_match FLOAT,
            keyword_match FLOAT
        )
        ''')
        
        # Create resume_analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            analysis_date TIMESTAMP,
            suggestions TEXT,
            FOREIGN KEY (resume_id) REFERENCES resume_data (id)
        )
        ''')
        
        self.conn.commit()
    
    def save_analysis(self, filename, analysis):
        """Save analysis results to database"""
        cursor = self.conn.cursor()
        
        # Insert into resume_data
        cursor.execute('''
        INSERT INTO resume_data (filename, upload_date, ats_score, skill_match, keyword_match)
        VALUES (?, ?, ?, ?, ?)
        ''', (filename, datetime.now(), analysis['ats_score'], 
              analysis['skill_match'], analysis['keyword_match']))
        
        resume_id = cursor.lastrowid
        
        # Insert into resume_analysis
        cursor.execute('''
        INSERT INTO resume_analysis (resume_id, analysis_date, suggestions)
        VALUES (?, ?, ?)
        ''', (resume_id, datetime.now(), str(analysis['suggestions'])))
        
        self.conn.commit()
    
    def get_quick_stats(self):
        """Get quick statistics for the dashboard"""
        cursor = self.conn.cursor()
        
        # Total Resumes
        cursor.execute("SELECT COUNT(*) FROM resume_data")
        total_resumes = cursor.fetchone()[0]
        
        # Average ATS Score
        cursor.execute("SELECT AVG(ats_score) FROM resume_data")
        avg_ats = cursor.fetchone()[0] or 0
        
        # High Performing Resumes
        cursor.execute("SELECT COUNT(*) FROM resume_data WHERE ats_score >= 70")
        high_performing = cursor.fetchone()[0]
        
        # Success Rate
        success_rate = (high_performing / total_resumes * 100) if total_resumes > 0 else 0
        
        return {
            "Total Resumes": f"{total_resumes:,}",
            "Avg ATS Score": f"{avg_ats:.1f}%",
            "High Performing": f"{high_performing:,}",
            "Success Rate": f"{success_rate:.1f}%"
        }
    
    def get_analysis_history(self):
        """Get analysis history for plotting"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT upload_date, ats_score, skill_match, keyword_match
        FROM resume_data
        ORDER BY upload_date DESC
        LIMIT 10
        ''')
        
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['Date', 'ATS Score', 'Skill Match', 'Keyword Match'])
        return df
    
    def plot_analysis_history(self):
        """Plot analysis history"""
        df = self.get_analysis_history()
        if df.empty:
            return None
        
        fig = px.line(df, x='Date', y=['ATS Score', 'Skill Match', 'Keyword Match'],
                     title='Resume Analysis History')
        return fig
    
    def close(self):
        """Close database connection"""
        self.conn.close() 