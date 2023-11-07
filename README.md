# Open-conf Mine the Git Goldmine Workshop
by Alex Zacharopoulos and Artemis Kouniakis

## Step 0: Clone this repository and change working directory
```sh
git clone https://github.com/code4thought-labs/mine-the-git-goldmine.git

cd mine-the-git-goldmine/
```

You can find the complete source code in the `complete` tag.
```bash
git checkout complete
```

Otherwise, you can stay in the `empty` tag
```bash
git checkout empty
```


## Step 1: Setup your environment

### Make sure you install Python and relevant libs
```bash
python --version
pip --version
pip install pandas matplot
```

### Clone mastodon repo to be used as a use case
```bash
git clone https://github.com/mastodon/mastodon.git
```

## Step 2: Extract git history file for mastodon
Change directory to mastodon and run your `git log` command. 
You want to redirect it to a file for easier analysis, finally move the log history in our main folder.

```bash
cd mastodon

git log --pretty=format:'BEGIN_COMMIT%nHash|%H%nAuthor|%ae%nDate|%ad%nMessage|%s' --date=format:'%d-%m-%Y %H:%M:%S' --numstat --no-renames > mastodon_git_history.log

mv mastodon_git_history.log ../

cd ..
```

This `git log` is a good start for collecting comprehensive data on the repository. 
It captures several important fields including:

- **Commit hash**: Using `%H` for the full hash.
- **Author Name**: Using `%an`.
- **Commit Date**: Using `%ad` in a specific date format.
- **Commit Message**: Using `%s`.

Additionally, the flags `--numstat` and `--summary` will give you information about the files changed and how many lines were added or deleted, as well as provide a summary of the changes.

## Step 3: Parse the git history in a dataframe

We will use Python's Pandas library to read the text file and convert it into a *DataFrame*. 
The Python code snippet below accomplishes this task:

```python
import pandas as pd

def parse_git_log_to_dataframe(file_path):
    data = []
    commit_data = {}
    changed_files = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line == "BEGIN_COMMIT":
                # If not empty, append the last commit's data to the list
                if commit_data:
                    for changed_file in changed_files:
                        new_commit_data = commit_data.copy()
                        new_commit_data.update(changed_file)
                        data.append(new_commit_data)
                    changed_files = []
                commit_data = {}  # Reset for the next commit
                continue
                
            # Skip lines that don't contain a pipe character
            if "|" not in line:
                # Possibly a file change line, should contain tab characters
                if '\t' in line:
                    added, deleted, file = line.split('\t')
                    changed_files.append({
                        "Added": added, 
                        "Deleted": deleted, 
                        "File": file
                    })
                continue
                
            # Parse each line based on the delimiters you used
            key, value = line.split("|", 1)
            commit_data[key] = value
    
    # If the file ends without a BEGIN_COMMIT line, add the last commit
    if commit_data:
        for changed_file in changed_files:
            new_commit_data = commit_data.copy()
            new_commit_data.update(changed_file)
            data.append(new_commit_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert 'Date', 'Added' and 'Deleted' columns to appropriate types
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M:%S')
    df['Added'] = pd.to_numeric(df['Added'], errors='coerce')
    df['Deleted'] = pd.to_numeric(df['Added'], errors='coerce')
    
    return df
```

We add the following code in your project root, in a file named `git_log_parser.py`.

Then we create a main program named `git_goldmine.py` where we add the execution code:
```python
import sys

from git_log_parser import *

if __name__ == "__main__":
    # Read path to the git log file as an argument
    file_path = sys.argv[1]

    # Parse the git log file into a DataFrame
    df = parse_git_log_to_dataframe(file_path)

    print(df)
```

and execute it by running:
```bash
python git_goldmine.py mastodon_git_history.log
```

Here's what the code does:

1. It reads the `mastodon_git_history.log` file line-by-line.
2. When it encounters a line saying `BEGIN_COMMIT`, it knows a new commit data block is starting.
3. It then proceeds to parse each line of the commit data block, filling in a dictionary (`commit_data`) with key-value pairs (Hash, Author, etc.).
4. Once a commit data block is done, it appends the filled dictionary to a list (`data`).
5. Finally, it creates a Pandas DataFrame from the list of dictionaries.

## Step 4: Scoping and data cleaning
In order to make our log information more useful we can add more dimensions, derived from the existing collected data, as well as to perform some data cleaning in order to remove our data noise. 

Create a new `scoping.py` file that will be used for this job.

First, we want to add a **Technology** dimension in our Dataframe. To do that we can map the *file extensions* to *technologies*:
```python
import pandas as pd

def add_technology_column(df: pd.DataFrame) -> pd.DataFrame:
    # Define a function to map file extensions to technologies
    def map_extension_to_technology(file: str):
        extension = file.split('.')[
            -1] if '.' in file else None
        mapping = {
            'rb': 'Ruby',
            'html': 'HTML',
            'haml': 'HTML',
            'erb': 'Embedded Ruby',
            'js': 'Javascript',
            'jsx': 'Javascript',
            'ts': 'Typescript',
            'tsx': 'Typescript',
            'scss': 'Saas'
        }
        return mapping.get(extension, 'Other')

    # Create the new 'Technology' column
    df['Technology'] = df['File'].apply(map_extension_to_technology)

    return df
```

In this code, the function add_technology_column takes an existing DataFrame df as its argument. It then defines another function map_extension_to_technology that takes a file name as input and returns the appropriate technology based on the file extension.

The function uses the apply method to create a new 'Technology' column in the DataFrame, filling it with values based on the 'File' column's extensions. Finally, it returns the updated DataFrame.

Second, we want to add another column **Component** maps the components to the following values based on the *path of the file*:
- app/controllersCode = controllers
- app/helpersCode = helpers
- app/libCode = lib
- app/modelsRepresentation = models
- app/policiesPermission = policies
- app/serializersCode = serializers
- app/servicesComplex = services
- app/viewsTemplates = views
- app/workersCode = workers
- app/javascript/mastodonCode = frontend 
- app/javascript/packsCode = non-react frontend 
- app/javascript/stylesCode = styles

```python
def add_component_column(df: pd.DataFrame) -> pd.DataFrame:
    # Define a function to map file paths to components
    def map_path_to_component(file_path: str):
        mapping = {
            'app/controllers': 'controllers',
            'app/helpers': 'helpers',
            'app/lib': 'lib',
            'app/models': 'models',
            'app/policies': 'policies',
            'app/serializers': 'serializers',
            'app/services': 'services',
            'app/views': 'views',
            'app/workers': 'workers',
            'app/javascript/mastodon': 'frontend',
            'app/javascript/packs': 'non-react frontend',
            'app/javascript/styles': 'styles'
        }
        for path, component in mapping.items():
            if path in file_path:
                return component
        return 'Other'
    
    # Create the new 'component' column
    df['Component'] = df['File'].apply(map_path_to_component)
    
    return df
```

In this code, the add_component_column function takes an existing DataFrame df and adds a new column 'component'. The map_path_to_component function is used to map the file path to its respective component based on the path's prefix. The apply method is then used to populate the new 'component' column using this mapping function.
After calling this function, your DataFrame df should have a new column that categorizes the components based on the file paths.

Third, there is a lot of noise in our dataset, such as commits from *bot* accounts, files that do not belong to code (marked as *Other* e.g. *json* files) and files that do not belong to any component (*Other* component).
Finally, it filters our commits where the messages are about changes for conforming to code styling standards.

> ! Important: The success of this step depends on the specific repository and its associated data. Generally, this phase requires significant investigative effort from the individual conducting the analysis.

```python
def clean_log(df: pd.DataFrame) -> pd.DataFrame:
    # Filter out the rows that have the value 'Other' in the 'Technology' and 'Component' columns
    df = df[df['Technology'] != 'Other']
    df = df[df['Component'] != 'Other']

    # Filter our rows where authors have the name bot or bots
    df = df[~df['Author'].str.contains('bot', case=False)]

    # Filter out rows with messages about style changes
    df = df[~df['Message'].str.contains('ESLint', case=False)]
    df = df[~df['Message'].str.contains('Enforce stricter rules', case=False)]
    
    return df
```

Finally, all this code needs to be integrated to our main code `git_goldmine.py`:
```python
import sys

from git_log_parser import *
from scoping import *

if __name__ == "__main__":
    # Read path to the git log file as an argument
    if len(sys.argv) < 2:
        print("Please provide a path to the git log file.")
        sys.exit(1)
    file_path = sys.argv[1]

    # Parse the git log file into a DataFrame
    df = parse_git_log_to_dataframe(file_path)
    
    # Add the new columns
    df = add_technology_column(df)
    df = add_component_column(df)

    # Clean the DataFrame
    df = clean_log(df)

    # Show the DataFrame with the new columns
    print(df)
```

Run it using:
```bash
python git_goldmine.py mastodon_git_history.log
```

## Step 5: Basic commit data interpretation
After extracting, parsing transforming and cleaning our data, it is time to start making some sense of it.
We will start with some basic demographics, so let's create a new `demographics.py` file.
Here, besides **pandas** we need to import also **matplot** in order to visualize our results.


### Number of commits per month
First, let's visualize the most simple demographic, this function takes our DataFrame df and aims to plot the number of commits per month:
```python
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
```

Some insights that one can get for such a graph is:
1. *Activity Level & Trends*: The graph shows the overall activity level of the project and helps identify increasing or decreasing trends over time.
2. *Project Milestones & Seasonality*: Spikes or dips in commits may correspond to project milestones, deadlines, or even seasonal patterns in work activity.
3. *Impact of Organizational Changes*: Significant changes in commit patterns could reflect the impact of organizational events, like team restructuring or the introduction of new workflows.
4. *Resource Planning*: A consistent increase in commits may indicate the need for additional resources or staff, while a decline may suggest overcapacity.
5. *Health Indicators*: In open-source projects, a stable or increasing number of commits can be viewed as a sign of a healthy and active developer community.


### Lines added per technology per quarter
Next, to understand the system's evolution better let's get more into the *type* of coded that has been added.

The second demographics graph function takes a DataFrame df as an argument and produces a stacked bar chart to visualize the number of lines of code added per quarter, grouped by technology.

```python
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
```

Some insights that one can get for such a graph is:
1. *Technology Focus:* Identify which technologies are receiving the most development effort in terms of lines of code added. This can help in resource allocation and strategic planning.
2. *Codebase Growth*: The plot shows how fast the codebase is growing in each technology. Rapid growth may necessitate additional resources or signify complexity that needs to be managed.
3. *Balance*: If there are imbalances in the distribution of lines of code across technologies, it may indicate over-reliance on certain technologies or neglect of others, requiring reevaluation.
4. *Impact of Initiatives*: If the organization has undertaken specific initiatives to boost development in certain technologies, the effectiveness of those initiatives can be gauged by looking at changes in lines of code added over time.

### Lines added per component per quarter
Finally, the following function takes a DataFrame as an argument and generates a stacked bar chart that visualizes the total lines of code added per quarter for each component in a software system.

```python
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
```

To compose the code above, add the following to `git_goldmine.py` and run `python git_goldmine.py mastodon_git_history.log`.
```python
import sys

from git_log_parser import *
from scoping import *
from demographics import *

if __name__ == "__main__":
    # Read path to the git log file as an argument
    if len(sys.argv) < 2:
        print("Please provide a path to the git log file.")
        sys.exit(1)
    file_path = sys.argv[1]

    # Parse the git log file into a DataFrame
    df = parse_git_log_to_dataframe(file_path)
    
    # Add the new columns
    df = add_technology_column(df)
    df = add_component_column(df)

    # Clean the DataFrame
    df = clean_log(df)

    # Show the DataFrame with the new columns
    print(df)

    # Demographics
    ## Plot the commit trend
    plot_commit_trend(df)

    ## Plot the lines added per quarter per technology
    plot_lines_added_per_quarter_per_tech(df)

    ## Plot the lines added per quarter per component
    plot_lines_added_per_quarter_per_component(df)
```

## Step 6: Code quality and team dynamics analysis
In the final chapter, we delve into nuanced insights that not only enhance our understanding of our codebase but also shed light on team dynamics. By doing so, we aim to elevate the overall efficiency and effectiveness of a software development team.

### Most changed files
First, we create a function `plot_most_changed_files` that takes a DataFrame (df) and an optional parameter (top_n, defaulting to 50). It creates a bar chart that displays the top N files with the most changes. Specifically, the function counts the number of changes for each file, sorts them in descending order, and then plots the top N. The x-axis represents the files, and the y-axis shows the number of changes.

```python
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
``` 

**Hotspot Analysis:** Prioritize Technical Debt Where It Matters Most.
Technical debt is often distributed unevenly across a codebase. Some files are relatively stable and problem-free, while others seem to be in a constant state of flux, attracting more bugs and requiring frequent changes. These frequently-changed files can quickly become "hotspots" of technical debt. 

The `plot_most_changed_files` function provides a targeted approach to identifying these hotspots. It gives you the power to prioritize efforts 
on the most volatile parts of your codebase, making your technical debt strategy more effective and efficient.
This tool empowers you to make informed decisions, enabling you to steer your teams toward high-value tasks that bring immediate benefits in quality, stability, and maintainability.

### Heatmap of Changed components

Visualizing the changed components in a treemap, creates a heatmap for changed files.
This visual is much better at identifying the "hot areas" where changes occur, and where not.

For making treemap, we use the `squarify` library.
To install it run: `pip install squarify`.

```python
import squarify
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
```

### Number of unique authors changed a file

The `plot_authors_per_file` function serves to identify and visualize the top N files that have been modified by the most (or least) number of unique authors in a codebase.

```python
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
```

#### Communication Overhead: Top files with MOST changes from unique authors.

This provides critical insights into communication overhead and potential areas of risk, specifically through its ability to identify "hotspot" files that are frequently modified by multiple unique authors.

- **Pinpointing Collaboration Bottlenecks:** The function identifies files that have many contributors, serving as an early warning sign of a communication bottleneck. These files may require additional synchronization and alignment meetings, increasing overhead.
- **Clarifying Ownership:** When multiple authors contribute to a file, it becomes harder to establish clear ownership. Understanding these hotspots allows you to assign dedicated owners or teams to certain files or modules, streamlining the development process and reducing communication complexities.
- **Risk Mitigation:** Files modified by multiple authors become hotspots that are more prone to errors and inconsistencies. Knowing this, you can proactively focus on these files for code reviews or potential refactoring, reducing the risk of future issues.
- **Focused Communication:** By identifying these hotspots, you can direct more focused communication towards resolving the ambiguity and complexities surrounding these files, potentially through focused discussions or targeted documentation.
- **Resource Allocation:** Understanding where the majority of team communication and alignment needs to happen allows you to allocate managerial resources more effectively, whether it’s through code ownership guidelines, additional training, or more rigorous code review processes.

By leveraging the insights from this function, one can proactively tackle communication overhead, thereby optimizing team efficiency, reducing risks, and ultimately delivering a more robust and maintainable product.

#### Knowledge Bottleneck: Top files with LEAST changes from unique authors

The plot_authors_per_file function can also be tailored to highlight files changed solely by a single author, thereby identifying potential "knowledge bottlenecks."

- **Single Point of Failure:** Files with only a single contributor can become problematic if that individual leaves the team or is unavailable. By identifying these files, you can preemptively mitigate the risks associated with a single point of failure.

- **Knowledge Distribution:** Recognizing files that are primarily owned by a single contributor enables you to facilitate knowledge sharing. This can be achieved through pair programming, code reviews, or specific knowledge transfer sessions.

- **Succession Planning:** Knowing who the sole contributors to files are helps in effective succession planning. You can train other team members on these critical parts of the codebase in advance, making for a smoother transition should the primary contributor leave or shift roles.

- **Reduced Onboarding Time:** If knowledge is not limited to one person, new team members can be onboarded more efficiently, as they won't have to rely solely on a single person for information. This can speed up the onboarding process and reduce its impact on productivity.

- **Strategic Resource Allocation:** By understanding where knowledge is concentrated in one individual, you can strategically allocate resources for cross-training, documentation, or even system refactoring to make the code more intuitive for others.

Identifying both hotspots for communication overhead and potential bottlenecks for concentrated knowledge allows for more balanced and resilient team operations. Addressing these issues proactively can save both time and resources in the long term, enabling your team to be more agile, adaptable, and effective.

### Heatmap of Changed files per number of Authors in Component level

Visualizing the changed files in component level by the number of auther who touched them in a treemap, creates a heatmap of knowledge distribution in the sysystem.
This visual is much better at identifying the "hot areas" of knoweldge bottlenecks or communication overhead.

```python
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
```

Finally, the compete code of `git_goldmine.py` looks like this:
```python
import sys

from git_log_parser import *
from scoping import *
from demographics import *
from dynamics import *

if __name__ == "__main__":
    # Read path to the git log file as an argument
    if len(sys.argv) < 2:
        print("Please provide a path to the git log file.")
        sys.exit(1)
    file_path = sys.argv[1]

    # Parse the git log file into a DataFrame
    df = parse_git_log_to_dataframe(file_path)
    
    # Add the new columns
    df = add_technology_column(df)
    df = add_component_column(df)

    # Clean the DataFrame
    df = clean_log(df)

    # Show the DataFrame with the new columns
    print(df)

    # Demographics
    ## Plot the commit trend
    plot_commit_trend(df)

    ## Plot the lines added per quarter per technology
    plot_lines_added_per_quarter_per_tech(df)

    ## Plot the lines added per quarter per component
    plot_lines_added_per_quarter_per_component(df)

    # Dynamics
    ## Plot the most changed files
    plot_most_changed_files(df, 50)

    ## Plot the 10 most authors per file
    plot_authors_per_file(df, False, 10)

    ## Plot the 50 least authors per file
    plot_authors_per_file(df, True, 50)

    ## Plot a heat map of the number of author touched each component
    plot_treemap_by_authors(df)

    ## Plot a heat map of the number of commits occured per component
    plot_treemap_by_commits(df)
```
