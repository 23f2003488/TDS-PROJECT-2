# /// script
# dependencies = [
#   "httpx",
#   "pandas",
#   "seaborn",
#   "scipy",
#   "matplotlib",
#   "numpy",
#   "tabulate",
# ]
# ///


import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore
import numpy as np
import argparse


# Get the token from the environment variable
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")


# Function to load data and summarize
def load_and_describe_data(filename):
    """
    Loads the dataset, describes statistics, and returns missing value information.
    Args:
        filename (str): Path to the CSV data file.
    Returns:
        df: Loaded DataFrame.
        summary_stats: Summary statistics of the data.
        missing_values: Missing value counts for each column.
    """
    # Read the CSV file
    df = pd.read_csv(filename, encoding='ISO-8859-1')
    
    # Basic summary statistics
    summary_stats = df.describe(include='all').transpose()
    
    # Calculate missing values
    missing_values = df.isnull().sum()
    
    return df, summary_stats, missing_values


# Function to create the correlation heatmap
def create_correlation_heatmap(df, output_file):
    """
    Creates a correlation heatmap and saves it as a PNG file.
    Args:
        df (pd.DataFrame): Input DataFrame.
        output_file (str): Path to save the heatmap PNG.
    """
    # Only numeric columns are considered for correlation
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        print("No numeric data available to compute correlations.")
        return

    # Compute correlation matrix
    corr = numeric_df.corr()

    # Plotting
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Correlation Matrix")
    plt.tight_layout()

    # Save the heatmap as PNG
    plt.savefig(output_file)
    plt.close()
    print(f"Saved Correlation Heatmap to {output_file}")


# Function to create missing values bar plot
def create_missing_value_barplot(df, output_file):
    """
    Creates and saves a bar plot showing missing values for each column.
    Args:
        df (pd.DataFrame): Input DataFrame.
        output_file (str): Output file path for saving the bar plot.
    """
    # Calculate missing values for each column
    missing_counts = df.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0]  # Filter to show only columns with missing values

    # Create the barplot
    plt.figure(figsize=(12, 6))
    sns.barplot(x=missing_counts.index, y=missing_counts.values, palette="viridis")
    plt.xticks(rotation=45)
    plt.xlabel("Columns")
    plt.ylabel("Number of Missing Values")
    plt.title("Number of Missing Values by Column")
    plt.tight_layout()

    # Save the barplot as PNG
    plt.savefig(output_file)
    plt.close()
    print(f"Saved Missing Values Bar Plot to {output_file}")


# Function to detect outliers using Z-score
def detect_outliers(df):
    """
    Detects outliers based on Z-score.
    Args:
        df (pd.DataFrame): Input DataFrame.
    Returns:
        DataFrame of detected outliers.
    """
    # Select only numeric columns for analysis
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        print("No numeric columns to analyze for outliers.")
        return None

    # Apply Z-score
    df_zscore = numeric_df.apply(zscore, axis=0)
    outliers = (df_zscore > 3).sum(axis=0)

    return outliers


# Create the narrative to save to the README.md
def create_narrative(df, summary_stats, missing_values, correlation_heatmap_path, missing_values_barplot_path, dataset_name):
    """
    Create the markdown narrative for the data analysis report.
    Args:
        df: DataFrame of loaded data.
        summary_stats: Summary statistics from describe.
        missing_values: Missing value counts.
        correlation_heatmap_path: Path to correlation heatmap.
        missing_values_barplot_path: Path to missing values barplot.
        dataset_name: Name of the dataset being analyzed.
    Returns:
        narrative string to save to README.md
    """
    narrative = f"# Data Analysis Report - {dataset_name}\n\n"
    
    # Dataset Overview
    narrative += f"## Dataset Overview\n"
    narrative += f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns. "
    narrative += f"The columns include:\n\n"
    for column in df.columns:
        narrative += f"- *{column}*: {df[column].dtype}\n"

    # Summary Statistics
    narrative += f"\n## Summary Statistics\n"
    narrative += summary_stats.to_markdown()

    # Missing values
    narrative += f"\n## Missing Values\n"
    narrative += missing_values.to_markdown()

    # Correlation heatmap visualization
    if correlation_heatmap_path:
        narrative += f"\n## Correlation Matrix\n"
        narrative += f"The correlation matrix of the dataset is visualized below:\n"
        narrative += f"![Correlation Matrix]({correlation_heatmap_path})\n"

    # Missing values visualization
    if missing_values_barplot_path:
        narrative += f"\n## Missing Values\n"
        narrative += f"A bar plot visualizing the number of missing values by column:\n"
        narrative += f"![Missing Values Bar Plot]({missing_values_barplot_path})\n"

    # Outliers (Z-score)
    outliers = detect_outliers(df)
    if outliers is not None:
        narrative += f"\n## Outliers\n"
        narrative += f"The number of outliers detected in the dataset (Z-score > 3) per column is as follows:\n"
        narrative += outliers.to_markdown()

    return narrative


# Main Analysis Function
def run_analysis(filename):
    """
    Main analysis pipeline: Load data, compute statistics, generate visualizations, and create narrative.
    Args:
        filename (str): Path to the dataset to analyze.
    """
    # Extract dataset name
    dataset_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Create dataset directory
    os.makedirs(dataset_name, exist_ok=True)
    
    # Load data and compute basic information
    df, summary_stats, missing_values = load_and_describe_data(filename)

    # Create visualizations
    correlation_heatmap_path = os.path.join(dataset_name, "correlation_matrix.png")
    missing_values_barplot_path = os.path.join(dataset_name, "missing_values_barplot.png")

    create_correlation_heatmap(df, correlation_heatmap_path)
    create_missing_value_barplot(df, missing_values_barplot_path)

    # Generate narrative
    narrative = create_narrative(
        df, summary_stats, missing_values, correlation_heatmap_path, missing_values_barplot_path, dataset_name
    )
    
    # Write the narrative to a markdown file
    with open(os.path.join(dataset_name, "README.md"), "w") as f:
        f.write(narrative)
    
    print("Analysis and visualizations complete.")


# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run data analysis on a specified dataset.")
    parser.add_argument("filename", type=str, help="Path to dataset CSV file")
    args = parser.parse_args()

    run_analysis(args.filename)


