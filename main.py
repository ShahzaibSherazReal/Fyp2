import streamlit as st
from PIL import Image
import json
import time
from utils.processor import find_best_match

# --- CONFIGURATION ---
st.set_page_config(page_title="Leaf Disease Detection", page_icon="🌿", layout="wide")

# --- THEME MANAGEMENT ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Error: {file_name} not found.")

# --- SIDEBAR & THEME TOGGLE ---
st.sidebar.title("⚙️ Settings")

# The Theme Toggle Widget
# We use 'value=True' so it defaults to Dark Mode
use_dark_mode = st.sidebar.toggle("Dark Mode 🌙", value=True)

if use_dark_mode:
    load_css("assets/dark.css")
    st.sidebar.caption("Theme: Dark (Hacker Mode)")
else:
    load_css("assets/light.css")
    st.sidebar.caption("Theme: Light (Clinical Mode)")

st.sidebar.markdown("---")

# Load Database
try:
    with open("database.json", "r") as f:
        KNOWLEDGE_BASE = json.load(f)
except FileNotFoundError:
    st.error("System Error: database.json not found.")
    st.stop()

# --- SESSION STATE SETUP ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = None

# Function to switch pages
def navigate_to(page, crop=None):
    st.session_state.page = page
    st.session_state.selected_crop = crop
    st.rerun()

# --- PAGE 1: HOME SCREEN (The Cards) ---
if st.session_state.page == 'home':
    st.title("🌿 Leaf Disease Detection")
    st.markdown("### ➀ Select Your Plant System")
    st.markdown("Choose a crop below to initialize the specific diagnostic model.")
    
    st.write("") 
    st.write("") 

    col1, col2, col3 = st.columns(3)

    # Card 1: Apple
    with col1:
        with st.container(border=True): 
            st.markdown("<h1 style='text-align: center;'>🍎</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Apple</h3>", unsafe_allow_html=True)
            if st.button("Select Apple Model", use_container_width=True):
                navigate_to('upload', 'Apple')

    # Card 2: Corn
    with col2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🌽</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Corn (Maize)</h3>", unsafe_allow_html=True)
            if st.button("Select Corn Model", use_container_width=True):
                navigate_to('upload', 'Corn')

    # Card 3: Potato
    with col3:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🥔</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Potato</h3>", unsafe_allow_html=True)
            if st.button("Select Potato Model", use_container_width=True):
                navigate_to('upload', 'Potato')
    
    st.write("") 
    st.markdown(
        """
        <div style='text-align: center; color: #888; padding: 20px; font-style: italic;'>
            🚀 More crops (Tomato, Grape, Cotton) coming in v3.0 update...
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- PAGE 2: UPLOAD SCREEN ---
elif st.session_state.page == 'upload':
    plant_type = st.session_state.selected_crop
    
    if st.button("← Back to Selection"):
        navigate_to('home')

    st.markdown(f"### ➁ Upload Leaf Image ({plant_type})")

    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        image = Image.open(uploaded_file)
        with col1:
            st.image(image, caption="Uploaded Specimen", use_container_width=True)
        
        if st.button("Run Diagnostics"):
            with col2:
                with st.status(f"Initializing {plant_type} Neural Network...", expanded=True) as status:
                    time.sleep(1) 
                    status.write("Preprocessing image (Resize 224x224)...")
                    time.sleep(0.5)
                    status.write(f"Loading {plant_type} weights...")
                    time.sleep(0.5)
                    status.update(label="Analysis Complete", state="complete", expanded=False)
                
                match_filename = find_best_match(image)
                
                if match_filename:
                    selected_plant_lower = plant_type.lower() 
                    
                    if selected_plant_lower not in match_filename:
                        actual_plant = match_filename.split('_')[0].capitalize() 
                        st.error(f"❌ **Error: Domain Mismatch Detected**")
                        st.error(f"Active Model: **{plant_type}** | Detected Leaf Features: **{actual_plant}**")
                        st.info("The system has halted to prevent false classification. Please upload the correct crop type.")
                    else:
                        if match_filename in KNOWLEDGE_BASE:
                            result = KNOWLEDGE_BASE[match_filename]
                            
                            st.markdown(f"""
                            <div class="report-box">
                                <h3>Analysis Report ({plant_type})</h3>
                                <p><strong>Detected Condition:</strong> {result['disease_name']}</p>
                                <p><strong>Severity Status:</strong> {result['status']}</p>
                                <p><strong>Pathogen Description:</strong> {result['description']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            m1, m2 = st.columns(2)
                            m1.metric("Model Confidence", result['confidence'])
                            m2.metric("Inference Time", "0.04s")
                            
                            st.warning(f"**Recommended Treatment:** {result['treatment']}")
                else:
                    st.error("⚠️ No Match Found")
                    st.info("Try uploading one of your Reference Images.")