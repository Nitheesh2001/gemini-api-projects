import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get career path recommendation
def get_career_recommendation(education, goals):
    prompt = f"""
    You are a career counselor. Based on the following details, provide a detailed career roadmap for the student.
    Education: {education}
    Goals: {goals}
    
    Provide a step-by-step guide on how the student can achieve their career goals.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Streamlit app
st.set_page_config(page_title="Career Counseling Chatbot", layout="wide")
st.title("Career Counseling Chatbot")

# Collect user input
st.header("Tell us about yourself")
education = st.text_area("Education Background", placeholder="e.g., Computer Science, Commerce, Biology, Chemistry, Physics, etc.")
goals = st.text_area("Career Goals", placeholder="e.g., Machine Learning Engineer, Software Engineer, Data Scientist, etc.")

# Button to submit the form
if st.button("Get Career Roadmap"):
    if education and goals:
        with st.spinner("Generating your career roadmap..."):
            try:
                recommendation = get_career_recommendation(education, goals)
                st.subheader("Your Career Roadmap")
                st.write(recommendation)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill out all the fields.")

if __name__ == "__main__":
    st.sidebar.header("Career Counseling Chatbot")
