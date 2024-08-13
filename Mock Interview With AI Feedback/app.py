import streamlit as st
import pyttsx3
import speech_recognition as sr
import os
from dotenv import load_dotenv
import google.generativeai as genai
import threading
import queue

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to get feedback from Gemini API
def get_feedback(answer, context):
    prompt = f"""
    Context: {context}
    Answer: {answer}

    Provide feedback on the answer and suggest areas of improvement.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Function to generate follow-up question based on previous answer
def generate_followup_question(previous_answer):
    prompt = f"""
    Based on the following answer, generate a follow-up question.
    Answer: {previous_answer}
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# Function to capture audio response and convert to text
def get_audio_response(q):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        st.write("Listening for your response...")
        audio = recognizer.listen(source)
        try:
            response = recognizer.recognize_google(audio)
            q.put(response)
        except sr.UnknownValueError:
            q.put("Could not understand audio")
        except sr.RequestError as e:
            q.put(f"Could not request results; {e}")

# Function to generate initial questions based on user input
def generate_initial_questions(job_type, experience_level, interview_format, focus_areas):
    initial_questions = [
        f"Tell me about your experience in {job_type}.",
        f"What are your strengths and weaknesses as a {experience_level} professional?",
        f"How do you prepare for a {interview_format} interview?",
        f"What are the key focus areas in {focus_areas}?"
    ]
    return initial_questions

# Streamlit app
st.set_page_config(page_title="Mock Interview with AI Feedback", layout="wide")
st.title("Mock Interview with AI Feedback")

# Collect user input
st.header("Tell us about yourself")
job_type = st.text_area("Job or Industry", placeholder="e.g., software engineering, marketing, finance, healthcare, etc.")
experience_level = st.text_area("Current Level of Experience", placeholder="e.g., entry-level, mid-level, senior-level, executive-level")
interview_format = st.text_area("Preferred Interview Format", placeholder="e.g., behavioral, technical, case study, panel interview")
focus_areas = st.text_area("Specific Focus Areas", placeholder="e.g., common interview questions, salary negotiation, body language")

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = generate_initial_questions(job_type, experience_level, interview_format, focus_areas)
    st.session_state.current_question = 0
    st.session_state.responses = []
    st.session_state.current_response = ""
    st.session_state.recording = False
    st.session_state.total_feedback = []
    st.session_state.interview_started = False

# Button to start the mock interview
if st.button("Start Mock Interview"):
    if job_type and experience_level and interview_format and focus_areas:
        st.session_state.questions = generate_initial_questions(job_type, experience_level, interview_format, focus_areas)
        st.session_state.current_question = 0
        st.session_state.responses = []
        st.session_state.current_response = ""
        st.session_state.recording = False
        st.session_state.total_feedback = []
        st.session_state.interview_started = True

# Function to handle recording and feedback loop
def handle_question():
    if st.session_state.current_question < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.current_question]
        st.write(f"Question {st.session_state.current_question + 1}: {question}")

        q = queue.Queue()
        if st.session_state.recording:
            st.write("Recording...")
            response_thread = threading.Thread(target=get_audio_response, args=(q,))
            response_thread.start()
            response_thread.join()
            if not q.empty():
                st.session_state.current_response = q.get()
            st.session_state.recording = False  # Stop recording after getting response
        else:
            if st.button("Double click to Start Recording Your Answer", key=f"stop_recording_{st.session_state.current_question}"):
                st.session_state.recording = True

        if st.session_state.current_response:
            st.write(f"Recorded Answer: {st.session_state.current_response}")
            feedback = get_feedback(st.session_state.current_response, st.session_state.questions[st.session_state.current_question])
            st.write(f"Feedback: {feedback}")

            # Calculate feedback score
            score = min(max(len(st.session_state.current_response.split()) // 5, 1), 10)
            st.session_state.total_feedback.append(score)

            followup_question = generate_followup_question(st.session_state.current_response)
            st.session_state.questions.append(followup_question)
            st.session_state.current_question += 1
            st.session_state.current_response = ""
            handle_question()  # Recursive call to handle the next question

# Loop through questions and feedback until "Finish" is clicked
if 'interview_started' in st.session_state and st.session_state.interview_started:
    handle_question()

# Finish button to end the mock interview
finish_button_placeholder = st.empty()
if finish_button_placeholder.button("Finish"):
    st.write("Mock Interview Finished")
    st.session_state.current_question = len(st.session_state.questions)
    st.session_state.interview_started = False

    # Calculate total feedback score
    if st.session_state.total_feedback:
        total_score = sum(st.session_state.total_feedback) // len(st.session_state.total_feedback)
    else:
        total_score = 0

    if total_score >= 7:
        st.write(f"Overall Feedback Score: {total_score}/10")
        st.write("Great job! Keep it up!")
    elif 4 <= total_score < 7:
        st.write(f"Overall Feedback Score: {total_score}/10")
        st.write("Good effort! There are some areas to improve.")
    else:
        st.write(f"Overall Feedback Score: {total_score}/10")
        st.write("Needs improvement. Focus on the feedback provided.")
        
    # Center the "Finish" button
    finish_button_placeholder.markdown("""
        <style>
        div.stButton > button:first-child {
            margin: 0 auto;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    st.sidebar.header("Mock Interview with AI Feedback")
