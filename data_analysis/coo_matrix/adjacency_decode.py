import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from helper import *
from caen_digitizer import *


# Function to generate the heatmap matrix for a given run number
def generate_heatmap(runNo, fileDir='/home/tianyi/Downloads/bl4s/DATA'):
    # Load data
    data = digitizer(f'{fileDir}/run{runNo:06}.root', events=range(500), channels=[i for i in range(17, 27)], signal_filter='converted')

    # Active channels (6 channels)
    active_channels = data.waveforms["wave"][:, 0:6]
    
    # Signal max and min
    signal_max = active_channels.max(axis=2)
    signal_min = active_channels.min(axis=2)

    # Event mask
    mask_event = (signal_min > -15) & (signal_max > 8)
    
    # Sensor trigger distribution
    sensor_trigger_distribution = np.sum(mask_event, axis=1)
    
    # Dual trigger mask
    dual_trigger_mask = sensor_trigger_distribution == 2
    rows, cols = np.where(mask_event[dual_trigger_mask])
    pairs = cols.reshape(mask_event[dual_trigger_mask].shape[0], 2)
    
    # Build co-occurrence matrix
    coo_matrix = np.zeros((6,6), dtype=int)
    for pair in pairs:
        i, j = pair
        coo_matrix[i, j] += 1
    
    return coo_matrix


# Specify the range of run numbers to include
runNos = range(1, 18)  # Example range of run numbers

# Number of rows and columns for the subplot grid
n_rows = 3
n_cols = 6

# Create a figure with multiple subplots
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 10))
axes = axes.flatten()  # Flatten to make indexing easier

# Mask for upper triangle
mask = ~np.triu(np.ones((6, 6), dtype=bool), k=1)

# Initialize lists to store the co-occurrence matrices
coo_matrices = []

# Loop over the specified run numbers and generate the heatmap data
for runNo in runNos:
    coo_matrix = generate_heatmap(runNo)
    coo_matrices.append(coo_matrix)

# Find the global min and max values across all matrices
global_min = min([coo_matrix.min() for coo_matrix in coo_matrices])
global_max = max([coo_matrix.max() for coo_matrix in coo_matrices])

# Loop again to plot each heatmap with the shared color scale
for idx, runNo in enumerate(runNos):
    if idx >= len(axes):  # Stop if we run out of subplot axes
        break
    
    # Plot the heatmap with shared vmin and vmax
    sns.heatmap(coo_matrices[idx], ax=axes[idx], linewidth=0.5, cbar=False, mask=mask, vmin=global_min, vmax=global_max)
    axes[idx].set_title(f"Run {runNo}")

# Add a colorbar to the figure (with a common color scale)
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # Adjust the position and size
sns.heatmap(coo_matrices[0], linewidth=0.5, ax=axes[0], cbar_ax=cbar_ax, cbar_kws={'label': 'Co-occurrence Count'}, vmin=global_min, vmax=global_max, mask=mask)

# Adjust layout and save the plot
plt.tight_layout(rect=[0, 0, 0.9, 1])  # Leave space on the right for the colorbar
plt.savefig("multi_run_heatmaps.png")
plt.show()
