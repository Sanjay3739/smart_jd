import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API base URL from environment variable
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# Streamlit UI configuration
st.set_page_config(
    page_title="🔍 SmartJD - AI Job Description Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
with open( "css\style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'jd_content' not in st.session_state:
    st.session_state.jd_content = ""
if 'jd_source' not in st.session_state:
    st.session_state.jd_source = ""
if 'jd_analysis' not in st.session_state:
    st.session_state.jd_analysis = {}

def reset_workflow():
    """Reset the entire workflow"""
    st.session_state.step = 1
    st.session_state.jd_content = ""
    st.session_state.jd_source = ""
    st.session_state.jd_analysis = {}

def next_step():
    """Move to next step"""
    st.session_state.step = 2

# Sidebar navigation
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 2rem;">
            <h2 style="color: var(--primary); margin-bottom: 0.5rem;">🔍 SmartJD</h2>
            <p style="color: var(--light-text); font-size: 0.9rem;">AI-Powered Job Description Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Workflow Progress")
    
    # Step indicators
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.markdown(f'<div class="step {"active" if st.session_state.step == 1 else "inactive"}">1</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="step-label">Create Job Description</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.markdown(f'<div class="step {"active" if st.session_state.step == 2 else "inactive"}">2</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="step-label">Compare & Analyze & Email</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔄 Start New Workflow", use_container_width=True):
        reset_workflow()
        st.rerun()

# Main content area
st.markdown("""
    <div class="header">
        <h1 style="margin-bottom: 0.5rem;">🔍 SmartJD</h1>
        <p style="color: var(--light-text);">AI-Powered Job Description Management & Candidate Matching</p>
    </div>
""", unsafe_allow_html=True)

# Step 1: Create or Input Job Description
if st.session_state.step == 1:
    st.markdown("""
        <div class="step-indicator">
            <div class="step active">1</div>
            <div class="step-label">Create Job Description</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-title">📝 Create or Input Job Description</div>', unsafe_allow_html=True)
        
        # JD Input mode selector
        mode = st.radio(
            "Choose input method:",
            ["📤 Upload JD File", "✍️ Manual Input", "🤖 AI Generate JD"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # =================== Upload File Mode ===================
        if mode == "📤 Upload JD File":
            st.markdown("#### Upload Job Description File")
            st.markdown("Upload a PDF, DOC, or DOCX file containing the job description.")
            
            uploaded_file = st.file_uploader(
                "Drag and drop or click to browse files",
                type=["pdf", "doc", "docx"],
                label_visibility="collapsed"
            )
            
            if uploaded_file and st.button("Process File", key="process_file"):
                with st.spinner("Processing file..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_BASE}/upload_jd_file", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.jd_content = result.get("text", "")
                            st.session_state.jd_source = f"Uploaded file: {uploaded_file.name}"
                            st.session_state.jd_analysis = result.get("analysis", {})
                            
                            st.toast("Job Description processed successfully!")
                            
                            with st.expander("View Processed Job Description", expanded=True):
                                st.markdown(st.session_state.jd_content)
                        else:
                            st.error(f"Failed to process file: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # =================== Manual Input Mode ===================
        elif mode == "✍️ Manual Input":
            st.markdown("#### Manual Job Description Input")
            st.markdown("Paste the complete job description in the text area below.")
            
            jd_text = st.text_area(
                "Paste your Job Description here:",
                height=300,
                placeholder="Enter the complete job description here...",
                label_visibility="collapsed"
            )
            
            if st.button("Format & Process JD") and jd_text.strip():
                with st.spinner("Processing and formatting..."):
                    try:
                        response = requests.post(f"{API_BASE}/manual_jd", data={"jd_text": jd_text})
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.jd_content = result.get("text", "")
                            st.session_state.jd_source = "Manual input"
                            st.session_state.jd_analysis = result.get("analysis", {})
                            
                            st.toast("Job Description formatted successfully!")
                            
                            with st.expander("View Formatted JD", expanded=True):
                                st.markdown(st.session_state.jd_content)
                        else:
                            st.error(f"Failed to format JD: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # =================== AI Generate Mode ===================
        elif mode == "🤖 AI Generate JD":
            st.markdown("#### AI-Generated Job Description")
            st.markdown("Fill in the details below to generate a professional job description.")
            
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
                                st.session_state.jd_analysis = result.get("analysis", {})
                                
                                st.toast("Job Description generated successfully!")
                                
                                with st.expander("View Generated JD", expanded=True):
                                    st.markdown(st.session_state.jd_content)
                            else:
                                st.error(f"Failed to generate JD: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        # Show continue button only if JD content exists
        if st.session_state.jd_content:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.markdown(f"**Current Job Description:** {st.session_state.jd_source}")
            with col2:
                if st.button("Continue to Analysis →", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()

# Step 2: Compare Job Description with Resume Files
elif st.session_state.step == 2:
    st.markdown("""
        <div class="step-indicator">
            <div class="step active">2</div>
            <div class="step-label">Compare & Analyze</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-title">📊 Job Description Analysis</div>', unsafe_allow_html=True)
        
        # Display current JD info
        st.markdown(f"**Job Description Source:** {st.session_state.jd_source}")
        
        # Show JD analysis summary
        if st.session_state.jd_analysis:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Job Title", st.session_state.jd_analysis.get('job_title', 'Not specified'))
            with col2:
                st.metric("Experience Required", st.session_state.jd_analysis.get('experience', 'Not specified'))
            with col3:
                st.metric("Education Level", st.session_state.jd_analysis.get('education', 'Not specified'))
            
            if st.session_state.jd_analysis.get('skills'):
                st.markdown("**Key Skills Required:**")
                for skill in st.session_state.jd_analysis['skills']:
                    st.markdown(f'<span class="skill-chip">{skill}</span>', unsafe_allow_html=True)
        
        # Show JD content in expander
        with st.expander("View Full Job Description"):
            st.markdown(st.session_state.jd_content)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # File upload for comparison
        st.markdown('''<div class="card"><h3>📂 Upload Resume/CV Files</h3> </div>''', unsafe_allow_html=True)
        st.markdown("Upload one or more resume files to compare against the job description.")
        
        uploaded_files = st.file_uploader(
            "Drag and drop or click to browse files",
            type=["pdf", "docx", "doc"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.toast(f"{len(uploaded_files)} file(s) selected for analysis")
            
            # Analysis mode selector
            analysis_mode = st.radio(
                "Analysis Mode:",
                ["📊 Compare & Analyze Only", "📧 Compare & Generate Emails"],
                horizontal=True
            )
            
            if st.button("Start Analysis", type="primary"):
                with st.spinner("Analyzing candidates..."):
                    try:
                        # Prepare files for API
                        files_data = [("files", (f.name, f, f.type)) for f in uploaded_files]
                        
                        endpoint = "/compare-jd-and-files/" if analysis_mode == "📊 Compare & Analyze Only" else "/generate-emails/"
                        response = requests.post(
                            f"{API_BASE}{endpoint}",
                            data={"jd_text": st.session_state.jd_content},
                            files=files_data
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            main_jd = data.get("main_parsed", {})
                            results = data.get("results", [])
                            
                            if analysis_mode == "📊 Compare & Analyze Only":
                                # Display analysis results
                                st.markdown('''<div class="card"><h3> 📊 Candidate Analysis Results</h3> </div>''', unsafe_allow_html=True)
                                
                                # Sort results by score (highest first)
                                valid_results = [r for r in results if "score" in r]
                                valid_results.sort(key=lambda x: x.get("score", 0), reverse=True)
                                
                                for candidate in valid_results:
                                    with st.container():
                                        
                                        # Header with name and score
                                        col1, col2 = st.columns([0.7, 0.3])
                                        with col1:
                                            st.markdown(f'<div class="candidate-name">{candidate.get("filename", "Unknown")}</div>', unsafe_allow_html=True)
                                        with col2:
                                            score = candidate.get("score", 0)
                                            if score >= 80:
                                                st.markdown(f'<div class="match-score green"><span>Match Score: {score}%</span></div>', unsafe_allow_html=True)
                                            elif score >= 50:
                                                st.markdown(f'<div class="match-score green"><span>Match Score: {score}%</span></div>', unsafe_allow_html=True)
                                            else:
                                                st.markdown(f'<div class="match-score red"><span>Match Score: {score}%</span></div>', unsafe_allow_html=True)
                                               
                                        if main_jd.get('skills'):
                                            st.markdown("**🎯 Required Skills:**")
                                            st.markdown("""
                                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                                                %s
                                            </div>  
                                            """ % "".join([f'<span class="skill-chip">{skill}</span>' for skill in main_jd.get("skills", [])]), 
                                            unsafe_allow_html=True) 

                                        # Progress bar
                                        st.markdown(f"""
                                            <div class="progress-container">
                                                <div class="progress-bar" style="width: {score}%"></div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Candidate details
                                        parsed = candidate.get("parsed", {})
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.markdown(f"**Experience:** {parsed.get('experience', 'Not specified')}")
                                            st.markdown(f"**Education:** {parsed.get('education', 'Not specified')}")
                                            # Missing skills
                                            if candidate.get("missing_skills"):
                                                st.markdown("**Missing Skills:**")
                                                st.markdown("""
                                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                                    %s
                                                </div>
                                                """ % "".join([f'<span class="skill-chip missing-skill">{skill}</span>' for skill in candidate.get('missing_skills', [])]), 
                                                unsafe_allow_html=True)
                                        
                                        with col2:
                                            st.markdown("**Skills:**")
                                            st.markdown("""
                                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                                %s
                                            </div>
                                            """ % "".join([f'<span class="skill-chip">{skill}</span>' for skill in parsed.get('skills', [])]), 
                                            unsafe_allow_html=True)
                                        
                                        st.markdown("---")
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)

                                # Show error files if any
                                error_results = [r for r in results if "error" in r]
                                if error_results:
                                    st.markdown("## ⚠️ Processing Errors")
                                    for error in error_results:
                                        st.error(f"{error.get('filename', 'Unknown file')}: {error.get('error', 'Unknown error')}")
                            
                            else:  # Email generation mode
                                st.markdown('''<div class="card"><h3>✉️ Email Generation Results</h3> </div>''', unsafe_allow_html=True)

                                # Separate candidates by type
                                interview_candidates = [r for r in results if r.get("email_type") == "interview"]
                                rejection_candidates = [r for r in results if r.get("email_type") == "rejection"]
                                
                                if interview_candidates:
                                    for candidate in interview_candidates:
                                        with st.container():
                                           
                                            col1, col2 = st.columns([0.7, 0.3])
                                            with col1:
                                                st.markdown(f'<div class="candidate-name">{candidate.get("candidate_name", "Unknown")}</div>', unsafe_allow_html=True)
                                            with col2:
                                               st.markdown(f"<div class='match-score green'><span>Match Score: {candidate.get('score', 0)}%</span></div>", unsafe_allow_html=True)
                                            st.markdown("#### Interview Invitation Email:")
                                            st.markdown(f'<div class="email-template">{candidate.get("email_content", "")}</div>', unsafe_allow_html=True)
                                            
                                            st.markdown('</div>', unsafe_allow_html=True)
                                
                                if rejection_candidates:
                                    st.markdown("### 📝 Other Candidates (Rejection Emails)")
                                    for candidate in rejection_candidates:
                                        with st.expander(f"{candidate.get('candidate_name', 'Unknown')} - Score: {candidate.get('score', 0)}%"):
                                            st.markdown(f'<div class="email-template rejection-email">{candidate.get("email_content", "")}</div>', unsafe_allow_html=True)
                                            
                                # Show error files if any
                                error_results = [r for r in results if "error" in r]
                                if error_results:
                                    st.markdown("## ⚠️ Processing Errors")
                                    for error in error_results:
                                        st.error(f"{error.get('filename', 'Unknown file')}: {error.get('error', 'Unknown error')}")
                        
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                    except Exception as e:
                        st.error(f"Request Failed: {str(e)}")
        
        # Navigation buttons
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.3, 0.7])
        with col1:
            if st.button("← Back to JD Creation", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("🔄 Start New Analysis", use_container_width=True):
                reset_workflow()
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: var(--light-text); font-size: 0.9rem;">
        <p>SmartJD - AI-Powered Job Description Management System</p>
    </div>
""", unsafe_allow_html=True)