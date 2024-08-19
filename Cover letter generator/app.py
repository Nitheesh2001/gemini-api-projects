import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get cover letter from Gemini API
def generate_cover_letter(details):
    prompt = f"""
    Generate a professional cover letter based on the following details:

    1. Full Name: {details['full_name']}
    2. Email: {details['email']}
    3. Phone Number: {details['phone']}
    4. Address: {details['address']}
    5. Company Name: {details['company_name']}
    6. Job Title: {details['job_title']}
    7. Introduction: {details['introduction']}
    8. Relevant Experience: {details['experience']}
    9. Skills: {details['skills']}
    10. Closing Statement: {details['closing_statement']}
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Streamlit app
st.set_page_config(page_title="Cover Letter Generator", layout="wide")
st.title("Cover Letter Generator")

# Collect user details
st.header("Fill in the following details to generate your cover letter")

details = {}
details['full_name'] = st.text_input("Full Name", placeholder="Enter your full name")
details['email'] = st.text_input("Email", placeholder="Enter your email address")
details['phone'] = st.text_input("Phone Number", placeholder="Enter your phone number")
details['address'] = st.text_area("Address", placeholder="Enter your address")
details['company_name'] = st.text_input("Company Name", placeholder="Enter the company name")
details['job_title'] = st.text_input("Job Title", placeholder="Enter the job title you are applying for")
details['introduction'] = st.text_area("Introduction", placeholder="Write a brief introduction about yourself")
details['experience'] = st.text_area("Relevant Experience", placeholder="Describe your relevant experience")
details['skills'] = st.text_area("Skills", placeholder="List your skills")
details['closing_statement'] = st.text_area("Closing Statement", placeholder="Write a closing statement")

# Button to submit the form
if st.button("Generate Cover Letter"):
    if all(details.values()):
        with st.spinner("Generating your cover letter..."):
            try:
                cover_letter = generate_cover_letter(details)
                st.subheader("Your Generated Cover Letter")
                st.write(cover_letter)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill out all the fields.")

if __name__ == "__main__":
    st.sidebar.header("Cover Letter Generator")
