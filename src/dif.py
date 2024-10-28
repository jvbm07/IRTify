import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2
import streamlit as st
from irt import calculate_irt_metrics

def create_dif_report(df, group_col):
    """
    Perform Differential Item Functioning (DIF) analysis.
    
    Parameters:
    - df: DataFrame with responses, including a 'Group' column for DIF analysis.
    - group_col: Column name in df representing the group (e.g., 'Gender').

    Returns:
    - A DataFrame with DIF analysis results, including IRT parameter differences and significance.
    """
    # Split data by group
    groups = df[group_col].unique()
    if len(groups) != 2:
        raise ValueError("DIF analysis requires exactly two groups for comparison.")
    
    group1, group2 = groups
    group1_data = df[df[group_col] == group1].drop(columns=[group_col]).reset_index(drop=True)
    group2_data = df[df[group_col] == group2].drop(columns=[group_col]).reset_index(drop=True)
    
    # Assuming the first row contains the correct answers
    correct_answers = df.iloc[0].drop(group_col)
    responses_g1 = group1_data.iloc[1:].values.tolist()
    responses_g2 = group2_data.iloc[1:].values.tolist()

    # Calculate IRT parameters for each group
    irt_metrics_g1 = calculate_irt_metrics(responses_g1, correct_answers)
    irt_metrics_g2 = calculate_irt_metrics(responses_g2, correct_answers)

    # Prepare results DataFrame for DIF analysis
    dif_results = []
    
    for item in correct_answers.index:
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

        # Statistical test (chi-squared for simplicity; adjust with a proper likelihood ratio test if needed)
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
    for item in correct_answers.index:
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
            ax.set_title(f'Item Characteristic Curve for Item: {item}')
            ax.set_xlabel('Theta')
            ax.set_ylabel('Probability of Correct Response')
            ax.legend()

            st.pyplot(fig)

        # Display DIF Metrics
        with col2:
            st.subheader(f'DIF Metrics for {item}')
            item_metrics = dif_df[dif_df['Item'] == item]
            st.table(item_metrics[['Difficulty Group 1', 'Difficulty Group 2', 'Discrimination Group 1', 
                                   'Discrimination Group 2', 'Guessing Group 1', 'Guessing Group 2', 
                                   'Difficulty Difference', 'Discrimination Difference', 'Guessing Difference', 
                                   'Chi2 Value', 'p-value', 'DIF Detected']])
    
    return dif_df
