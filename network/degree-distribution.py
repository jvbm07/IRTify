import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

# Load your dataset
df = pd.read_csv('/home/user/IRTify/network/2024-11-24T23-18_export.csv')


# Initialize a graph
G = nx.Graph()

# Add edges from the DataFrame
for _, row in df.iterrows():
    student_id = row['student_id']
    for question_id in row.index[1:]:  # Skip 'student_id' column
        if row[question_id] == 1:
            G.add_edge(student_id, question_id)

# Calculate the degree of each node
degrees = [degree for _, degree in G.degree()]

# Calculate frequency of each degree
degree_counts = Counter(degrees)
x = list(degree_counts.keys())  # Degree values
y = list(degree_counts.values())  # Frequencies

# Create scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='blue', edgecolor='black', alpha=0.75)
plt.title('Degree Distribution (Scatter Plot)')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.grid(alpha=0.5, linestyle='--')

# Save the scatter plot as an image
plt.savefig('degree_distribution_scatter.png', dpi=300, bbox_inches='tight')  # Save with high resolution

# Optional: Close the plot to free up memory
plt.close()