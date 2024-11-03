import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2
import streamlit as st
from irt import calculate_irt_metrics

def create_dif_report(answer_df, student_info_df, group_column):
    """
    Perform Differential Item Functioning (DIF) analysis based on a specified group column.
    
    Parameters:
    - answer_df: DataFrame with student responses and true answers.
    - student_info_df: DataFrame with student IDs and groups (e.g., 'Gender').
    - group_column: Column name in student_info_df to be used for grouping (e.g., 'gender').
    
    Returns:
    - A DataFrame with DIF analysis results, including IRT parameter differences and significance.
    """
    # Select student answer rows, starting from the third row
    # Select student answer rows starting from the third row
    student_answers_df = answer_df.iloc[2:].copy()  # Start from third row onward
    student_answers_df.reset_index(inplace=True)

    
    column_names = ['student_id'] + [str(i) for i in range(1, len(student_answers_df.columns))]
    student_answers_df.columns = column_names    

    # Ensure student_id is string type in both DataFrames for consistent merging
    student_answers_df['student_id'] = student_answers_df['student_id'].astype(str)
    student_info_df['student_id'] = student_info_df['student_id'].astype(str)

    # Merge on 'student_id'
    merged_df = student_answers_df.merge(student_info_df, on='student_id', how='left')
    

    # Separate correct answers from student responses
    correct_answers = merged_df.iloc[0, 1:-1]  # True answers row (excluding 'student_id' and group_column)
    student_data = merged_df.iloc[1:].reset_index(drop=True)  # Remaining rows as student data
    
    # Check if group_column exists in the data
    if group_column not in student_data.columns:
        raise ValueError(f"The specified group column '{group_column}' does not exist in the merged data.")

    # Group the data by the specified column
    groups = student_data[group_column].unique()
    if len(groups) != 2:
        raise ValueError("DIF analysis requires exactly two groups for comparison.")

    group1, group2 = groups
    group1_data = student_data[student_data[group_column] == group1].iloc[:, 1:-1]
    group2_data = student_data[student_data[group_column] == group2].iloc[:, 1:-1]
    
    # Calculate IRT parameters for each group

    group1_data = group1_data.values.tolist()
    group2_data = group2_data.values.tolist()

    correct_answers = correct_answers.values.tolist()
    irt_metrics_g1 = calculate_irt_metrics(correct_answers, group1_data)
    irt_metrics_g2 = calculate_irt_metrics(correct_answers, group2_data)

    # Prepare results DataFrame for DIF analysis
    dif_results = []
    
    for item in range(len(correct_answers)):
        # Extract parameters for the item in both groups
        difficulty_g1 = irt_metrics_g1.loc[item, 'Difficulty']
        discrimination_g1 = irt_metrics_g1.loc[item, 'Discrimination']
        guessing_g1 = irt_metrics_g1.loc[item, 'Guessing']

        difficulty_g2 = irt_metrics_g2.loc[item, 'Difficulty']
        discrimination_g2 = irt_metrics_g2.loc[item, 'Discrimination']
        guessing_g2 = irt_metrics_g2.loc[item, 'Guessing']
        
        # Calculate differences in parameters
        difficulty_diff = difficulty_g1 - difficulty_g2
        discrimination_diff = discrimination_g1 - discrimination_g2
        guessing_diff = guessing_g1 - guessing_g2

        # Chi-square test
        chi2_val = (difficulty_diff ** 2 + discrimination_diff ** 2 + guessing_diff ** 2)
        p_value = chi2.sf(chi2_val, 3)  # 3 degrees of freedom

        # Collect results
        dif_results.append({
            'Item': item,
            'Difficulty Group 1': difficulty_g1,
            'Difficulty Group 2': difficulty_g2,
            'Discrimination Group 1': discrimination_g1,
            'Discrimination Group 2': discrimination_g2,
            'Guessing Group 1': guessing_g1,
            'Guessing Group 2': guessing_g2,
            'Difficulty Difference': difficulty_diff,
            'Discrimination Difference': discrimination_diff,
            'Guessing Difference': guessing_diff,
            'Chi2 Value': chi2_val,
            'p-value': p_value,
            'DIF Detected': p_value < 0.05
        })

    # Convert results to DataFrame
    dif_df = pd.DataFrame(dif_results)
    
    # Visualize DIF Analysis: ICC for each item
    for item in range(len(correct_answers)):
        col1, col2 = st.columns(2)
        with col1:
            theta = np.linspace(-3, 3, 100)
            
            # Parameters for each group
            a_g1, b_g1, c_g1 = irt_metrics_g1.loc[item, 'Discrimination'], irt_metrics_g1.loc[item, 'Difficulty'], irt_metrics_g1.loc[item, 'Guessing']
            a_g2, b_g2, c_g2 = irt_metrics_g2.loc[item, 'Discrimination'], irt_metrics_g2.loc[item, 'Difficulty'], irt_metrics_g2.loc[item, 'Guessing']

            # Calculate ICC for each group
            prob_g1 = c_g1 + (1 - c_g1) / (1 + np.exp(-a_g1 * (theta - b_g1)))
            prob_g2 = c_g2 + (1 - c_g2) / (1 + np.exp(-a_g2 * (theta - b_g2)))

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(theta, prob_g1, color='blue', label=f'{group1} ICC')
            ax.plot(theta, prob_g2, color='red', linestyle='--', label=f'{group2} ICC')
            ax.set_title(f'Item Characteristic Curve for Item: {item + 1}')
            ax.set_xlabel('Theta')
            ax.set_ylabel('Probability of Correct Response')
            ax.legend()

            st.pyplot(fig)

        # Display DIF Metrics
        with col2:
            st.subheader(f'DIF Metrics for {item + 1}')
            item_metrics = dif_df[dif_df['Item'] == item]
            st.table(item_metrics[['Difficulty Group 1', 'Difficulty Group 2', 'Discrimination Group 1', 
                                   'Discrimination Group 2', 'Guessing Group 1', 'Guessing Group 2', 
                                   'Difficulty Difference', 'Discrimination Difference', 'Guessing Difference', 
                                   'Chi2 Value', 'p-value', 'DIF Detected']])
    
    return dif_df