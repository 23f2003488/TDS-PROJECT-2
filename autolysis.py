import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore
import numpy as np
import argparse

# Get the token from the environment variable
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

# Function to read the dataset and show basic info
def load_and_describe_data(filename):
    # Read the CSV file
    df = pd.read_csv(filename, encoding='ISO-8859-1')
    
    # Basic summary of the dataset
    summary_stats = df.describe(include='all').transpose()
    missing_values = df.isnull().sum()
    
    return df, summary_stats, missing_values

# Function to create a correlation heatmap
def plot_correlation_matrix(df, dataset_name):
    # Select only numeric columns for correlation analysis
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return None
    
    # Compute correlation matrix
    corr = numeric_df.corr()

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Correlation Matrix")
    plt.tight_layout()

    # Save as PNG (dynamic file name based on dataset)
    correlation_image_path = f"{dataset_name}/correlation_matrix.png"
    plt.savefig(correlation_image_path)
    plt.close()
    
    return correlation_image_path

# Function to create the narrative
def create_narrative(df, summary_stats, missing_values, correlation_image_path, dataset_name):
    narrative = f"# Data Analysis Report - {dataset_name}\n\n"
    
    # Adding dataset summary
    narrative += f"## Dataset Overview\n"
    narrative += f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns. "
    narrative += f"The columns include:\n\n"
    for column in df.columns:
        narrative += f"- *{column}*: {df[column].dtype}\n"
    
    narrative += f"\n## Summary Statistics\n"
    narrative += summary_stats.to_markdown()
    
    # Adding missing values analysis
    narrative += f"\n## Missing Values\n"
    narrative += missing_values.to_markdown()
    
    # Correlation insights
    if correlation_image_path:
        narrative += f"\n## Correlation Matrix\n"
        narrative += f"The correlation matrix of the dataset is visualized below:\n"
        narrative += f"![Correlation Matrix]({correlation_image_path})\n"
    
    # Outliers detection
    outliers = detect_outliers(df)
    if outliers is not None:
        narrative += f"\n## Outliers\n"
        narrative += f"The number of outliers detected in the dataset (Z-score > 3) per column is as follows:\n"
        narrative += outliers.to_markdown()
    
    return narrative

# Function to detect outliers using Z-score
def detect_outliers(df):
    # Select only numeric columns for outlier detection
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return None
    
    # Apply z-score method to detect outliers
    df_zscore = numeric_df.apply(zscore, axis=0)
    outliers = (df_zscore > 3).sum(axis=0)
    
    return outliers

# Main function that drives the entire analysis and storytelling process
def run_analysis(filename):
    # Extract the dataset name from the filename (without the extension)
    dataset_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Create a directory for the dataset (if it doesn't already exist)
    os.makedirs(dataset_name, exist_ok=True)
    
    # Load the dataset and get basic info
    df, summary_stats, missing_values = load_and_describe_data(filename)
    
    # Create visualizations
    correlation_image_path = plot_correlation_matrix(df, dataset_name)
    
    # Generate the narrative
    narrative = create_narrative(df, summary_stats, missing_values, correlation_image_path, dataset_name)
    
    # Print the final narrative
    print(narrative)

    # Write the narrative to a README.md file in the respective dataset folder
    with open(f"{dataset_name}/README.md", "w") as f:
        f.write(narrative)

# Main execution
if __name__ == "__main__":
    # Set up argument parser to accept filename as an argument
    parser = argparse.ArgumentParser(description="Run data analysis on the specified dataset.")
    parser.add_argument("filename", type=str, help="The path to the dataset CSV file")
    args = parser.parse_args()

    # Run the analysis with the provided dataset filename
    run_analysis(args.filename)
