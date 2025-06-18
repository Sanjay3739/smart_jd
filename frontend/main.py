import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API base URL from environment variable
API_BASE = os.getenv("API_BASE")

# Streamlit UI configuration
st.set_page_config(page_title="SmartJD - Complete JD Management", layout="wide")
st.title("SmartJD - AI-Powered Job Description Management & Comparison")

# Apply custom CSS
st.markdown("""
    <style>
        .st-emotion-cache-1w723zb {
            max-width: 100% !important;
            padding: 2rem 1rem 10rem !important;
        }
        .success-box {
            padding: 10px;
            border-radius: 5px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            margin: 10px 0;
        }
        .step-indicator {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #007bff;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'jd_content' not in st.session_state:
    st.session_state.jd_content = ""
if 'jd_source' not in st.session_state:
    st.session_state.jd_source = ""

# Reset the entire workflow
def reset_workflow():
    st.session_state.step = 1
    st.session_state.jd_content = ""
    st.session_state.jd_source = ""

# Move to next step
def next_step():
    st.session_state.step = 2

# Sidebar navigation
st.sidebar.header("Workflow Navigation")
st.sidebar.markdown(f"""
**Current Step:** {st.session_state.step}/2

**Step 1:** Create/Input Job Description  
**Step 2:** Compare with Resume Files
""")

if st.sidebar.button("Start New Workflow"):
    reset_workflow()
    st.rerun()

# Main content area
if st.session_state.step == 1:
    st.markdown('<div class="step-indicator"><h3>Step 1: Create or Input Job Description</h3></div>', unsafe_allow_html=True)
    
    # JD Input mode selector
    mode = st.radio("Choose how to create your Job Description:", 
                   ["Upload JD File", "Manual Input", "AI Generate JD"], 
                   horizontal=True)
    
    st.markdown("---")
    
    # =================== Upload File Mode ===================
    if mode == "Upload JD File":
        st.subheader("Upload Job Description File")
        uploaded_file = st.file_uploader("Upload a JD file", type=["pdf", "doc", "docx"])
        
        if uploaded_file and st.button("Process File"):
            with st.spinner("Processing file..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_BASE}/upload_jd_file", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.jd_content = result.get("text", "")
                        st.session_state.jd_source = f"Uploaded file: {uploaded_file.name}"
                        st.success("Job Description processed successfully!")
                        
                        with st.expander("View Processed JD", expanded=True):
                            st.markdown(st.session_state.jd_content)
                    else:
                        st.error(f"Failed to process file: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if st.session_state.jd_content:
            st.markdown("---")
            if st.button("Continue to File Comparison", key="continue_upload"):
                st.session_state.step = 2
                st.rerun()
    
    # =================== Manual Input Mode ===================
    elif mode == "Manual Input":
        st.subheader("Manual Job Description Input")
        
        jd_text = st.text_area("Paste your Job Description below:", height=300, 
                              placeholder="Enter the complete job description here...")
        
        if st.button("Format & Process JD") and jd_text.strip():
            with st.spinner("Processing and formatting..."):
                try:
                    response = requests.post(f"{API_BASE}/manual_jd", data={"jd_text": jd_text})
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.jd_content = result.get("text", "")
                        st.session_state.jd_source = "Manual input"
                        st.success("Job Description formatted successfully!")
                        
                        with st.expander("View Formatted JD", expanded=True):
                            st.markdown(st.session_state.jd_content)
                    else:
                        st.error(f"Failed to format JD: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if st.session_state.jd_content:
            st.markdown("---")
            if st.button("Continue to File Comparison", key="continue_manual"):
                st.session_state.step = 2
                st.rerun()
    
    # =================== AI Generate Mode ===================
    elif mode == "AI Generate JD":
        st.subheader("AI-Generated Job Description")
        
        with st.form("jd_generation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input("Job Title *", placeholder="e.g., Senior Software Engineer")
                experience = st.text_input("Years of Experience *", placeholder="e.g., 3-5")
                skills = st.text_area("Must-have Skills *", height=100, 
                                    placeholder="e.g., Python, React, AWS, Docker")
                company = st.text_input("Company Name", placeholder="e.g., Tech Solutions Inc.")
            
            with col2:
                employment_type = st.selectbox("Employment Type", 
                                             ["Full-time", "Part-time", "Contract", "Internship"])
                industry = st.text_input("Industry", placeholder="e.g., Technology, Healthcare")
                location = st.text_input("Location", placeholder="e.g., San Francisco, CA / Remote")
            
            submit_generate = st.form_submit_button("Generate Job Description")
        
        if submit_generate:
            if not job_title.strip() or not skills.strip():
                st.error("Job Title and Skills are mandatory fields!")
            else:
                with st.spinner("Generating Job Description..."):
                    try:
                        payload = {
                            "job_title": job_title,
                            "experience": experience,
                            "skills": skills,
                            "company": company,
                            "employment_type": employment_type,
                            "industry": industry,
                            "location": location,
                        }
                        response = requests.post(f"{API_BASE}/generate_jd", data=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.jd_content = result.get("text", "")
                            st.session_state.jd_source = f"AI Generated: {job_title}"
                            st.success("Job Description generated successfully!")
                            
                            with st.expander("View Generated JD", expanded=True):
                                st.markdown(st.session_state.jd_content)
                        else:
                            st.error(f"Failed to generate JD: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.jd_content:
            st.markdown("---")
            if st.button("Continue to File Comparison", key="continue_ai"):
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    st.markdown('<div class="step-indicator"><h3>Step 2: Compare Job Description with Resume Files</h3></div>', unsafe_allow_html=True)
    
    # Display current JD info
    st.markdown(f'<div class="success-box"><strong>Current JD Source:</strong> {st.session_state.jd_source}</div>', 
                unsafe_allow_html=True)
    
    with st.expander("View Current Job Description"):
        st.markdown(st.session_state.jd_content)
    
    st.markdown("---")
    
    # File upload for comparison
    st.subheader("Upload Resume/CV Files for Comparison")
    uploaded_files = st.file_uploader(
        "Upload one or more resume files to compare against the Job Description",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOC, DOCX"
    )
    
    if uploaded_files:
        st.info(f"{len(uploaded_files)} file(s) selected for comparison")
        
        if st.button("Analyze & Compare Files"):
            with st.spinner("Analyzing files and calculating match scores..."):
                try:
                    files_data = [("files", (f.name, f, f.type)) for f in uploaded_files]
                    
                    response = requests.post(
                        f"{API_BASE}/compare-jd-and-files/",
                        data={"jd_text": st.session_state.jd_content},
                        files=files_data
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        main_jd = data.get("main_parsed", {})
                        results = data.get("results", [])
                        
                        st.markdown("""
                            <h3 style='font-size: 18px;'>Job Description Analysis</h3>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("""
                                <div style='font-size: 14px;'>
                                    Experience Required<br>
                                    <span style='font-size: 20px; font-weight: bold;'>{}</span>
                                </div>
                            """.format(main_jd.get('experience', 'Not specified')), unsafe_allow_html=True)

                        with col2:
                            st.markdown("""
                                <div style='font-size: 14px;'>
                                    Education Required<br>
                                    <span style='font-size: 20px; font-weight: bold;'>{}</span>
                                </div>
                            """.format(main_jd.get('education', 'Not specified')), unsafe_allow_html=True)

                        with col3:
                            st.markdown("""
                                <div style='font-size: 14px;'>
                                    Total Skills<br>
                                    <span style='font-size: 20px; font-weight: bold;'>{}</span>
                                </div>
                            """.format(len(main_jd.get('skills', []))), unsafe_allow_html=True)
                        
                        if main_jd.get('skills'):
                            st.markdown("Required Skills:")
                            skills_text = ", ".join(main_jd.get("skills", []))
                            st.markdown(f"`{skills_text}`")
                        
                        st.markdown("---")
                        st.markdown("## Resume Comparison Results")
                        
                        valid_results = [r for r in results if "score" in r]
                        if valid_results:
                            max_score = max(r.get("score", 0.0) for r in valid_results)
                            valid_results.sort(key=lambda x: x.get("score", 0), reverse=True)
                            
                            for idx, item in enumerate(valid_results):
                                filename = item.get('filename', 'Unknown')
                                
                                with st.expander(f"{filename} - Score: {item.get('score', 0)}/100", expanded=(idx == 0)):
                                    parsed = item.get("parsed", {})
                                    score = item.get("score", 0.0)
                                    missing_skills = item.get("missing_skills", [])
                                    remarks = item.get("remarks", [])
                                    
                                    if score == max_score and score > 0:
                                        st.success(f"TOP MATCH! Score: {score}/100")
                                    elif score >= 70:
                                        st.success(f"EXCELLENT MATCH! Score: {score}/100")
                                    elif score >= 50:
                                        st.warning(f"GOOD MATCH. Score: {score}/100")
                                    else:
                                        st.error(f"POOR MATCH. Score: {score}/100")
                                    
                                    st.progress(score / 100)
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("Candidate Profile:")
                                        st.markdown(f"Experience: {parsed.get('experience', 'Not specified')}")
                                        st.markdown(f"Education: {parsed.get('education', 'Not specified')}")
                                    
                                    with col2:
                                        st.markdown("Skills Found:")
                                        candidate_skills = parsed.get('skills', [])
                                        if candidate_skills:
                                            st.markdown(", ".join(candidate_skills))
                                        else:
                                            st.markdown("No skills detected")
                                    
                                    if missing_skills:
                                        st.markdown("Missing Skills:")
                                        st.error(", ".join(missing_skills))
                                    else:
                                        st.success("All required skills are present!")
                                    
                                    if remarks:
                                        st.markdown("Analysis Notes:")
                                        for remark in remarks:
                                            st.markdown(f"- {remark}")
                        
                        error_results = [r for r in results if "error" in r]
                        if error_results:
                            st.markdown("---")
                            st.markdown("## Files with Processing Errors")
                            for item in error_results:
                                st.error(f"{item.get('filename', 'Unknown')}: {item.get('error', 'Unknown error')}")
                    
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    st.error(f"Request Failed: {str(e)}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to JD Creation"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Start New Analysis"):
            reset_workflow()
            st.rerun()

# Footer
st.markdown("---")
st.markdown("SmartJD - Streamlining recruitment with AI-powered job description management and candidate matching.")