import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ctt import create_ctt_report, calculate_ctt_metrics
from irt import create_irt_report
from dif import create_dif_report
from semantic import create_semantic_report, map_questions_to_topics, load_files
from network import create_network_report, create_full_network
from student_report import generate_student_report

import numpy as np
from scipy.special import expit

# Function to reset the page
def reset_page():
    st.session_state.uploaded_file = None
    st.session_state.df = None
    st.session_state.home = True
    st.session_state.questions_file = None
    st.session_state.topics_file = None
    st.session_state.mapped_df = None
    st.session_state.info_file = None


# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'questions_file' not in st.session_state:
    st.session_state.questions_file = None
if 'topics_file' not in st.session_state:
    st.session_state.topics_file = None
if 'info_file' not in st.session_state:
    st.session_state.info_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'mapped_df' not in st.session_state:
    st.session_state.mapped_df = None
if 'question_info_df' not in st.session_state:
    st.session_state.question_info_df = None
if 'home' not in st.session_state:
    st.session_state.home = True  # Start on the home page by default
# Set up the page configuration
st.set_page_config(page_title="New Project - Quiz Analysis Studio", layout="wide")

# Sidebar menu
st.sidebar.title("Project Menu")

# Home button
if st.sidebar.button("🏠 Home"):
    st.session_state.home = True
    st.stop()

# Documentation button
if st.sidebar.button("📚 Documentation"):
    st.write("Redirecting to the documentation...")
    st.stop()

# Create New Project button
if st.sidebar.button("🆕 Create New Project"):
    if st.radio("Warning: Creating a new project will erase the current project. Are you sure you want to continue?", ["No", "Yes"]) == "Yes":
        reset_page()
        st.rerun()
    st.session_state.home = False

# Landing page content
if st.session_state.home:
    st.title("Welcome to the Quiz Analysis Studio")
    st.write("""
        **Quiz Analysis Studio** is a comprehensive tool designed to help educators analyze quiz data 
        effectively. With features for Classical Test Theory (CTT) analysis, Item Response Theory (IRT) 
        analysis, and Differential Item Functioning (DIF) analysis, this application allows you to gain 
        valuable insights into your students' performance and the effectiveness of your assessments.

        **Key Features:**
        - Upload quiz data in CSV format.
        - Generate detailed CTT reports with histograms for each question.
        - Conduct IRT and DIF analysis to explore more advanced psychometric properties.
        - User-friendly interface with multiple tabs for easy navigation.

        Use the sidebar to upload your quiz data and start your analysis journey!
    """)
    st.session_state.home = False  # After displaying the home page, set it to False
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Dataset", "CTT Analysis", "IRT Analysis", "DIF Analysis", "Semantic Analysis", "Network Analysis", "Student Report"])

def highlight_rows(row):
    if row.name == 0:  # First row (index 0)
        return ['background-color: lightblue'] * len(row)
    elif row.name == 1:  # Second row (index 1)
        return ['background-color: lightgreen'] * len(row)
    else:
        return [''] * len(row)  # No color for other rows

def calculate_scores(answer_sheet_df):
    if answer_sheet_df.empty:
        return None

    answer_sheet_df.reset_index(inplace=True)
    # Separate the correct answers and student responses
    correct_answers = answer_sheet_df.iloc[1, 1:]  # Assumes second row has correct answers, ignoring first column
    student_responses_df = answer_sheet_df.iloc[2:, 1:]  # Remaining rows are student responses

    # Create a new DataFrame to store 1s and 0s for correct/incorrect answers
    result_df = student_responses_df.apply(lambda row: row == correct_answers, axis=1).astype(int)
    # Calculate and add the score for each student
    result_df['Score'] = result_df.iloc[:].sum(axis=1)

    # Add the student IDs back to the result DataFrame
    result_df.insert(0, 'student_id', answer_sheet_df.iloc[2:, 0].values)

    result_df.reset_index(inplace=True, drop=True)

    return result_df

def plot_scores(scores):
    plt.figure(figsize=(10, 6))
    
    # Determine the minimum and maximum scores for bin creation
    min_score = scores["Score"].min()
    max_score = scores["Score"].max()
    
    # Create bins for the histogram
    bins = range(min_score, max_score + 2)  # +2 to include the maximum score
    
    plt.hist(scores["Score"], bins=bins, color='skyblue', edgecolor='black', width=0.8)
    plt.title("Histogram of Scores")
    plt.xlabel("Scores")
    plt.ylabel("Frequency")
    
    st.pyplot(plt)

# Function to generate a histogram for a selected item
def plot_item_histogram(df, item_index):
    # Select the item (column) and count the occurrences of each alternative
    item_responses = df.iloc[1:, item_index]
    counts = item_responses.value_counts(sort=False)
    
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    counts.plot(kind='bar')
    plt.title(f'Distribution of Responses for Item {item_index + 1}')
    plt.xlabel('Alternatives')
    plt.ylabel('Number of Students')
    st.pyplot(plt)

with tab1:
    st.header("Dataset")
    
    # Main dataset file upload
    
    uploaded_file = st.file_uploader("Upload Main CSV (Required)", type=["csv"])
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.df = pd.read_csv(uploaded_file, header=None)
        st.session_state.df.set_index(st.session_state.df.columns[0], inplace=True)
    
    if st.session_state.df is not None:
        styled_df = st.session_state.df.reset_index()
        st.dataframe(
            styled_df.style
            .applymap(lambda _: "background-color: lightblue", subset=pd.IndexSlice[styled_df.index[0:1], :])  # First row in blue
            .applymap(lambda _: "background-color: lightgreen", subset=pd.IndexSlice[styled_df.index[1:2], :])  # Second row in green
            .applymap(lambda _: "background-color: yellow", subset=pd.IndexSlice[styled_df.index[2:], styled_df.columns[0]])  # First column from third row onward in yellow
        )



        # Calculate scores button
        if st.button("Calculate Scores"):
            scores = calculate_scores(st.session_state.df)
            if scores is not None:
                st.session_state.scores = scores
                st.write("Scores for each student:")
                st.dataframe(scores)
                plot_scores(scores)
    else:
        st.write("No file uploaded.")
    
    # Optional additional file uploads for semantic analysis
    st.subheader("Optional Files for Semantic Analysis")
    
    # Optional questions CSV file
    questions_file = st.file_uploader("Upload Questions CSV (Optional)", type="csv")
    if questions_file:
        st.session_state.questions_file = questions_file

    # Optional topics TXT file
    topics_file = st.file_uploader("Upload Topics TXT (Optional)", type="txt")
    if topics_file:
        st.session_state.topics_file = topics_file


# Tab 2: CTT Analysis
with tab2:
    st.header("CTT Analysis Dashboard")
    if st.session_state.df is not None:
        # Create CTT Report
        if st.button("Create CTT Report"):
            report = create_ctt_report(st.session_state.df)
            for img in report:
                st.markdown(img, unsafe_allow_html=True)
        
        # Select multiple items to analyze
        st.subheader("Analyze Items")
        items_selected = st.multiselect("Select items to analyze:", range(1, st.session_state.df.shape[1] + 1))
        
        if st.button("Show Item Analysis"):
            for item in items_selected:
                st.write(f"Item {item}:")
                plot_item_histogram(st.session_state.df, item - 1)
                st.write("---")  # Add a separator between histograms
    else:
        st.write("No data uploaded.")

# Tab 3: IRT Analysis
# Function to calculate the Item Characteristic Curve (ICC)
def calculate_icc(theta, a, b, c=0):
    """
    Calculate the probability of a correct response based on IRT.
    
    Parameters:
    - theta: Ability level of the respondent
    - a: Discrimination parameter (slope)
    - b: Difficulty parameter (location of the curve)
    - c: Guessing parameter (lower asymptote), default is 0 (for 2PL or 1PL models)
    
    Returns:
    - Probability of a correct response (P(theta)).
    """
    # 3PL Model: P(theta) = c + (1 - c) / (1 + exp(-a * (theta - b)))
    return c + (1 - c) / (1 + np.exp(-a * (theta - b)))


with tab3:
    st.header("IRT Analysis Dashboard")
    if st.session_state.df is not None:
        # Create IRT Report
        if st.button("Create IRT Report"):
            report = create_irt_report(st.session_state.df)
            for img in report:
                st.markdown(img, unsafe_allow_html=True)
    else:
        st.write("No data uploaded.")

# Tab 4: DIF Analysis

def calculate_dif():
    # Generate x values greater than 0
    x = np.linspace(0.1, 10, 100)
    
    # Generate two slightly different sigmoid curves (logistic function)
    y1 = expit(x - 5)  # Sigmoid curve 1
    y2 = expit(x - 4.5)  # Sigmoid curve 2 (slightly shifted)

    return x, y1, y2
with tab4:

    st.header("DIF Analysis Dashboard")
    if st.session_state.df is not None:
        df = st.session_state.df
        info_file = st.file_uploader("Upload Students Info CSV", type="csv")
        if info_file:
            st.session_state.info_file = pd.read_csv(info_file)
            # Allow the user to select a column for grouping
            group_column = st.selectbox("Select the column for group analysis:", options=st.session_state.info_file.columns)
        
        # Create DIF Report if a column is selected and button is clicked
        if st.button("Create DIF Report"):
            if group_column:
                report = create_dif_report(st.session_state.df, st.session_state.info_file, group_column)
                for img in report:
                    st.markdown(img, unsafe_allow_html=True)
            else:
                st.write("Please select a valid column for group analysis.")
    else:
        st.write("No data uploaded.")

with tab5:  # Tab 5: Semantic Analysis
    st.header("Semantic Analysis Dashboard")
    
    # Check if optional files for semantic analysis are available
    if st.session_state.questions_file is not None and st.session_state.topics_file is not None:
        if st.button("Create Semantic Report"):
            create_semantic_report(st.session_state.questions_file, st.session_state.topics_file)
    else:
        st.write("Upload the Questions CSV and Topics TXT files in Tab 1 to enable Semantic Analysis.")

with tab6:
    if st.session_state.df is not None and st.session_state.questions_file is not None and st.session_state.topics_file is not None:
        if st.button("Create Network Report"):
            questions_df, topics = load_files(st.session_state.questions_file, st.session_state.topics_file)
            mapped_df = map_questions_to_topics(questions_df, topics)
            ctt_metrics = calculate_ctt_metrics(st.session_state.df)

            st.session_state.mapped_df = mapped_df
            report_message = create_network_report(ctt_metrics, mapped_df)
            create_full_network(st.session_state.scores, st.session_state.question_info_df, st.session_state.info_file)
            st.success(report_message)
    else:
        st.write("Metrics or questions data is not available.")

with tab7:
    if st.button("Generate Student Report"):
        generate_student_report('r4',st.session_state.scores, st.session_state.mapped_df, st.session_state.info_file)