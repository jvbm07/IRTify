import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain model
llm = OpenAI(openai_api_key=openai_api_key)

def load_files(questions_file, topics_file):
    """Load the questions and topics files from UploadedFile objects."""
    questions_df = pd.read_csv(questions_file)
    topics = [topic.strip() for topic in topics_file.read().decode("utf-8").split(',')]
    return questions_df, topics

def map_questions_to_topics(questions_df, topics):
    """Map each question to one or more topics using LangChain for intent classification."""
    # Prepare mapping for each question
    mapping = {}
    progress_text = "Mapping operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)
    percent_complete = 0
    total_len = len(questions_df)
    pace = 1/total_len
    for idx, row in questions_df.iterrows():
        my_bar.progress(percent_complete + pace, text=progress_text)
        percent_complete += pace

        question_text = row.iloc[1] + " " + " ".join(row.iloc[2:].dropna().astype(str))
        
        # Create a prompt for topic classification
        prompt = (
            f"Given the following topics: {', '.join(topics)}\n\n"
            f"Classify the following question into relevant topics. "
            f"Return only the relevant topics in a comma-separated list with no extra spaces or punctuation:\n\n"
            f"Do not return anything besides that."
            f"Question: {question_text}\n\n"
            f"Format: Topic1, Topic2, Topic3"
        )
        
        # Get topics from the LLM
        response = llm(prompt)
        identified_topics = response.strip().split(', ')  # Assumes model returns comma-separated topics
        mapping[row['question_number']] = identified_topics

    my_bar.empty()
    questions_df['mapped_topics'] = questions_df['question_number'].map(mapping)
    return questions_df

def plot_topic_distribution(mapped_df):
    """Plot the distribution of topics covered across all questions."""
    topic_counts = pd.Series([topic for topics in mapped_df['mapped_topics'] for topic in topics]).value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=topic_counts.index, y=topic_counts.values, ax=ax, palette='viridis')
    ax.set_title("Topic Distribution in Assessment Questions")
    ax.set_xlabel("Topics")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

def display_question_mapping(mapped_df):
    """Display each question and its mapped topics in a table."""
    st.subheader("Question to Topic Mapping")
    st.table(mapped_df[['question_number', 'statement', 'mapped_topics']])

def create_semantic_report(questions_file, topics_file):
    """Main function to create and display the semantic report."""
    questions_df, topics = load_files(questions_file, topics_file)
    mapped_df = map_questions_to_topics(questions_df, topics)
    
    # Display the question-topic mapping and topic distribution chart
    display_question_mapping(mapped_df)
    plot_topic_distribution(mapped_df)
