import pandas as pd
import streamlit as st

def generate_student_report(answer_sheet_df, metrics_df):
    # Create a dictionary to hold student mastery data
    student_mastery = {}

    # Map difficulty rates to topics
    topic_difficulty_map = metrics_df.set_index('question_number')['mapped_topics'].to_dict()

    # Iterate through each student in the answer sheet
    for student_id in answer_sheet_df.index:
        student_mastery[student_id] = {'mastered': [], 'needs_study': []}

        # Get student's answers
        student_answers = answer_sheet_df.loc[student_id]

        # Iterate through each question in the answer sheet
        for question_number, student_answer in student_answers.items():
            if question_number != 'true_answers':  # Skip true answers row
                correct_answer = answer_sheet_df['true_answers'][question_number]
                mapped_topics = topic_difficulty_map.get(question_number, "")
                
                if student_answer == correct_answer:
                    # If the answer is correct, add to mastered topics
                    for topic in mapped_topics.split(","):
                        student_mastery[student_id]['mastered'].append(topic.strip())
                else:
                    # If the answer is incorrect, add to topics needing study
                    for topic in mapped_topics.split(","):
                        student_mastery[student_id]['needs_study'].append(topic.strip())

    # Convert to DataFrame for better display
    report_df = pd.DataFrame.from_dict(student_mastery, orient='index')

    # Display report in Streamlit
    st.header("Student Mastery Report")
    st.dataframe(report_df)
