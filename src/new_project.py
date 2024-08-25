import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ctt import create_ctt_report

# Function to reset the page
def reset_page():
    st.session_state.uploaded_file = None
    st.session_state.df = None
    st.session_state.home = True


# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
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
tab1, tab2, tab3, tab4 = st.tabs(["Dataset", "CTT Analysis", "IRT Analysis", "DIF Analysis"])

def calculate_scores(df):
    if df.empty:
        return None

    # Drop the first row by index
    df = df.drop(df.index[0])

    # The first row contains the correct answers
    correct_answers = df.iloc[0, 1:].values  # Exclude the first column (student IDs)
    
    # Set the first column as the index (student IDs)
    df.set_index(df.columns[0], inplace=True)
    df.index.name = 'Student_ID'
    
    # Remove the first row (which contains correct answers) from the DataFrame
    df = df[1:]
    
    # Get the responses and compare them to correct answers
    responses = df.values
    scores = []

    for response in responses:
        score = sum([r == c for r, c in zip(response, correct_answers)])
        scores.append(score)

    # Create a DataFrame with the results
    scores_df = pd.DataFrame({'Score': scores}, index=df.index)
    return scores_df

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
    # Streamlit app code
    st.header("Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file

        st.session_state.df = pd.read_csv(uploaded_file, header=None)
        st.session_state.df.set_index(st.session_state.df.columns[0], inplace=True)
    
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df)
        
        # Calculate and display scores
        if st.button("Calculate Scores"):
            scores = calculate_scores(st.session_state.df)
            if scores is not None:
                st.write("Scores for each student:")
                st.dataframe(scores)
    else:
        st.write("No file uploaded.")

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
with tab3:
    st.header("IRT Analysis Dashboard")
    if st.session_state.df is not None:
        # Your IRT analysis code goes here
        st.write("IRT Analysis Results will be displayed here.")
    else:
        st.write("No data uploaded.")

# Tab 4: DIF Analysis
with tab4:
    st.header("DIF Analysis Dashboard")
    if st.session_state.df is not None:
        # Your DIF analysis code goes here
        st.write("DIF Analysis Results will be displayed here.")
    else:
        st.write("No data uploaded.")
