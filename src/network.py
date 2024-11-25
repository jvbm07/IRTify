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
    # Adjust the question_number in metrics_df to match the range in questions_df
    metrics_df['question_number'] += questions_df['question_number'].min()

    # Merge after transformation
    merged_df = pd.merge(metrics_df, questions_df[[question_col, topic_col]], on=question_col)

    # merged_df = pd.merge(metrics_df, questions_df[[question_col, topic_col]], on=question_col)

    # Check if the merged DataFrame is not empty
    if not merged_df.empty:
        plt.figure(figsize=(12, 6))
        
        st.dataframe(merged_df)
        st.session_state.question_info_df = merged_df
        G = generate_bipartite_graph(merged_df)
        plot_bipartite_graph(G)
        # G = generate_topic_graph(merged_df)
        # plot_topic_graph(G)
        return merged_df
    
    else:
        return "Error: Merged DataFrame is empty. Check your input data."

def create_full_network(student_scores_df, question_info_df, student_dif_df):

    # Sample data frame structure:
    # student_scores_df: columns -> ['student_id', 'question_id', 'got_it_right', 'total_score']
    # question_info_df: columns -> ['question_id', 'topic', 'difficulty']
    # student_dif_df: columns -> ['student_id', 'class']

    # Initialize the graph
    G = nx.Graph()
    question_info_df['question_number'] -= question_info_df['question_number'].min()

    # Step 1: Add student nodes with color by class and size by total score
    student_classes_dict = student_dif_df.set_index('student_id')['TP_SEXO'].to_dict()
    class_colors = {'M': 'red', 'F': 'blue'}  # Example colors for each class

    # Set a size scaling factor for student nodes based on their total score
    for _, row in student_scores_df[['student_id', 'Score']].drop_duplicates().iterrows():
        student_id = row['student_id']
        total_score = row['Score']
        student_class = student_classes_dict.get(student_id, 'Unknown')
        color = class_colors.get(student_class, 'gray')
        size = 50 + 20 * total_score  # Adjust base size and scaling factor as needed
        G.add_node(student_id, type='student', color=color, size=size)

    # Step 2: Add question nodes with size by difficulty
    difficulty_dict = question_info_df.set_index('question_number')['difficulty-rate'].to_dict()
    for question_id, difficulty in difficulty_dict.items():
        G.add_node(question_id, type='question', color='green', size=500 * difficulty)  # Scale the difficulty for visibility

    # Step 3: Add topic nodes
    topics = question_info_df['mapped_topics'].explode().unique()
    for topic in topics:
        G.add_node(topic, type='topic', color='orange')  # Color all topics the same for simplicity

    for _, row in student_scores_df.iterrows():
        student_id = row['student_id']
        for question_number in student_scores_df.columns[1:]:  # Skip 'student_id' column
            if row[question_number] == 1:  # Check if the student got the question right
                G.add_edge(student_id, question_number)

    # Step 5: Add edges between questions and their topics
    for _, row in question_info_df.iterrows():
        question = row['question_number']
        topics = row['mapped_topics']
        
        # Check if topics is a list, then iterate to create an edge for each topic
        if isinstance(topics, list):
            for topic in topics:
                G.add_edge(question, topic)
        else:
            G.add_edge(question, topics)  # if it's a single topic, directly add the edge

    # Visualization
    # Create a color and size map based on node attributes
    node_colors = [G.nodes[node].get('color', 'gray') for node in G.nodes]
    node_sizes = [G.nodes[node].get('size', 100) for node in G.nodes]  # Default size if 'size' attribute not set

    # Draw the network
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)  # Use spring layout for better separation

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

    plt.title("Student-Question-Topic Network with Score-based Node Sizes")
    plt.show()

    st.pyplot(plt)  # Display the figure in Streamlit
    plt.clf()  # Clear the figure to avoid overlapping in future plots