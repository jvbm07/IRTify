import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def generate_student_report(student_id, student_scores_df, question_info_df, class_info_df):
    report = {}
    # 1. Basic Information
    student_data = student_scores_df[student_scores_df['student_id'] == student_id]
    if student_data.empty:
        return f"Student ID {student_id} not found."
    
    student_class = class_info_df[class_info_df['student_id'] == student_id]['TP_SEXO'].values[0]
    total_score = student_data['Score'].values[0]
    total_questions = len(student_data.columns) - 2
    correct_percentage = (total_score / total_questions) * 100
    
    report['Student ID'] = student_id
    report['Class'] = student_class
    report['Total Score'] = total_score
    report['Correct Answer Percentage'] = f"{correct_percentage:.2f}%"

    # Class average comparison
    class_avg_score = student_scores_df[student_scores_df['student_id'].isin(class_info_df[class_info_df['TP_SEXO'] == student_class]['student_id'])].iloc[:, 1:].sum(axis=1).mean()
    report['Class Average Score'] = class_avg_score

    # 2. Topic Mastery
    topic_correct_counts = {}
    topic_total_counts = {}
    for question in student_data.columns[1:]:
        # Get the topic(s) mapped to the question if it exists in question_info_df
        question_topics = question_info_df[question_info_df['question_number'] == question]['mapped_topics']

        if not question_topics.empty:
            question_topics = question_topics.values[0]
        else:
            question_topics = "Topic not found"  # or set to None, or handle it as needed
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
    for question in student_data.columns[1:-1]:
        correct = student_data[question].values[0] == 1
        difficulty = question_info_df[question_info_df['question_number'] == question]['difficulty-rate'].values[0]
        if correct and difficulty > 0.5:  # Arbitrary high difficulty threshold
            high_diff_correct.append(question)
        elif not correct and difficulty <= 0.5:  # Arbitrary low difficulty threshold
            low_diff_incorrect.append(question)

    report['High-Difficulty Questions Answered Correctly'] = high_diff_correct
    report['Low-Difficulty Questions Answered Incorrectly'] = low_diff_incorrect

    # 4. Class Standing and Percentile
    scores = student_scores_df.iloc[:, 1:].sum(axis=1).values
    percentile_rank = (scores < total_score).sum() / len(scores) * 100
    report['Percentile Ranking'] = f"{percentile_rank:.2f}%"

    st.write(f"### Report for Student ID: {report['Student ID']}")
    st.write(f"Class: {report['Class']}")
    st.write(f"Total Score: {report['Total Score']}")
    st.write(f"Correct Answer Percentage: {report['Correct Answer Percentage']}")
    st.write(f"Class Average Score: {report['Class Average Score']}")
    st.write(f"Percentile Ranking: {report['Percentile Ranking']}")

    # Call visualization functions
    plot_topic_mastery(report)
    plot_score_comparison(report)
    plot_low_difficulty_incorrect(report)
    plot_performance_radar(report)
    generate_study_plan(report, question_info_df)
    return

def plot_topic_mastery(report_df):
    # Extract and clean topic mastery data
    topic_mastery = report_df['Topic Mastery']
    filtered_topic_mastery = {k: float(v.replace('%', '')) for k, v in topic_mastery.items() if float(v.replace('%', '')) > 0}
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(filtered_topic_mastery.keys(), filtered_topic_mastery.values(), color='skyblue')
    ax.set_xlabel('Topics')
    ax.set_ylabel('Mastery (%)')
    ax.set_title(f"Topic Mastery for Student {report_df['Student ID']}")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

def plot_score_comparison(report_df):
    total_score = report_df['Total Score']
    class_average_score = report_df['Class Average Score']
    max_score = max(total_score, class_average_score) * 1.2  # Scale slightly higher than max for display

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.barh(0, total_score, color='blue', alpha=0.7, height=0.3, label='Student Score')
    ax.barh(0, class_average_score, color='green', alpha=0.7, height=0.3, label='Class Average')
    ax.set_xlim(0, max_score)
    ax.set_yticks([])
    ax.set_xticks([0, max_score / 2, max_score])
    ax.legend()
    ax.set_title(f"Score Comparison: Student vs Class Average")
    st.pyplot(fig)

def plot_low_difficulty_incorrect(report_df):
    low_difficulty_incorrect = report_df['Low-Difficulty Questions Answered Incorrectly']
    
    # Plotting
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(low_difficulty_incorrect)), [1] * len(low_difficulty_incorrect), color='lightcoral')
    ax.set_yticks(range(len(low_difficulty_incorrect)))
    ax.set_yticklabels([f"Question {q}" for q in low_difficulty_incorrect])
    ax.set_title("Low-Difficulty Questions Answered Incorrectly")
    ax.set_xlabel("Incorrect Answer")
    ax.set_xlim(0, 1)
    st.pyplot(fig)



def plot_performance_radar(report_df):
    categories = ['Correct Answer Percentage', 'Percentile Ranking']
    values = [float(report_df['Correct Answer Percentage'].replace('%', '')),
              float(report_df['Percentile Ranking'].replace('%', ''))]
    
    # Radar chart data
    values += values[:1]  # Repeat the first value at the end for circular graph
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='skyblue', alpha=0.4)
    ax.plot(angles, values, color='skyblue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title("Performance Radar")
    st.pyplot(fig)


def generate_study_plan(report_df, question_info_df):
    # Extract low-difficulty questions answered incorrectly from the report
    low_difficulty_incorrect = report_df['Low-Difficulty Questions Answered Incorrectly']
    
    # Filter question info to get topics and difficulty for incorrect low-difficulty questions
    incorrect_questions_info = question_info_df[
        question_info_df['question_number'].isin(low_difficulty_incorrect)
    ]
    
    # Explode 'mapped_topics' column to handle cases where it contains lists
    incorrect_questions_info = incorrect_questions_info.explode('mapped_topics')
    
    # Count incorrect answers per topic and average difficulty per topic
    topic_difficulty = (
        incorrect_questions_info.groupby('mapped_topics')
        .agg(
            question_count=('question_number', 'count'),  # number of questions answered incorrectly in each topic
            avg_difficulty=('difficulty-rate', 'mean')    # average difficulty of questions in each topic
        )
        .sort_values(by=['avg_difficulty', 'question_count'], ascending=[True, False])
    ).reset_index()
    
    # Display study plan in a table
    st.write("### Study Plan")
    st.write("This plan ranks topics by priority, focusing on those with low-difficulty questions that were answered incorrectly.")
    st.table(topic_difficulty.rename(columns={
        'mapped_topics': 'Topic',
        'question_count': 'Questions Incorrectly Answered',
        'avg_difficulty': 'Average Difficulty'
    }))
    
    # Additional explanation to guide the student
    st.write("""
    - **Focus on mastering topics with the lowest average difficulty** where mistakes occurred.
    - These are foundational topics and should be prioritized for review.
    - **Topics with more incorrect answers** indicate areas of particular weakness and should be reviewed thoroughly.
    """)

