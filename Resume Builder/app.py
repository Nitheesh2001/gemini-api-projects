import streamlit as st
from fpdf import FPDF
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get resume content
def get_resume_content(name, email, phone, education, experience, skills, projects):
    prompt = f"""
    You are a professional resume builder. Based on the following details, create a well-structured resume.
    Name: {name}
    Email: {email}
    Phone: {phone}
    Education: {education}
    Experience: {experience}
    Skills: {skills}
    Projects: {projects}
    
    Provide a detailed and formatted resume.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Function to generate PDF
def generate_pdf(resume_content, filename="resume.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in resume_content.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True, align='L')

    pdf.output(filename)
    return filename

# Streamlit app
st.set_page_config(page_title="Resume Builder", layout="wide")
st.title("Resume Builder")

# Collect user input
st.header("Enter your details")
name = st.text_input("Full Name", placeholder="e.g., John Doe")
email = st.text_input("Email", placeholder="e.g., john.doe@example.com")
phone = st.text_input("Phone", placeholder="e.g., +1234567890")
education = st.text_area("Education", placeholder="e.g., B.Sc. in Computer Science from XYZ University")
experience = st.text_area("Experience", placeholder="e.g., Software Engineer at ABC Corp. (2018-2022)")
skills = st.text_area("Skills", placeholder="e.g., Python, Machine Learning, Data Analysis")
projects = st.text_area("Projects", placeholder="e.g., AI Chatbot, E-commerce Website")

# Button to submit the form
if st.button("Generate Resume"):
    if name and email and phone and education and experience and skills and projects:
        with st.spinner("Generating your resume..."):
            try:
                resume_content = get_resume_content(name, email, phone, education, experience, skills, projects)
                st.subheader("Your Resume")
                st.text(resume_content)
                
                # Generate and provide download link for PDF
                pdf_filename = generate_pdf(resume_content)
                with open(pdf_filename, "rb") as file:
                    st.download_button(
                        label="Download Resume as PDF",
                        data=file,
                        file_name="resume.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill out all the fields.")

if __name__ == "__main__":
    st.sidebar.header("Resume Builder")
