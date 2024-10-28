import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import numpy as np

def process_image(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Process each contour to extract information
    data = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 50:  # Assuming a minimum size for bubbles
            # Extract the region of interest (ROI)
            roi = thresh[y:y+h, x:x+w]
            # Analyze the ROI to determine if a bubble is filled
            filled = np.mean(roi) > 127  # Adjust this threshold based on your needs
            data.append((x, y, filled))

    # Sort data by x and y coordinates to match the answer sheet layout
    data.sort(key=lambda k: (k[1], k[0]))

    # Convert data to DataFrame
    student_data = pd.DataFrame(data, columns=['x', 'y', 'filled'])
    return student_data

# Title and subtitle of the app
st.title("IRTify")
st.subheader("Empowering Psychometric Analysis with IRT and DIF Insights")

# File uploader for image
uploaded_image = st.file_uploader("Upload your answer sheet image", type=["jpg", "jpeg", "png"])

# Check if an image is uploaded
if uploaded_image is not None:
    # Read the uploaded image
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    # Display the uploaded image
    st.image(image, channels="BGR", caption="Uploaded Answer Sheet", use_column_width=True)

    # Process the image to extract data
    student_data = process_image(image)

    # Display the extracted data
    with st.expander("Show Extracted Data"):
        st.write("Here is the extracted data from the answer sheet:")
        st.dataframe(student_data)

    # Optionally, visualize the contours on the image
    for _, row in student_data.iterrows():
        color = (0, 255, 0) if row['filled'] else (0, 0, 255)
        cv2.rectangle(image, (row['x'], row['y']), (row['x'] + 50, row['y'] + 50), color, 2)
    
    st.image(image, channels="BGR", caption="Processed Answer Sheet", use_column_width=True)

else:
    st.write("Please upload an answer sheet image to process and extract data.")

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
