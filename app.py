import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# App eke page setting
st.set_page_config(page_title="Spec Extractor & VAT Calculator", layout="wide")

# Sidebar - API Key and VAT Calculator
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password", help="Paste your Google AI Studio API key here")
    
    st.markdown("---")
    st.header("🧮 VAT Calculator (18%)")
    calc_type = st.radio("Calculation Type:", ["Add VAT (Have Price Without VAT)", "Extract VAT (Have Price With VAT)"])
    price_input = st.number_input("Enter Amount (Rs.):", min_value=0.0, format="%.2f")
    
    if price_input > 0:
        if "Add VAT" in calc_type:
            vat = price_input * 0.18
            total = price_input + vat
            st.success(f"**Price Without VAT:** Rs. {price_input:,.2f}\n\n**VAT (18%):** Rs. {vat:,.2f}\n\n**Total With VAT:** Rs. {total:,.2f}")
        else:
            base = price_input / 1.18
            vat = price_input - base
            st.success(f"**Price Without VAT:** Rs. {base:,.2f}\n\n**VAT (18%):** Rs. {vat:,.2f}\n\n**Total With VAT:** Rs. {price_input:,.2f}")

# Main Interface
st.title("📄 IT Product Spec Extractor")
st.write("Upload a blank specification sheet and enter the product model to auto-fill the details.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("1. Upload Specification Sheet (Image)", type=['png', 'jpg', 'jpeg'])
with col2:
    model_name = st.text_input("2. Enter Product Brand & Model (e.g., Dell Inspiron 15):")

if st.button("Generate Specifications", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar first!")
    elif not uploaded_file or not model_name:
        st.warning("⚠️ Please upload an image and enter a product model name.")
    else:
        try:
            # Gemini API Setup
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            image = Image.open(uploaded_file)
            
            # Encoded search query for the PDF link
            search_query = urllib.parse.quote(f"{model_name} official brochure specifications filetype:pdf")
            
            prompt = f"""
            You are an IT & Office Automation Product Expert at a top Sri Lankan IT company.
            1. Analyze the uploaded specification sheet image and identify the required fields.
            2. Find the highly accurate technical specifications for: {model_name}.
            3. Generate a line-by-line output matching the image fields.
            
            Format strictly as:
            **[Field Name]:** [Extracted Value]
            
            Constraints:
            - Align specs with Sri Lankan market standards (e.g., 230V, standard warranty).
            - If a detail is unavailable, write: "As per manufacturer's official documentation". Do not guess.
            
            At the very end of your output, add this exact download link on a new line:
            [📥 Download Official Brochure PDF](https://www.google.com/search?q={search_query})
            """
            
            with st.spinner("Extracting and processing specifications... Please wait."):
                response = model.generate_content([prompt, image])
                st.markdown("### 📋 Generated Specifications")
                st.info(response.text)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
