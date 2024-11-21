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
    return answer_sheet_df.iloc[1].values[0:]  # Assuming the first row has titles and the second row has correct answers

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
    answer_map = {'A': 2, 'B': 3, 'C': 4, 'D': 5}
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
        question_num = row['question_number']
        
        # Get the correct answer letter for this question from correct_answers_df
        correct_letter = correct_answers[int(question_num)-1].upper()

        if len(correct_letter) > 0 and correct_letter in answer_map:
            # Find the correct column index based on the answer letter
            correct_col = answer_map[correct_letter[0]]

            # Get the text for the correct alternative
            correct_text = row.iloc[correct_col]

            # Generate the explanation for the correct answer
            explanation = generate_explanation(question_text, correct_text)
            
            # For debugging or output purposes
            st.subheader(f"Question {question_num}: {question_text}")
            st.subheader(f"Correct Answer: {correct_text}")
            st.markdown(f"Explanation: {explanation}\n")
        
        if explanation:
            explanations[question_text] = explanation
        if count > 10:
            break
        count += 1
    my_bar.empty()
    return explanations

    

def get_correct_alternative_text(questions_info_df, correct_answers):
    # Map letters to column offsets (0-based index adjustment)
    answer_map = {'A': 2, 'B': 3, 'C': 4, 'D': 5, 'E': 6}

    # Initialize a dictionary to store each question's correct alternative text
    correct_alternatives = {}

    for i, row in questions_info_df.iterrows():
        question_num = row['question_number']
        
        # Get the correct answer letter for this question
        correct_letter = correct_answers.get(question_num)

        if correct_letter in answer_map:
            # Find the correct column index based on the answer letter
            correct_col = answer_map[correct_letter]
            
            # Get the text for the correct alternative
            correct_text = row.iloc[correct_col]
            
            # Store it in the dictionary for later use
            correct_alternatives[question_num] = correct_text
    
    return correct_alternatives