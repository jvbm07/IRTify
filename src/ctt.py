import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import streamlit as st

def create_ctt_report(df):
    # Assuming the first row contains the correct answers
    correct_answers = df.iloc[0]
    report = []
    
    # Extract all unique options from the dataset (excluding the first column)
    all_options = sorted(df.iloc[1:].stack().unique())
    
    # Generate a histogram for each question
    for col in df.columns:
        # Initialize the layout: two columns
        col1, col2 = st.columns(2)

        # Plot the histogram in the left column
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Count the answers, including missing categories
            answers = df[col].value_counts().reindex(all_options, fill_value=0)
            
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
            st.subheader(f'Data for {col}')
            st.dataframe(answers.reset_index().rename(columns={'index': 'Answer', col: 'Count'}))

    return report

def plot_item_histogram_with_answer(df, item_index):
    """
    Plots a histogram for a selected item with the correct answer highlighted.

    Parameters:
    df (pd.DataFrame): The dataset containing the responses.
    item_index (int): The index of the item (column) to analyze.

    Returns:
    None: The function directly plots the histogram.
    """
    # The first row contains the correct answers
    correct_answer = df.iloc[0, item_index]
    
    # Select the item (column) and count the occurrences of each alternative
    item_responses = df.iloc[1:, item_index]
    counts = item_responses.value_counts(sort=False)
    
    # Create a color map for the bars
    colors = ['blue' if alt != correct_answer else 'green' for alt in counts.index]
    
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    counts.plot(kind='bar', color=colors)
    plt.title(f'Distribution of Responses for Item {item_index + 1}')
    plt.xlabel('Alternatives')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=0)
    plt.show()