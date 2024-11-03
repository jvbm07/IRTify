import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr

def create_ctt_report(df):
    # Assuming the first row contains the correct answers
    correct_answers = df.iloc[1]
    students_answers_df = df.iloc[2:]
    ctt_metrics = calculate_ctt_metrics(df)

    report = []
    
    # Extract all unique options from the dataset (excluding the first column)
    all_options = sorted(df.iloc[2:].stack().unique())
    
    # Generate a histogram for each question
    for col in students_answers_df.columns:
        # Initialize the layout: two columns
        col1, col2 = st.columns(2)

        # Plot the histogram in the left column
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Count the answers, including missing categories
            answers = students_answers_df[col].value_counts().reindex(all_options, fill_value=0)
            
            sns.barplot(x=answers.index, y=answers.values, ax=ax, palette="viridis")

            # Highlight the correct answer
            correct_answer = correct_answers[col]
            if correct_answer in all_options:
                ax.bar(all_options.index(correct_answer), answers[correct_answer], color='red', alpha=0.7, label='Correct Answer')

            ax.set_title(f'Question: {col}')
            ax.set_xlabel('Answer')
            ax.set_ylabel('Number of Responses')
            ax.set_xticks(range(len(all_options)))
            ax.set_xticklabels(all_options)
            ax.legend()

            st.pyplot(fig)

        # Display the data for this item in the right column
        with col2:
            st.subheader(f'CTT Metrics for {col}')
            question_metrics = ctt_metrics[ctt_metrics['question_number'] == col]
            st.table(question_metrics[['difficulty-rate', 'discrimination-rate', 'cronbachs-alpha']])
    return report

# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import streamlit as st

def calculate_difficulty_rate(responses, correct_answer):
    """Calculates the difficulty rate for a given question."""
    return (responses == correct_answer).mean()

def calculate_discrimination_rate(responses, correct_answer, scores):
    """Calculates the discrimination rate for a given question."""
    upper_group = responses[scores >= scores.median()]
    lower_group = responses[scores < scores.median()]
    return (upper_group == correct_answer).mean() - (lower_group == correct_answer).mean()

def calculate_cronbach_alpha(responses, correct_answer, scores):
    """Calculates Cronbach's alpha for a given question."""
    item_scores = (responses == correct_answer).astype(int)
    return pearsonr(item_scores, scores)[0]

def calculate_ctt_metrics(df):
    """Calculates all CTT metrics for each question in the dataset."""
    correct_answers = df.iloc[1]
    students_answers_df = df.iloc[2:]
    scores = (students_answers_df == correct_answers).sum(axis=1)

    metrics = {
        'question_number': [],
        'difficulty-rate': [],
        'discrimination-rate': [],
        'cronbachs-alpha': []
    }
    
    for col in students_answers_df.columns:
        
        correct_answer = correct_answers[col]
        responses = students_answers_df[col]
        
        metrics['difficulty-rate'].append(calculate_difficulty_rate(responses, correct_answer))
        metrics['discrimination-rate'].append(calculate_discrimination_rate(responses, correct_answer, scores))
        metrics['cronbachs-alpha'].append(calculate_cronbach_alpha(responses, correct_answer, scores))
        metrics['question_number'].append(col)

    return pd.DataFrame(metrics)

# def create_ctt_report(df):
#     """Generates the CTT report with histograms and metrics."""
#     # Generate CTT metrics
#     ctt_metrics = calculate_ctt_metrics(df)

#     # Assuming the first row contains the correct answers
#     correct_answers = df.iloc[0]
#     report = []
    
#     # Extract all unique options from the dataset (excluding the first column)
#     all_options = sorted(df.iloc[1:].stack().unique())
    
#     # Generate a histogram for each question
#     for col in df.columns:
#         # Initialize the layout: two columns
#         col1, col2 = st.columns(2)

#         # Plot the histogram in the left column
#         with col1:
#             fig, ax = plt.subplots(figsize=(8, 6))
            
#             # Count the answers, including missing categories
#             answers = df[col].value_counts().reindex(all_options, fill_value=0)
            
#             sns.barplot(x=answers.index, y=answers.values, ax=ax, palette="viridis")

#             # Highlight the correct answer
#             correct_answer = correct_answers[col]
#             if correct_answer in all_options:
#                 ax.bar(all_options.index(correct_answer), answers[correct_answer], color='red', alpha=0.7, label='Correct Answer')

#             ax.set_title(f'Question: {col}')
#             ax.set_xlabel('Answer')
#             ax.set_ylabel('Number of Responses')
#             ax.set_xticks(range(len(all_options)))
#             ax.set_xticklabels(all_options)
#             ax.legend()

#             st.pyplot(fig)

#         # Display the CTT metrics for this item in the right column
#         with col2:
#             st.subheader(f'CTT Metrics for {col}')
#             question_metrics = ctt_metrics[ctt_metrics['Question'] == col]
#             st.table(question_metrics[['Difficulty Rate', 'Discrimination Rate', 'Cronbach\'s Alpha']])

#     return report
