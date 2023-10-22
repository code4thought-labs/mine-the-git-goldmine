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
