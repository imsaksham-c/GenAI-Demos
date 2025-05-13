import streamlit as st
from openai import OpenAI
import PyPDF2
import os
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def compare_pdfs_with_openai(text1, text2, client):
    """Compare PDF texts using OpenAI's GPT model."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # You can also use "gpt-3.5-turbo" for a more cost-effective solution
            messages=[
                {"role": "system", "content": "You are an expert document analyst. Your task is to identify and report significant changes between two document versions. Ignore formatting changes, spacing differences, and minor typos. Focus on substantive changes like added/removed paragraphs, modified numbers, changed dates, altered terms, and other meaningful edits. Format your response in markdown with clear headings and bullet points."},
                {"role": "user", "content": f"Original document:\n\n{text1}\n\nNew document:\n\n{text2}\n\nPlease identify and explain the significant differences between these documents."}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in API call: {str(e)}"

def main():
    st.set_page_config(page_title="PDF Comparison Tool", layout="wide")
    
    st.title("PDF Comparison Tool")
    st.write("Upload two PDF files to compare them and identify significant changes.")
    
    # File upload section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original PDF (PDF1)")
        pdf1 = st.file_uploader("Upload the original PDF", type="pdf", key="pdf1")
        
    with col2:
        st.subheader("Modified PDF (PDF2)")
        pdf2 = st.file_uploader("Upload the modified PDF", type="pdf", key="pdf2")
    
    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key (or set it as OPENAI_API_KEY in .env file)", type="password")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    if st.button("Compare PDFs") and pdf1 and pdf2:
        if not client.api_key:
            st.error("Please provide an OpenAI API key.")
            return
            
        with st.spinner("Extracting text from PDFs..."):
            # Save uploaded files to temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp1:
                temp1.write(pdf1.read())
                temp1_path = temp1.name
                
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp2:
                temp2.write(pdf2.read())
                temp2_path = temp2.name
            
            # Extract text from PDFs
            text1 = extract_text_from_pdf(temp1_path)
            text2 = extract_text_from_pdf(temp2_path)
            
            # Clean up temporary files
            os.unlink(temp1_path)
            os.unlink(temp2_path)
        
        with st.spinner("Analyzing differences with OpenAI..."):
            # Compare PDFs using OpenAI
            comparison_result = compare_pdfs_with_openai(text1, text2, client)
            
        # Display comparison results
        st.subheader("Comparison Results")
        st.markdown(comparison_result)
        
        # Display raw text (collapsible)
        with st.expander("View Raw Extracted Text"):
            st.subheader("PDF1 Text")
            st.text_area("", text1, height=300)
            st.subheader("PDF2 Text")
            st.text_area("", text2, height=300)

if __name__ == "__main__":
    main()