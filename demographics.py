import matplotlib.pyplot as plt
import pandas as pd

def plot_commit_trend(df: pd.DataFrame):
    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()

    # Set 'Date' as index for resampling
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Resample data by month and count commits
    commits_by_month = df.resample('M').count()['Hash']
    
    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(commits_by_month.index, commits_by_month.values, marker='o', linestyle='-')
    
    plt.title('Commits trend')
    plt.xlabel('Month')
    plt.ylabel('Number of Commits')
    
    plt.show()

def plot_lines_added_per_quarter_per_tech(df: pd.DataFrame):
    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()
    
    # Remove rows where 'Added' is NaN
    df = df.dropna(subset=['Added'])
    
    # Set 'Date' as index for resampling
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Resample data by quarter and sum the lines added, grouped by technology
    lines_added_by_quarter_tech = df.groupby([pd.Grouper(freq='Q'), 'Technology'])['Added'].sum().unstack().fillna(0)
    
    # Plotting
    plt.figure(figsize=(14, 7))
    
    # Create the stacked bar chart
    ax = lines_added_by_quarter_tech.plot(kind='bar', stacked=True, figsize=(14,7))
    
    # Get current x-tick labels
    labels = [item.get_text() for item in ax.get_xticklabels()]
    
    # Convert labels to QX/YY format
    new_labels = ['Q{}/{}'.format((pd.to_datetime(label).month - 1)//3 + 1, pd.to_datetime(label).year) for label in labels]
    
    # Set new x-tick labels
    ax.set_xticklabels(new_labels, rotation=90)
    
    plt.title('Lines Added per Quarter per Technology')
    plt.xlabel('Quarter')
    plt.ylabel('Lines Added')
    plt.legend(title='Technology')
    
    plt.show()

def plot_lines_added_per_quarter_per_component(df: pd.DataFrame):
    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()

    # Delete rows where 'Added' is NaN
    df = df.dropna(subset=['Added'])
    
    # Set 'Date' as index for resampling
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Resample data by quarter and sum the lines added, grouped by component
    lines_added_by_quarter_component = df.groupby([pd.Grouper(freq='Q'), 'Component'])['Added'].sum().unstack().fillna(0)
    
    # Plotting
    plt.figure(figsize=(14, 7))
    
    # Create the stacked bar chart
    ax = lines_added_by_quarter_component.plot(kind='bar', stacked=True, figsize=(14,7))
    
    # Get current x-tick labels
    labels = [item.get_text() for item in ax.get_xticklabels()]
    
    # Convert labels to QX/YY format
    new_labels = ['Q{}/{}'.format((pd.to_datetime(label).month - 1)//3 + 1, pd.to_datetime(label).year) for label in labels]
    
    # Set new x-tick labels
    ax.set_xticklabels(new_labels, rotation=90)
    
    plt.title('Lines Added per Quarter per Component')
    plt.xlabel('Quarter')
    plt.ylabel('Lines Added')
    plt.legend(title='Component')
    
    plt.show()
    