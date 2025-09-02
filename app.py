# app.py

import streamlit as st
import os
import uuid
from crew import CemexCrew  # Ensure this is uncommented when you run with the crew
import base64
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="CEMEX Damage Analysis Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
    # page_icon=r"D:\\Crewai Projects\\cemex\\Symbol.svg" # This path may not work on deployment
)



sample_result = """
CEMEX Repair Solution Guide
Problem Summary:
Cracks in indoor walls can occur due to various reasons, including settling of the building, temperature changes, or moisture. The most common types of cracks are those less than 2.0mm wide, which can be effectively repaired using appropriate methods and materials.
Recommended CEMEX Products:
WHO60® Grout: A thixotropic, shrink-compensated cement-based grout with polymer additives used for bonding helical reinforcement bars to masonry.
Plaster-based filler: For refilling the cracks after treatment.
Pure 150 Pro Epoxy Resin: For cases where the body of the brick behind is fractured.
Step-by-Step Repair Protocol:
Preparation:
Identify the type of crack. For cracks less than 2.0mm in width, proceed with the following steps.
Ensure the area is clean and free from dust or debris.
V-Grooving:
Scratch the crack back to the brickwork in a ‘V’ shape. This allows for better adhesion of the repair materials.
Remove all loose particles, ideally by flushing with water.
Injection of Epoxy (if necessary):
If the crack indicates that the body of the brick is fractured, inject Pure 150 Pro Epoxy Resin into the crack. Allow it to cure as per manufacturer instructions.
Filling the Crack:
Refill the ‘V’ groove with a plaster-based filler. This should be done in three coats to allow for shrinkage.
Allow each coat to dry for approximately 24 hours before applying the next coat.
Final Touches:
Once the final coat is dry, sand the area to ensure a smooth finish.
Repaint the area to match the surrounding wall.
Inspection:
After repairs, inspect the area for any signs of re-cracking or further damage. If cracks reappear, it may indicate an underlying structural issue that requires further assessment.
Reference Links:
ABI Information Sheet - Crack Repair Procedure
Masonry Wall Reinforcement Guide
This guide provides a clear, actionable repair strategy for cracks in indoor walls, utilizing recommended CEMEX products and methods based on internal documentation
"""

# --- Sidebar Logo ---
# This uses Streamlit's native function to place the logo at the top of the sidebar.
# It's cleaner and more reliable than custom HTML.
# st.logo(r"D:\\Crewai Projects\\cemex\\Logo.png",size="large")

# --- Custom CSS for Modern CEMEX Branding ---
st.markdown("""
    <style>
        /* General Body and Font */
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333333;
        }

            
        /* Main App Container */
        .stApp {
            background-color: #FFFFFF;
        }


        /* Sidebar Styling */
        .st-emotion-cache-1kyxreq {
            background-color: #F0F2F5;
            border-right: 1px solid #E0E0E0;
        }
        
        /* Style for the "Upload Damage Image" title in the sidebar */
        .st-emotion-cache-1kyxreq h1 {
            font-size: 22px;
            color: linear-gradient(135deg, #023185, #E3303D);;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #E0E0E0;
        }

        /* Chat Message Container Styling */
        .stChatMessage {
            background-color: transparent;
            padding: 0;
            margin: 0 0 1rem 0;
        }

        /* Custom Cards for Bot (Assistant) Response */
        [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 35px;
        padding: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        
        /* Target the markdown elements rendered inside our styled container */
        [data-testid="stVerticalBlockBorderWrapper"] h3 {
            color: #023185; /* CEMEX Blue */
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #F0F2F5;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"] p > strong {
            color: #023185; /* CEMEX Blue */
            font-weight: bold;
            font-size: 1.1em;
        }

        [data-testid="stVerticalBlockBorderWrapper"] ul, 
        [data-testid="stVerticalBlockBorderWrapper"] ol {
            padding-left: 25px;
            margin-top: 5px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] li {
            margin-bottom: 8px;
        }

        /* --- STYLES FOR THE HEADER SECTION --- */
        .app-header h1 {
            /* 1. Apply the gradient as the background image */
            background:  -webkit-linear-gradient(5deg, #023185, #E3303D);
            
            
            /* 2. Clip the background to the shape of the text */
            -webkit-background-clip: text; /* For Safari/Chrome */
            background-clip: text;
            
            /* 3. Make the text itself transparent to show the background */
            color: transparent;

            /* --- Your existing layout styles --- */
            font-size: 2.2rem;
            font-weight: bold;
            margin-bottom: 0.2rem;
            margin-top: 1.5rem;
            padding: 0;
        }

        .app-header p {
            /* This styles the subtitle "Upload an image..." */
            color: #4A4A4A;
            font-size: 1rem;
            margin: 0;
            padding: 0;
        }

        .app-header hr {
            /* This styles the horizontal line */
            margin-top: 0.8rem;
            margin-bottom: 1.5rem;
            border: none;
            border-top: 1px solid #E0E0E0;
        }
            
        /* User message styling */
        .user-message-card {
            background-color: #FFFFFF;
            border-radius: 100px;
            font-color: #333333;
            padding: 16px;
            border-left: 8px solid #E3303D;
        }
            
        /* --- STYLES FOR THE CUSTOM PDF DOWNLOAD LIST --- */
        .pdf-list-container {
            background-color:#FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 15px; /* Softer radius */
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .pdf-download-link {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            border-radius: 10px;
            text-decoration: none;
            color: #333333;
            transition: background-color 0.2s ease-in-out;
            margin-bottom: 5px; /* Space between links */
        }
        .pdf-download-link:hover {
            background-color: #dbe6f9     ; /* Light grey hover effect */
            color: #023185; /* Brand blue on hover */
        }
        .pdf-download-link:last-child {
            margin-bottom: 0; /* No margin on the last item */
        }
        .pdf-icon {
            font-size: 1.3em;
            margin-right: 12px;
        }

    </style>
""", unsafe_allow_html=True)
# In app.py, add this new function near the top

# In app.py, replace your old function with this one.
# Make sure you have 'import base64' at the top of your file.

# In app.py, replace the old function with this corrected one.
# Ensure you have 'import base64' at the top of your file.

def display_reference_documents(folder_path):
    """
    Scans a folder for PDF files and displays them as a clean, custom-styled list.
    """
    try:
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

        if pdf_files:
            st.markdown("---")
            st.markdown("#### Reference Documents")

            # Start of the custom HTML container
            html_content = '<div class="pdf-list-container">'
            
            for pdf_file in pdf_files:
                file_path = os.path.join(folder_path, pdf_file)
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # --- THIS IS THE CORRECTED LINE ---
                # Build the link on a single line to avoid rendering issues.
                html_content += f'<a href="data:application/pdf;base64,{base64_pdf}" download="{pdf_file}" class="pdf-download-link"><span class="pdf-icon">📄</span><span>{pdf_file}</span></a>'
            
            html_content += '</div>'
            st.markdown(html_content, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error(f"Error: The specified folder was not found: {folder_path}")
# --- Main Page Title and Description ---
# st.title("Damage Analysis Assistant")
# --- Main Page Title and Description ---
st.markdown("""
<div class="app-header">
    <h1>Damage Analysis Assistant</h1>
    <p>Upload an image of structural damage to receive a detailed repair guide.</p>
    <hr>
</div>
""", unsafe_allow_html=True)
# --- Function to Display Bot Response in Cards ---
def display_results_in_cards(result_text):
    st.markdown(result_text, unsafe_allow_html=True)

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    
    if message["role"] == "user":
        with st.chat_message("user",avatar=r"D:\\Crewai Projects\\cemex\\Icons8\\icons8-account-50.png"):
            st.markdown(f"<div class='user-message-card'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant",avatar=r"D:\\Crewai Projects\\cemex\\Symbol.svg"):
            display_results_in_cards(message["content"])

# --- Sidebar for Image Upload (Consolidated) ---
with st.sidebar:
    st.markdown("<h1>Upload Damage Image</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
    if uploaded_file:
        
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

# --- Main Chat Input and Logic ---
if prompt := st.chat_input("e.g., How do I repair this spalling concrete?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user",avatar=r"D:\\Crewai Projects\\cemex\\Icons8\\icons8-account-50.png"):
        st.markdown(f"<div class='user-message-card'>{prompt}</div>", unsafe_allow_html=True)

    image_path = None
    if uploaded_file:
        temp_dir = "temp_images"
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        image_path = os.path.join(temp_dir, f"{uuid.uuid4()}{os.path.splitext(uploaded_file.name)[1]}")
        with open(image_path, "wb") as f: f.write(uploaded_file.getvalue())

    # --- Execute the Crew and Display Response ---
    # Make sure to uncomment the CemexCrew import and this block to run the analysis
    with st.chat_message("assistant",avatar=r"D:\\Crewai Projects\\cemex\\Symbol.svg"):
        spinner_text = "Analyzing image and preparing repair guide..." if image_path else "Analyzing your query..."
        with st.spinner(spinner_text):
          
            cemex_crew_manager = CemexCrew()
            crew = cemex_crew_manager.get_crew(image_uploaded=bool(image_path))
            inputs = {'query': prompt}
            if image_path:
                inputs['image_path'] = image_path
            result = crew.kickoff(inputs=inputs)
            result=result.tasks_output[-1].raw
            
            display_results_in_cards(result)
            st.session_state.messages.append({"role": "assistant", "content":result})
            bucket_folder_path = r"D:\\Crewai Projects\\cemex\\bucket_files"
            display_reference_documents(bucket_folder_path)

    # --- Clean up the temporary image file ---
    if image_path and os.path.exists(image_path):
        os.remove(image_path)