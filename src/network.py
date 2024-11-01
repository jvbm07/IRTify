import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import networkx as nx

def generate_bipartite_graph(metrics_df):
    # Create a bipartite graph
    B = nx.Graph()
    
    # Define the two sets of nodes
    questions = metrics_df['question_number'].tolist()
    topics = []

    # Collect unique topics
    for mapped_topics in metrics_df['mapped_topics']:
        if isinstance(mapped_topics, str):
            mapped_topics = mapped_topics.split(",")
        topics.extend([topic.strip() for topic in mapped_topics])

    topics = list(set(topics))  # Get unique topics

    # Add nodes for questions and topics
    B.add_nodes_from(questions, bipartite=0)  # Questions
    B.add_nodes_from(topics, bipartite=1)  # Topics

    # Create edges between questions and their mapped topics
    for index, row in metrics_df.iterrows():
        question_number = row['question_number']
        mapped_topics = row['mapped_topics']
        
        if isinstance(mapped_topics, str):
            mapped_topics = mapped_topics.split(",")
        
        mapped_topics = [topic.strip() for topic in mapped_topics]  # Clean up whitespace

        for topic in mapped_topics:
            B.add_edge(question_number, topic)  # Connect question to topic

    return B

def plot_bipartite_graph(B):
    plt.figure(figsize=(12, 8))

    # Get the positions for nodes in a bipartite layout
    pos = nx.bipartite_layout(B, nodes=[n for n in B.nodes() if n in B.nodes() if isinstance(n, int)])  # Questions are integers

    # Draw the bipartite graph
    nx.draw_networkx_nodes(B, pos, nodelist=[n for n in B.nodes() if isinstance(n, int)], node_color='skyblue', label='Questions')
    nx.draw_networkx_nodes(B, pos, nodelist=[n for n in B.nodes() if isinstance(n, str)], node_color='lightgreen', label='Topics')
    nx.draw_networkx_edges(B, pos, width=2, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(B, pos, font_size=10)

    plt.title("Bipartite Graph of Questions and Topics")
    plt.axis('off')  # Turn off the axis
    plt.legend()  # Add legend to differentiate questions and topics
    
    # Use Streamlit to display the plot
    st.pyplot(plt)  # Display the figure in Streamlit
    plt.clf()  # Clear the figure to avoid overlapping in future plots

def generate_topic_graph(metrics_df):
    # Create a directed graph
    G = nx.Graph()

    # Iterate through the DataFrame rows
    for index, row in metrics_df.iterrows():
        question_number = row['question_number']
        mapped_topics = row['mapped_topics']  # Assume this is already a list

        # Create edges between all pairs of topics for this question
        if isinstance(mapped_topics, str):
            mapped_topics = mapped_topics.split(",")  # Split only if it's a string
        mapped_topics = [topic.strip() for topic in mapped_topics]  # Clean up whitespace

        for i in range(len(mapped_topics)):
            for j in range(i + 1, len(mapped_topics)):
                topic1 = mapped_topics[i]
                topic2 = mapped_topics[j]
                
                # Add an edge between the topics
                G.add_edge(topic1, topic2, question=question_number)

    return G


def plot_topic_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)  # Positions for all nodes

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=12)

    plt.title("Topic Relationship Graph")
    plt.axis('off')  # Turn off the axis
    
    # Use Streamlit to display the plot
    st.pyplot(plt)  # Display the figure in Streamlit
    plt.clf()  # Clear the figure to avoid overlapping in future plots

def create_network_report(metrics_df, questions_df, difficulty_col='difficulty-rate', question_col='question_number', topic_col='mapped_topics'):
    """
    Generate a network report visualizing the relationship between question difficulty and topics.

    Parameters:
    - metrics_df: DataFrame containing the metrics with difficulty rates and questions.
    - questions_df: DataFrame containing questions and their mapped topics.
    - difficulty_col: Column name for difficulty metrics.
    - question_col: Column name for questions.
    - topic_col: Column name for mapped topics.
    """

    # Merge the metrics DataFrame with the questions DataFrame on the question column
    print(metrics_df)
    print(questions_df)
    merged_df = pd.merge(metrics_df, questions_df[[question_col, topic_col]], on=question_col)

    # Check if the merged DataFrame is not empty
    if not merged_df.empty:
        plt.figure(figsize=(12, 6))
        
        st.dataframe(merged_df)
        G = generate_bipartite_graph(merged_df)
        plot_bipartite_graph(G)
        # G = generate_topic_graph(merged_df)
        # plot_topic_graph(G)
        return "Network report created successfully."
    
    else:
        return "Error: Merged DataFrame is empty. Check your input data."

