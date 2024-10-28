import numpy as np
import pandas as pd

def sigmoid(x, a, b, c):
    """Sigmoid function for estimating the item characteristic curve."""
    return c + (1 - c) / (1 + np.exp(-a * (x - b)))

def calculate_difficulty(correct_answers, responses):
    """Calculates the difficulty parameter for each item as the percentage of correct responses."""
    difficulties = []
    for i in range(len(correct_answers)):
        correct_count = sum(1 for response in responses if response[i] == correct_answers[i])
        difficulty = correct_count / len(responses)
        difficulties.append(difficulty)
    return difficulties

def calculate_discrimination(responses, correct_answers):
    """Estimates discrimination for each item based on item-total correlation."""
    scores = [sum(1 for i in range(len(correct_answers)) if resp[i] == correct_answers[i]) for resp in responses]
    total_scores = np.array(scores)
    discriminations = []
    for i in range(len(correct_answers)):
        item_scores = np.array([resp[i] == correct_answers[i] for resp in responses], dtype=int)
        corr = np.corrcoef(item_scores, total_scores)[0, 1]
        discriminations.append(corr if not np.isnan(corr) else 0)
    return discriminations

def calculate_guessing(correct_answers, responses):
    """Estimate guessing parameter dynamically based on unique answer choices."""
    guessing_params = []
    for i in range(len(correct_answers)):
        unique_options = set(response[i] for response in responses)
        guessing_param = 1 / len(unique_options)
        guessing_params.append(guessing_param)
    return guessing_params

def calculate_irt_metrics(correct_answers, responses):
    """Generates a DataFrame of IRT metrics for each item."""
    difficulty = calculate_difficulty(correct_answers, responses)
    discrimination = calculate_discrimination(responses, correct_answers)
    guessing = calculate_guessing(correct_answers, responses)

    # Create a DataFrame with each metric as a column
    irt_metrics_df = pd.DataFrame({
        "Item": range(1, len(correct_answers) + 1),
        "Difficulty": difficulty,
        "Discrimination": discrimination,
        "Guessing": guessing
    })
    
    return irt_metrics_df

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Assuming calculate_irt_metrics is defined elsewhere
def create_irt_report(df):
    # Assuming the first row contains the correct answers
    correct_answers = df.iloc[0].tolist()
    students_answers_df = df.iloc[1:].reset_index(drop=True)
    irt_metrics_df = calculate_irt_metrics(correct_answers, students_answers_df.values.tolist())

    # Convert to a list for report
    report = []

    # Generate an ICC plot for each question based on IRT metrics
    for idx, row in irt_metrics_df.iterrows():
        col1, col2 = st.columns(2)
        item_name = f'Item {row["Item"]}'

        # Plot the ICC (Item Characteristic Curve) in the left column
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Generate a range of theta values (latent trait levels)
            theta = np.linspace(-3, 3, 100)
            a = row['Discrimination']
            b = row['Difficulty']
            c = row['Guessing']

            # Calculate probabilities using the IRT 3PL model
            probabilities = c + (1 - c) / (1 + np.exp(-a * (theta - b)))

            ax.plot(theta, probabilities, color='blue', label=f'{item_name} ICC')
            ax.set_title(f'Item Characteristic Curve: {item_name}')
            ax.set_xlabel('Theta')
            ax.set_ylabel('Probability of Correct Response')
            ax.legend()

            st.pyplot(fig)

        # Display the IRT metrics in the right column
        with col2:
            st.subheader(f'IRT Metrics for {item_name}')
            st.table(pd.DataFrame({
                'Metric': ['Difficulty', 'Discrimination', 'Guessing'],
                'Value': [b, a, c]
            }))

    return report
