import matplotlib.pyplot as plt
import pandas as pd

import squarify

def plot_most_changed_files(df: pd.DataFrame, top_n: int = 100):
    # Count the number of changes for each file
    changes_by_file = df['File'].value_counts()
    
    # Sort and take the top N most changed files
    top_n_changed_files = changes_by_file.sort_values(ascending=False).head(top_n)
    
    # Plotting
    plt.figure(figsize=(10, 5))
    ax = top_n_changed_files.plot(kind='bar')
    
    plt.title(f'Top {top_n} Most Changed Files')
    plt.xlabel('Files')
    plt.ylabel('Number of Changes')
    
    # Rotate x-axis labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    
    plt.show()


def plot_authors_per_file(df: pd.DataFrame, asc: bool = False, top_n: int = 10):
    # Group by 'File' and count unique authors for each file
    unique_authors_by_file = df.groupby('File')['Author'].nunique()
    
    # Sort and take the top N files with most unique authors
    top_n_files_by_authors = unique_authors_by_file.sort_values(ascending=asc).head(top_n)
    
    # Plotting
    plt.figure(figsize=(10, 5))
    ax = top_n_files_by_authors.plot(kind='bar')
    
    most_least: str = 'Least' if asc else 'Most'
    plt.title(f'Top {top_n} Files with {most_least} changes from Unique Authors')
    plt.xlabel('Files')
    plt.ylabel('Number of Unique Authors changed the file')
    
    # Rotate x-axis labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    
    plt.show()


def plot_treemap_by_authors(df: pd.DataFrame):
    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()
    
    # Count the unique authors per component
    unique_authors_per_component = df.groupby('Component')['Author'].nunique()
    
    # Determine color based on number of unique authors (normalize the count)
    max_authors = unique_authors_per_component.max()
    min_authors = unique_authors_per_component.min()
    norm = plt.Normalize(min_authors, max_authors)
    colors = plt.cm.Blues(norm(unique_authors_per_component.values))
    
    # Plotting
    plt.figure(figsize=(14, 7))
    
    squarify.plot(sizes=unique_authors_per_component.values, label=unique_authors_per_component.index, 
                  color=colors, alpha=.8, text_kwargs={'fontsize':10})
    
    plt.title("Number of Unique Authors by Component")
    plt.axis('off')
    
    # Create a custom legend to indicate what the colors mean
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=min_authors, vmax=max_authors))
    sm.set_array([])
    plt.colorbar(sm, orientation='vertical', label='Number of Unique Authors')
    
    plt.show()


def plot_treemap_by_commits(df: pd.DataFrame):
    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()
    
    # Count the commits per component
    commits_per_component = df.groupby('Component')['Hash'].nunique()
    
    # Determine color based on number of commits (normalize the count)
    max_commits = commits_per_component.max()
    min_commits = commits_per_component.min()
    norm = plt.Normalize(min_commits, max_commits)
    colors = plt.cm.Reds(norm(commits_per_component.values))
    
    # Plotting
    plt.figure(figsize=(14, 7))
    
    squarify.plot(sizes=commits_per_component.values, label=commits_per_component.index, 
                  color=colors, alpha=.8, text_kwargs={'fontsize':10})
    
    plt.title("Number of Commits by Component")
    plt.axis('off')
    
    # Create a custom legend to indicate what the colors mean
    sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=min_commits, vmax=max_commits))
    sm.set_array([])
    plt.colorbar(sm, orientation='vertical', label='Number of Commits')
    
    plt.show()
