import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Title and subtitle of the app
st.title("IRTify")
st.subheader("Empowering Psychometric Analysis with IRT and DIF Insights")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Check if a file is uploaded
if uploaded_file is not None:
    # Read the uploaded CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Create an expandable section to show the DataFrame
    with st.expander("Show Data"):
        st.write("Here is the content of the CSV file:")
        st.dataframe(df)

    # Optional: Show some basic statistics of the DataFrame
    with st.expander("Show Statistics"):
        st.write("Here are some basic statistics of the CSV file:")
        st.write(df.describe())

    # Widget to select columns for analysis
    st.write("Select the items to analyze:")
    selected_columns = st.multiselect("Choose columns", options=df.columns)

    # Display selected columns if any
    if selected_columns:
        st.write("Selected columns for analysis:")
        st.dataframe(df[selected_columns])

        # Plotting options
        st.write("Select the type of plot:")
        plot_type = st.selectbox("Choose plot type", ["Line Plot", "Bar Plot", "Scatter Plot", "Histogram"])

        if plot_type == "Line Plot":
            st.line_chart(df[selected_columns])
        elif plot_type == "Bar Plot":
            st.bar_chart(df[selected_columns])
        elif plot_type == "Scatter Plot":
            if len(selected_columns) >= 2:
                x_axis = st.selectbox("Select X-axis", options=selected_columns)
                y_axis = st.selectbox("Select Y-axis", options=selected_columns)
                st.write("Scatter Plot")
                fig, ax = plt.subplots()
                sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax)
                st.pyplot(fig)
            else:
                st.write("Please select at least two columns for a scatter plot.")
        elif plot_type == "Histogram":
            column_to_plot = st.selectbox("Select column for histogram", options=selected_columns)
            st.write("Histogram")
            fig, ax = plt.subplots()
            sns.histplot(df[column_to_plot], ax=ax, kde=True)
            st.pyplot(fig)

else:
    st.write("Please upload a CSV file to view its content and select columns for analysis.")
