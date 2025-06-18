# Recruitment AI - Job Description Management System

A FastAPI-based application for managing and analyzing job descriptions using Google's Gemini AI.

## Features

- Upload and parse job descriptions from various file formats (PDF, DOCX, DOC)
- Submit job descriptions manually through text input
- Generate new job descriptions based on specific requirements
- Compare job descriptions and calculate match scores
- Analyze skill gaps between job descriptions
- Format and clean up job descriptions using AI

## Project Structure

```
recruitment-ai/
├── app.py              # Main FastAPI application
├── frontend/           # Frontend application files
├── uploaded_jds/       # Directory for temporary file uploads
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd recruitment-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=your_gemini_model_name
API_BASE =your_fast_api_url
```

## Running the Application

navigate folder path :
```bash
cd beckand
```
Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Run the Streamlit application:
```bash
streamlit run main.py
```

The frontend will be available at `http://localhost:8501`

## API Endpoints

- `POST /upload_jd_file`: Upload and parse a job description file
- `POST /manual_jd`: Submit a job description text directly
- `POST /generate_jd`: Generate a new job description based on parameters
- `POST /compare-jd-and-files/`: Compare job descriptions and analyze gaps
- `GET /health`: Health check endpoint

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Development

- The project uses FastAPI for the web framework
- Google's Gemini AI for text generation and analysis
- Pydantic for data validation
- Python-multipart for file uploads
- docx2txt, PyMuPDF (fitz), and textract for file parsing

## AI Model Implementation

### Model Choice: Google's Gemini AI
We chose Google's Gemini AI for this project for several key reasons:

1. **Performance & Accuracy**
   - State-of-the-art language understanding capabilities
   - Excellent performance in text analysis and generation tasks
   - Strong contextual understanding for job description analysis

2. **Cost Efficiency**
   - Competitive pricing compared to other enterprise AI models
   - Pay-as-you-go model suitable for varying workloads
   - No minimum usage requirements

3. **Features & Capabilities**
   - Advanced text generation for creating job descriptions
   - Strong semantic understanding for skill gap analysis
   - Robust text processing for document parsing

### Model Implementation

The Gemini AI model is used in several key areas of the application:

1. **Job Description Generation**
   - Creates structured job descriptions based on input parameters
   - Maintains consistent formatting and professional language
   - Incorporates industry standards and best practices

2. **Skill Gap Analysis**
   - Analyzes job descriptions to identify required skills
   - Compares candidate qualifications against job requirements
   - Provides detailed gap analysis with actionable insights

3. **Document Processing**
   - Extracts and structures information from various file formats
   - Cleans and formats text for better readability
   - Identifies key components in job descriptions

## Example Test Files

To help you get started with testing the application, we provide example files in the `test_files` directory:

1. **Job Descriptions**
   - `example_jd_software_engineer.pdf`
   - `example_jd_data_scientist.docx`
   - `example_jd_product_manager.doc`

2. **Resume Examples**
   - `example_resume_software_engineer.pdf`
   - `example_resume_data_scientist.docx`

These files can be used to test:
- File upload functionality
- Job description parsing
- Skill matching and gap analysis
- Document comparison features

## License

MIT License