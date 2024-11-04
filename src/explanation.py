import pandas as pd
import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Load API key from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain model
llm = OpenAI(openai_api_key=openai_api_key)

def get_correct_answers(answer_sheet_df):
    # Retrieve the correct answers from the answer sheet DataFrame
    return answer_sheet_df.iloc[1].values[1:]  # Assuming the first row has titles and the second row has correct answers

def generate_explanation(question, correct_answer):
    # Create a prompt for OpenAI
    prompt = f"Explain why the answer to the question '{question}' is '{correct_answer}'."
    
    try:
        # Call OpenAI API
        explanation = llm(prompt)
        return explanation
    except Exception as e:
        print(f"Error occurred while calling OpenAI: {e}")
        return None

def create_explanations(question_df, answer_sheet_df):
    correct_answers = get_correct_answers(answer_sheet_df)
    
    explanations = {}
    progress_text = "Explaining operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    percent_complete = 0
    total_len = len(question_df)
    pace = 1/total_len
    count = 0
    for i, row in question_df.iterrows():
        my_bar.progress(percent_complete + pace, text=progress_text)
        percent_complete += pace

        question_text = row['statement']  # Extract the question statement
        correct_answer = correct_answers[i]  # Get the correct answer for the question
        explanation = generate_explanation(question_text, correct_answer)
        
        if explanation:
            explanations[question_text] = explanation
        if count > 10:
            break
        count += 1
    my_bar.empty()
    return explanations

    

