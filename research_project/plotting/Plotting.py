import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('data/montreal_betweenness.csv') 

# Define bins for sum_of_errors
bins = 20  # Number of bins
data['sum_of_errors_bin'] = pd.cut(data['sum_of_errors'], bins=bins)

# Group by bins and calculate mean values
#grouped_data = data.groupby('sum_of_errors_bin').agg({
    #'continuous_disconnected_points': 'mean',
    #'bikengrowth_disconnected_points': 'mean'
#}).reset_index()

# Calculate the bin centers
#bin_centers = grouped_data['sum_of_errors_bin'].apply(lambda x: x.mid)

# Plot the distribution
plt.figure(figsize=(12, 6))

# Plot histogram
data['sum_of_errors'].plot(kind='hist', bins=bins, color='lightblue', edgecolor='black', alpha=0.7, label='Distribution of sum_of_errors')

# Overlay mean lines
#plt.plot(bin_centers, grouped_data['continuous_disconnected_points'], color='red', label='Mean of continuous_disconnected_points', linewidth=2)
#plt.plot(bin_centers, grouped_data['bikengrowth_disconnected_points'], color='green', label='Mean of bikengrowth_disconnected_points', linewidth=2)

# Adding labels, title, and legend
plt.xlabel('Sum of Errors')
plt.ylabel('Frequency')
plt.title('Distribution of sum_of_errors')
plt.legend()

plt.tight_layout()
plt.show()
