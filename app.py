import streamlit as st
import pandas as pd
import io
import time
from utils import extract_text_from_pdf, extract_claims_with_llm
from verifier import search_live_web, cross_reference_claim

st.set_page_config(
    page_title="Truth Layer – AI Fact Checking Agent",
    page_icon="🛡️",
    layout="wide"
)

# Render Custom Styling Elements
st.markdown("""
    <style>
    .report-title { font-size: 2.4rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem; }
    .report-subtitle { font-size: 1.1rem; color: #94A3B8; margin-bottom: 2rem; }
    div[data-testid="stMetricValue"] > div { font-size: 2rem; font-weight: bold; }
    </style>
""", unsafe_allowed_html=True)

st.markdown('<p class="report-title">🛡️ Truth Layer – AI Fact Checking Agent</p>', unsafe_allowed_html=True)
st.markdown('<p class="report-subtitle">Instantly analyze marketing PDFs, extract factual statements, and run autonomous real-time live web verification protocols.</p>', unsafe_allowed_html=True)

# API Access Settings
st.sidebar.header("🔑 Authentication Setup")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Input your secret key to authorize verification sequences.")

if not openai_api_key:
    st.info("💡 Please enter an OpenAI API Key in the sidebar to get started.")
    st.stop()

# Persistent state containers
if "extracted_claims" not in st.session_state:
    st.session_state.extracted_claims = []
if "verification_results" not in st.session_state:
    st.session_state.verification_results = None

# PDF Processing Section
st.subheader("1. Asset Injection")
uploaded_file = st.file_uploader("Drop target marketing copy collateral (PDF formats supported)", type=["pdf"])

if uploaded_file:
    if st.button("Extract Claims 🔍", use_container_width=True):
        with st.spinner("Parsing documents and structural text fields..."):
            try:
                raw_text = extract_text_from_pdf(uploaded_file)
                if not raw_text:
                    st.error("Document parser returned empty text. Confirm the file has selectable text layers.")
                else:
                    claims = extract_claims_with_llm(raw_text, openai_api_key)
                    st.session_state.extracted_claims = claims
                    st.session_state.verification_results = None # Clear old pipeline states
                    st.success(f"Successfully isolated {len(claims)} quantifiable factual statements.")
            except Exception as error:
                st.error(f"Execution Error: {str(error)}")

# Interactive Workflow Management
if st.session_state.extracted_claims:
    st.subheader("2. Review Isolated Claims")
    
    # Render selectable modifications
    selected_claims = st.multiselect(
        "Confirm statements queued for live-web cross-referencing:",
        options=st.session_state.extracted_claims,
        default=st.session_state.extracted_claims
    )
    
    if st.button("Verify Claims 🚀", use_container_width=True):
        if not selected_claims:
            st.warning("Select at least one unique statement layer to verify.")
        else:
            results_pool = []
            progress_bar = st.progress(0)
            status_ticker = st.empty()
            
            for index, target_claim in enumerate(selected_claims):
                status_ticker.markdown(f"**Verifying ({index+1}/{len(selected_claims)}):** *\"{target_claim}\"*")
                
                # Dynamic pipeline execution
                evidence_data = search_live_web(target_claim)
                resolution = cross_reference_claim(target_claim, evidence_data, openai_api_key)
                
                results_pool.append({
                    "Claim": target_claim,
                    "Status": resolution.get("status", "FALSE"),
                    "Evidence": evidence_data if evidence_data else "No live records captured.",
                    "Correct Information": resolution.get("correct_information", "N/A"),
                    "Confidence Score": f"{resolution.get('confidence_score', 0)}%"
                })
                
                progress_bar.progress((index + 1) / len(selected_claims))
                time.sleep(0.5) # Protect API endpoints against threshold adjustments
                
            status_ticker.empty()
            progress_bar.empty()
            st.session_state.verification_results = pd.DataFrame(results_pool)

# Output Assessment Layer
if st.session_state.verification_results is not None:
    st.subheader("3. Verification Report Matrix")
    df = st.session_state.verification_results
    
    # Generate high-level metric indicators
    col1, col2, col3 = st.columns(3)
    col1.metric("Verified Data Points ✅", len(df[df['Status'] == 'VERIFIED']))
    col2.metric("Inaccurate Anomalies ⚠️", len(df[df['Status'] == 'INACCURATE']))
    col3.metric("Confirmed Contradictions 🚨", len(df[df['Status'] == 'FALSE']))
    
    # Custom colored cell highlights mapping logic
    def dynamic_row_coloring(val):
        if val == 'VERIFIED':
            return 'background-color: #15803D; color: white;'
        elif val == 'INACCURATE':
            return 'background-color: #854D0E; color: white;'
        elif val == 'FALSE':
            return 'background-color: #991B1B; color: white;'
        return ''

    styled_output_matrix = df.style.applymap(dynamic_row_coloring, subset=['Status'])
    st.dataframe(styled_output_matrix, use_container_width=True, hide_index=True)
    
    # Prepare export asset buffers
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    st.download_button(
        label="Download Verification Audit Report (CSV)",
        data=csv_bytes,
        file_name="truth_layer_audit_report.csv",
        mime="text/csv",
        use_container_width=True
    )
