import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    if len(sys.argv) != 9:
        print("Usage: python LowvsHighGUI.py <input_folder> <output_folder> <diffusion_bins> <diffusion_range_min> <diffusion_range_max> <size_bins> <size_range_min> <size_range_max>")
        return

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    diffusion_bins = int(sys.argv[3])
    diffusion_range_min = float(sys.argv[4])
    diffusion_range_max = float(sys.argv[5])
    size_bins = int(sys.argv[6])
    size_range_min = float(sys.argv[7])
    size_range_max = float(sys.argv[8])

    file_paths = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith("diffusion_coefficients.csv")]

    data_frames = [pd.read_csv(file) for file in file_paths]

    average_cluster_sizes = []
    diffusion_coefficients = []
    alpha_values = []
    labels = []
    cell_counts = {'TAF2 High Expression': 0, 'TAF2 Low Expression ohne Warten': 0, 'TAF5 Low Expression ohne Warten': 0}
    cluster_counts = {'TAF2 High Expression': 0, 'TAF2 Low Expression ohne Warten': 0, 'TAF5 Low Expression ohne Warten': 0}

    for i, data in enumerate(data_frames):
        avg_cluster_size = data.iloc[:, 1].values
        diff_coeff = data['Diffusion Coefficient'].values
        alpha_val = data['Alpha'].values
        average_cluster_sizes.extend(avg_cluster_size)
        diffusion_coefficients.extend(diff_coeff)
        alpha_values.extend(alpha_val)
        
        # Assign conditions and count cells and clusters
        if i <= 4:
            condition = 'TAF2 High Expression'
        elif 5 <= i <= 10:
            condition = 'TAF2 Low Expression ohne Warten'
        else:
            condition = 'TAF5 Low Expression ohne Warten'
        
        labels.extend([condition] * len(avg_cluster_size))
        cell_counts[condition] += 1
        cluster_counts[condition] += len(avg_cluster_size)

    # Convert to DataFrame for analysis
    df = pd.DataFrame({
        'Average Cluster Size': average_cluster_sizes,
        'Diffusion Coefficient': diffusion_coefficients,
        'Alpha': alpha_values,
        'Condition': labels
    })

    # Check for NaN values and handle them
    print("Checking for NaN values...")
    print(df.isna().sum())

    # Drop NaN values
    df.dropna(inplace=True)

    # Define the palette
    palette = {
        'TAF2 High Expression': 'green',
        'TAF2 Low Expression ohne Warten': 'red',
        'TAF5 Low Expression ohne Warten': 'purple'
    }

    # Plot histograms of Diffusion Coefficient for each condition
    plt.figure(figsize=(14, 8))

    conditions = df['Condition'].unique()
    for i, condition in enumerate(conditions, 1):
        plt.subplot(2, 2, i)
        sns.histplot(df[df['Condition'] == condition]['Diffusion Coefficient'], kde=True, color=palette[condition], bins=diffusion_bins)
        plt.title(f'Diffusion Coefficient Distribution\n{condition}', fontsize=16)
        plt.xlabel('Diffusion Coefficient / \u03bcm²/s', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.xlim(diffusion_range_min, diffusion_range_max)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.annotate(f'Cells: {cell_counts[condition]}\nClusters: {cluster_counts[condition]}', 
                    xy=(0.7, 0.85), xycoords='axes fraction', fontsize=12, bbox=dict(boxstyle="round", fc="w"))

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "DiffusionCoefficient_Histograms.png"))
    plt.show()

    # Plot histograms of Average Cluster Size for each condition
    plt.figure(figsize=(14, 8))

    for i, condition in enumerate(conditions, 1):
        plt.subplot(2, 2, i)
        sns.histplot(df[df['Condition'] == condition]['Average Cluster Size'], kde=True, color=palette[condition], bins=size_bins)
        plt.title(f'Average Cluster Size Distribution\n{condition}', fontsize=16)
        plt.xlabel('Average Cluster Size / \u03bcm²', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.xlim(size_range_min, size_range_max)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.annotate(f'Cells: {cell_counts[condition]}\nClusters: {cluster_counts[condition]}', 
                    xy=(0.7, 0.85), xycoords='axes fraction', fontsize=12, bbox=dict(boxstyle="round", fc="w"))

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "ClusterSize_Histograms.png"))
    plt.show()

    # Scatter plot for Diffusion Coefficients vs. Average Cluster Size
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='Average Cluster Size', y='Diffusion Coefficient', hue='Condition', palette=palette, s=100)
    plt.title('Diffusion Coefficients vs. Average Cluster Size', fontsize=20)
    plt.xlabel('Average Cluster Size / \u03bcm²', fontsize=20)
    plt.ylabel('Diffusion Coefficient / \u03bcm²/s', fontsize=20)
    plt.xlim(size_range_min, size_range_max)
    plt.ylim(diffusion_range_min, diffusion_range_max)
    handles, _ = plt.gca().get_legend_handles_labels()
    plt.legend(handles=handles, labels=[f'{condition} (N = {cell_counts[condition]} Cells, {cluster_counts[condition]} Clusters)' for condition in conditions], title='Condition', fontsize=12, title_fontsize=14)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "Scatterplot_Diffusion_vs_ClusterSize.png"))
    plt.show()

if __name__ == "__main__":
    main()
