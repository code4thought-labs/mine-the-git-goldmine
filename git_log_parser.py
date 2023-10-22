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