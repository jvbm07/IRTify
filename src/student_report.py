import pandas as pd
import streamlit as st

def generate_student_report(student_id, student_scores_df, question_info_df, class_info_df):
    report = {}

    # 1. Basic Information
    student_data = student_scores_df[student_scores_df['student_id'] == student_id]
    if student_data.empty:
        return f"Student ID {student_id} not found."
    
    student_class = class_info_df[class_info_df['student_id'] == student_id]['gender'].values[0]
    total_score = student_data['Score'].values[0]
    total_questions = len(student_data.columns) - 2
    correct_percentage = (total_score / total_questions) * 100
    
    report['Student ID'] = student_id
    report['Class'] = student_class
    report['Total Score'] = total_score
    report['Correct Answer Percentage'] = f"{correct_percentage:.2f}%"

    # Class average comparison
    class_avg_score = student_scores_df[student_scores_df['student_id'].isin(class_info_df[class_info_df['gender'] == student_class]['student_id'])].iloc[:, 1:].sum(axis=1).mean()
    report['Class Average Score'] = class_avg_score

    # 2. Topic Mastery
    topic_correct_counts = {}
    topic_total_counts = {}
    for question in student_data.columns[1:]:
        question_topics = question_info_df[question_info_df['question_number'] == question]['mapped_topics'].values[0]
        correct = student_data[question].values[0] == 1
        for topic in question_topics:
            topic_total_counts[topic] = topic_total_counts.get(topic, 0) + 1
            if correct:
                topic_correct_counts[topic] = topic_correct_counts.get(topic, 0) + 1

    topic_mastery = {topic: (topic_correct_counts.get(topic, 0) / total) * 100
                     for topic, total in topic_total_counts.items()}
    report['Topic Mastery'] = {k: f"{v:.2f}%" for k, v in topic_mastery.items()}

    # 3. Difficulty Analysis
    high_diff_correct = []
    low_diff_incorrect = []
    for question in student_data.columns[1:]:
        correct = student_data[question].values[0] == 1
        difficulty = question_info_df[question_info_df['question_number'] == question]['difficulty'].values[0]
        if correct and difficulty > 0.7:  # Arbitrary high difficulty threshold
            high_diff_correct.append(question)
        elif not correct and difficulty <= 0.3:  # Arbitrary low difficulty threshold
            low_diff_incorrect.append(question)

    report['High-Difficulty Questions Answered Correctly'] = high_diff_correct
    report['Low-Difficulty Questions Answered Incorrectly'] = low_diff_incorrect

    # 4. Class Standing and Percentile
    scores = student_scores_df.iloc[:, 1:].sum(axis=1).values
    percentile_rank = (scores < total_score).sum() / len(scores) * 100
    report['Percentile Ranking'] = f"{percentile_rank:.2f}%"
    
    # Classify performance category
    if percentile_rank > 90:
        report['Performance Category'] = "Excellent"
    elif percentile_rank > 70:
        report['Performance Category'] = "Above Average"
    elif percentile_rank > 50:
        report['Performance Category'] = "Average"
    else:
        report['Performance Category'] = "Needs Improvement"
    
    st.dataframe(report)
    return report
