import pandas as pd

def add_technology_column(df: pd.DataFrame) -> pd.DataFrame:
    # Define a function to map file extensions to technologies
    def map_extension_to_technology(file: str):
        extension = file.split('.')[-1] if '.' in file else None
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