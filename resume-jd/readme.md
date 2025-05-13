# Resume-JD Matcher

A Streamlit application that compares resumes with job descriptions using OpenAI's GPT models to provide match scores, feedback, and professional summaries.

## Features

- **Multiple Input Methods**: Upload files (PDF, DOCX) or provide URLs (including LinkedIn profiles)
- **Advanced Scraping**: Extract text from both job descriptions and resumes from various sources
- **AI-Powered Analysis**: Uses OpenAI's GPT models to compare resumes against job descriptions
- **Comprehensive Scoring**: Provides a match score on a scale of 0-10
- **Actionable Feedback**: Delivers specific recommendations to improve resume match
- **Professional Summary**: Generates a third-person summary highlighting achievements relevant to the job description (for scores 7+)
- **User-Friendly Interface**: Clean and intuitive UI with visual score indicator

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/resume-jd-matcher.git
   cd resume-jd-matcher
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Rename `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

1. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. In the sidebar:
   - The app will automatically use your OpenAI API key from the `.env` file. If not found, you'll be prompted to enter it
   - Choose whether to upload a file or provide a URL for both the job description and resume
   - Upload the appropriate files or enter the URLs
   - Click "Analyze Match" to process the documents

4. View your results:
   - Match score (0-10)
   - Detailed feedback with improvement suggestions
   - Professional summary (if score is 7 or higher)

## How It Works

1. **Text Extraction**:
   - PDF files: Uses PyPDF2 to extract text
   - DOCX files: Uses python-docx to parse content
   - URLs: Uses requests and BeautifulSoup to scrape and clean text content
   - Special handling for LinkedIn and other job sites to avoid scraping issues

2. **Candidate Name Extraction**:
   - Uses OpenAI to intelligently extract the candidate's name from the resume

3. **Match Analysis**:
   - Sends both the job description and resume to OpenAI
   - Evaluates matches based on skills, experience, education, location, industry knowledge, and achievements
   - Returns a comprehensive JSON response with score, feedback, and summary

4. **Results Presentation**:
   - Visual score indicator with color coding
   - Formatted feedback for easy reading
   - Professional summary formatted for ready use

## Tips for Best Results

- Ensure your OpenAI API key has access to the required models (GPT-4o recommended)
- For PDF files, make sure the text is selectable/extractable (not scanned images)
- When using URLs, ensure they are publicly accessible
- LinkedIn profiles work best when they are public profiles
- Larger documents may take longer to process due to token limitations

## Troubleshooting

- If you encounter scraping issues with LinkedIn, try using a file upload instead
- If the API returns an error, check your API key and usage limits
- For very large documents, consider trimming them to focus on the most relevant sections

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/) GPT models
- Text extraction powered by PyPDF2 and python-docx
- Web scraping capabilities thanks to BeautifulSoup