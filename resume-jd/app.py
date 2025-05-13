import streamlit as st
import requests
from bs4 import BeautifulSoup
import docx
import PyPDF2
import os
import re
import json
from dotenv import load_dotenv
import openai
from io import BytesIO

# ------------- ENVIRONMENT & PAGE SETUP -------------
load_dotenv()

# Initialize session state
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'jd_cleaned' not in st.session_state:
    st.session_state.jd_cleaned = False
if 'resume_cleaned' not in st.session_state:
    st.session_state.resume_cleaned = False
if 'last_jd_url' not in st.session_state:
    st.session_state.last_jd_url = ""
if 'last_resume_url' not in st.session_state:
    st.session_state.last_resume_url = ""
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Page configuration
st.set_page_config(
    page_title="Resume-JD Matcher",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------- CUSTOM CSS FOR FACEBOOK-LIKE CONTRAST -------------
st.markdown("""
<style>
/* Main background and text colors */
.stApp {
    background-color: #1E1E1E;
    color: #FFFFFF;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #242526;
    color: #FFFFFF;
}

/* Header styling */
h1, h2, h3, h4, h5, h6 {
    color: #1877F2;
}

/* Button styling */
.stButton>button {
    background-color: #1877F2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #166FE5;
}

/* Radio buttons */
.stRadio > div {
    background-color: #242526;
    color: #FFFFFF;
    border-radius: 6px;
    padding: 0.5rem;
}

/* Text input fields */
.stTextInput>div>div>input {
    background-color: #3A3B3C;
    color: #FFFFFF;
    border: 1px solid #4E4F50;
    border-radius: 6px;
}

/* File uploader */
.stFileUploader {
    background-color: #3A3B3C;
    border: 1px dashed #4E4F50;
    border-radius: 8px;
    padding: 1rem;
}

/* Text areas */
.stTextArea textarea {
    background-color: #3A3B3C;
    color: #FFFFFF;
    border: 1px solid #4E4F50;
}

/* Upload area */
.upload-area {
    background-color: #3A3B3C;
    color: #FFFFFF;
    border: 2px dashed #4E4F50;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
}

/* Card/container styling */
.css-1r6slb0, .css-12w0qpk, .css-keje6w {
    background-color: #242526;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid #4E4F50;
}

/* Copy button styling */
.copy-button {
    background-color: #1877F2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    cursor: pointer;
    margin-top: 0.5rem;
}

.copy-button:hover {
    background-color: #166FE5;
}

/* Results container */
.results-container {
    background-color: #242526;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #4E4F50;
    margin-top: 1.5rem;
}

/* Score indicator */
.score-indicator {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1877F2;
    text-align: center;
    padding: 1rem;
}

/* Feedback items */
.feedback-item {
    background-color: #3A3B3C;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    border-left: 3px solid #1877F2;
    color: #FFFFFF;
}

/* Summary section */
.summary-section {
    background-color: #3A3B3C;
    padding: 1rem;
    border-radius: 8px;
    margin-top: 1rem;
    color: #FFFFFF;
}

/* Instructions section */
.instructions {
    background-color: #3A3B3C;
    border-left: 4px solid #1877F2;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
    color: #FFFFFF;
}

/* Code block for copy text */
pre {
    background-color: #242526;
    color: #FFFFFF;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #4E4F50;
}

/* Success and error messages */
.success-message {
    background-color: #3A3B3C;
    color: #4CAF50;
    padding: 0.75rem;
    border-radius: 6px;
    margin: 1rem 0;
    border-left: 3px solid #4CAF50;
}

.error-message {
    background-color: #3A3B3C;
    color: #F44336;
    padding: 0.75rem;
    border-radius: 6px;
    margin: 1rem 0;
    border-left: 3px solid #F44336;
}
</style>
""", unsafe_allow_html=True)

# ------------- OPENAI API KEY HANDLING -------------
with st.sidebar:
    st.header("OpenAI API Configuration")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            openai.api_key = api_key
    else:
        st.success("API key loaded from environment!")
        openai.api_key = api_key

    st.header("Model Settings")
    model = st.selectbox("Select Model:", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"], index=0)
    
    # Add contact information
    st.markdown("---")
    st.header("Connect with me:")
    st.markdown("""
    📧 Email - [imsaksham.c@gmail.com](mailto:imsaksham.c@gmail.com)
    
    🔗 LinkedIn - [linkedin.com/in/saksham-chaurasia](https://www.linkedin.com/in/saksham-chaurasia/)
    
    💻 GitHub - [github.com/imsaksham-c](https://github.com/imsaksham-c)
    """)

# ------------- TEXT EXTRACTION HELPERS -------------
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF files."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        st.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from DOCX files."""
    try:
        doc = docx.Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX extraction error: {e}")
        return ""

def extract_text_from_url(url):
    """Extract text from a webpage URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator="\n")
        
        # Break into lines and remove leading and trailing space
        lines = [line.strip() for line in text.splitlines()]
        
        # Remove blank lines
        text = "\n".join([line for line in lines if line])
        
        return text
    except Exception as e:
        st.error(f"URL extraction error: {e}")
        return ""

# ------------- LLM CLEANING OF EXTRACTED TEXT -------------
def clean_text_with_llm(text, text_type):
    """Use OpenAI to clean and extract only relevant information from scraped text."""
    if not text or not openai.api_key:
        return text
    
    try:
        if text_type == "job_description":
            prompt = f"""Extract and organize only the relevant information from this job description:
{text}

Format your response as follows:
Company: [company name]
Job Title: [job title]
Location: [location]
Job Type: [full-time/part-time/contract]
Required Skills: [list of key skills]
Responsibilities: [bullet points of main responsibilities]
Qualifications: [bullet points of required qualifications]
Benefits: [any mentioned benefits]

Remove any redundant information, advertisements, or irrelevant content.
"""
        else:  # resume
            prompt = f"""Extract and organize only the relevant information from this resume:
{text}

Format your response as follows:
Name: [candidate name]
Contact Information: [email/phone]
Professional Summary: [brief summary]
Skills: [list of key skills]
Experience: [bullet points of relevant experience]
Education: [education details]
Certifications: [any certifications]

Remove any redundant information or irrelevant content.
"""
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a faster model for preprocessing
            messages=[
                {"role": "system", "content": "You are an expert at extracting relevant information from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Could not optimize the extracted text: {e}")
        return text

# ------------- MATCH ANALYSIS WITH ADVANCED SUMMARY -------------
def analyze_match(jd_text, resume_text, model):
    """Analyze the match between a job description and resume using OpenAI."""
    if not openai.api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        return None
    
    if not jd_text or not resume_text:
        st.error("Please provide both a job description and resume to analyze.")
        return None
    
    try:
        prompt = f"""
You are an expert ATS (Applicant Tracking System) and career advisor. Analyze the match between the job description and resume provided below.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Provide a detailed analysis in JSON format with the following structure:
1. "score": A number from 0-10 indicating how well the resume matches the job description
2. "feedback": An array of specific improvement suggestions (at least 3)
3. "name": The candidate's name extracted from the resume
4. "summary": A professional third-person summary of the candidate's qualifications as they relate to the job (3-4 sentences)
5. "attractive_points": An array of 5 specific points that make this candidate's profile attractive for this role
6. "fit_explanation": A paragraph explaining why this candidate is a good fit for the role, referencing specific requirements from the job description

For the summary and attractive points, focus on highlighting the candidate's strengths that directly match the job requirements.

Return ONLY the JSON object without any additional text.
"""
        
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert ATS system and career advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'({[\s\S]*})', result)
            if json_match:
                result_json = json.loads(json_match.group(0))
                return result_json
            else:
                return json.loads(result)
        except Exception as e:
            st.error(f"Error parsing JSON response: {e}")
            st.write(result)
            return None
            
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None

# ------------- MAIN APP LAYOUT -------------
st.markdown('<h1 style="text-align: center;">📋 Resume-JD Matcher</h1>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ------------- JOB DESCRIPTION INPUT -------------
with col1:
    st.header("Job Description")
    
    jd_source = st.radio("Select Job Description source:", ["Upload File", "Enter URL"], horizontal=True)
    
    # Reset cleaned flag when source changes
    if 'last_jd_source' not in st.session_state or st.session_state.last_jd_source != jd_source:
        st.session_state.jd_cleaned = False
        st.session_state.last_jd_source = jd_source
        # Reset analysis when source changes
        st.session_state.analysis_done = False
    
    # Track if we need to process a new JD
    jd_needs_processing = False
    
    if jd_source == "Upload File":
        jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
        
        # Check if file has changed
        if jd_file is not None:
            file_details = {"filename": jd_file.name, "size": jd_file.size}
            file_id = str(file_details)
            
            if 'last_jd_file_id' not in st.session_state or st.session_state.last_jd_file_id != file_id:
                st.session_state.last_jd_file_id = file_id
                st.session_state.jd_cleaned = False
                jd_needs_processing = True
                # Reset analysis when file changes
                st.session_state.analysis_done = False
    else:
        jd_url = st.text_input("Enter Job Description URL:")
        if jd_url and st.session_state.last_jd_url != jd_url:
            st.session_state.last_jd_url = jd_url
            st.session_state.jd_cleaned = False
            jd_needs_processing = True
            # Reset analysis when URL changes
            st.session_state.analysis_done = False
    
    # Only process the JD if it needs processing and hasn't been cleaned
    if jd_needs_processing and not st.session_state.jd_cleaned:
        if jd_source == "Upload File" and jd_file is not None:
            # Extract text from file
            if jd_file.name.endswith('.pdf'):
                raw_jd_text = extract_text_from_pdf(jd_file)
            elif jd_file.name.endswith('.docx'):
                raw_jd_text = extract_text_from_docx(jd_file)
                
            # Clean the text
            if raw_jd_text:
                with st.spinner("Cleaning and organizing job description..."):
                    jd_text = clean_text_with_llm(raw_jd_text, "job_description")
                    st.session_state.jd_text = jd_text
                    st.session_state.jd_cleaned = True
                    st.success("Job description extracted and cleaned successfully!")
        elif jd_source == "Enter URL" and jd_url:
            # Extract and clean text from URL
            with st.spinner("Extracting text from URL..."):
                raw_jd = extract_text_from_url(jd_url)
                
                if raw_jd:
                    with st.spinner("Cleaning and organizing job description..."):
                        jd_text = clean_text_with_llm(raw_jd, "job_description")
                        st.session_state.jd_text = jd_text
                        st.session_state.jd_cleaned = True
                        st.success("Job description extracted and cleaned successfully from URL!")
                else:
                    st.error("Failed to extract text from the provided URL.")
    
    # Always display the JD text if it exists in session state
    if st.session_state.jd_text:
        st.text_area("Extracted Job Description", st.session_state.jd_text, height=200, key="jd_display", disabled=True)

# ------------- RESUME INPUT -------------
with col2:
    st.header("Resume")
    
    resume_source = st.radio("Select Resume source:", ["Upload File", "Enter URL"], horizontal=True)
    
    # Reset cleaned flag when source changes
    if 'last_resume_source' not in st.session_state or st.session_state.last_resume_source != resume_source:
        st.session_state.resume_cleaned = False
        st.session_state.last_resume_source = resume_source
        # Reset analysis when source changes
        st.session_state.analysis_done = False
    
    # Track if we need to process a new resume
    resume_needs_processing = False
    
    if resume_source == "Upload File":
        resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
        
        # Check if file has changed
        if resume_file is not None:
            file_details = {"filename": resume_file.name, "size": resume_file.size}
            file_id = str(file_details)
            
            if 'last_resume_file_id' not in st.session_state or st.session_state.last_resume_file_id != file_id:
                st.session_state.last_resume_file_id = file_id
                st.session_state.resume_cleaned = False
                resume_needs_processing = True
                # Reset analysis when file changes
                st.session_state.analysis_done = False
    else:
        resume_url = st.text_input("Enter Resume URL (LinkedIn profile, etc.):")
        if resume_url and st.session_state.last_resume_url != resume_url:
            st.session_state.last_resume_url = resume_url
            st.session_state.resume_cleaned = False
            resume_needs_processing = True
            # Reset analysis when URL changes
            st.session_state.analysis_done = False
    
    # Only process the resume if it needs processing and hasn't been cleaned
    if resume_needs_processing and not st.session_state.resume_cleaned:
        if resume_source == "Upload File" and resume_file is not None:
            # Extract text from file
            if resume_file.name.endswith('.pdf'):
                raw_resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.name.endswith('.docx'):
                raw_resume_text = extract_text_from_docx(resume_file)
                
            # Clean the text
            if raw_resume_text:
                with st.spinner("Cleaning and organizing resume..."):
                    resume_text = clean_text_with_llm(raw_resume_text, "resume")
                    st.session_state.resume_text = resume_text
                    st.session_state.resume_cleaned = True
                    st.success("Resume extracted and cleaned successfully!")
        elif resume_source == "Enter URL" and resume_url:
            # Extract and clean text from URL
            with st.spinner("Extracting text from URL..."):
                raw_resume = extract_text_from_url(resume_url)
                
                if raw_resume:
                    with st.spinner("Cleaning and organizing resume..."):
                        resume_text = clean_text_with_llm(raw_resume, "resume")
                        st.session_state.resume_text = resume_text
                        st.session_state.resume_cleaned = True
                        st.success("Resume extracted and cleaned successfully from URL!")
                else:
                    st.error("Failed to extract text from the provided URL.")
    
    # Always display the resume text if it exists in session state
    if st.session_state.resume_text:
        st.text_area("Extracted Resume", st.session_state.resume_text, height=200, key="resume_display", disabled=True)

# ------------- ANALYSIS BUTTON & RESULTS -------------
st.header("Analysis")

if st.button("Analyze Match", type="primary"):
    if not st.session_state.jd_text or not st.session_state.resume_text:
        st.error("Please provide both a job description and resume to analyze.")
    elif not openai.api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        with st.spinner("Analyzing the match..."):
            # Only use the stored session state values, don't reprocess
            result = analyze_match(st.session_state.jd_text, st.session_state.resume_text, model)
            
            if result:
                st.session_state.analysis_result = result
                st.session_state.analysis_done = True

# Display analysis results (either from button click or from session state)
if st.session_state.analysis_done and st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Score display
    score = result.get("score", 0)
    score_color = "#4CAF50" if score >= 7 else "#FF9800" if score >= 5 else "#F44336"
    
    st.markdown(f'<div class="score-indicator" style="color: {score_color};">{score}/10</div>', unsafe_allow_html=True)
    
    # Candidate name
    candidate_name = result.get("name", "Candidate")
    st.markdown(f"<h3>Results for: {candidate_name}</h3>", unsafe_allow_html=True)
    
    # Feedback
    st.markdown("<h3>Improvement Suggestions:</h3>", unsafe_allow_html=True)
    feedback = result.get("feedback", [])
    for item in feedback:
        st.markdown(f'<div class="feedback-item">{item}</div>', unsafe_allow_html=True)
    
    # Summary section with attractive points and fit explanation
    summary_text = result.get("summary", "")
    attractive_points = result.get("attractive_points", [])
    fit_explanation = result.get("fit_explanation", "")
    
    if summary_text:
        st.markdown('<div class="summary-section">', unsafe_allow_html=True)
        
        # Professional Summary
        st.markdown("<h3>Professional Summary:</h3>", unsafe_allow_html=True)
        st.markdown(summary_text)
        
        # Key Strengths (5 attractive points)
        if attractive_points:
            st.markdown("<h3>Key Strengths:</h3>", unsafe_allow_html=True)
            for i, point in enumerate(attractive_points, 1):
                st.markdown(f"**{i}.** {point}")
        
        # Job Fit Analysis
        if fit_explanation:
            st.markdown("<h3>Job Fit Analysis:</h3>", unsafe_allow_html=True)
            st.markdown(fit_explanation)
        
        # Prepare text for copy button
        copy_text = f"""Professional Summary:
{summary_text}

Key Strengths:
""" + "\n".join([f"{i}. {point}" for i, point in enumerate(attractive_points, 1)]) + f"""

Job Fit Analysis:
{fit_explanation}
"""
        
        # Display the text in a code block for easy copying
        st.markdown("<h3>Copy-Ready Summary:</h3>", unsafe_allow_html=True)
        st.code(copy_text, language=None)
        
        # Add copy button with JavaScript
        st.markdown("""
        <button class="copy-button" onclick="copyToClipboard()">Copy Summary</button>
        <script>
        function copyToClipboard() {
            const text = document.querySelector('pre').innerText;
            navigator.clipboard.writeText(text).then(function() {
                alert('Summary copied to clipboard!');
            }, function(err) {
                alert('Could not copy text: ' + err);
            });
        }
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
elif not st.session_state.analysis_done:
    st.markdown('<div class="instructions">', unsafe_allow_html=True)
    st.markdown("## How to use this app")
    st.markdown("""
    1. Enter your OpenAI API key in the sidebar (or configure it in the .env file)
    2. Upload a Job Description or provide a URL
    3. Upload your Resume or provide a URL
    4. Click "Analyze Match" to see the results
    5. Review the match score, improvement feedback, and professional summary
    6. Use the copy button to copy the summary for your applications
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------- FOOTER -------------
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #898F9C; font-size: 0.8rem;">
    Resume-JD Matcher | Powered by OpenAI | © 2025
</div>
""", unsafe_allow_html=True)
