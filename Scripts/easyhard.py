# This script differentiates between the "easy" and "hard" programs and creates a nice list of them
# Easy basically means our scripts are able to run them "easily" without any manual intervention
# Hard means that we need to manually check them before running our scripts

import pandas as pd

def categorize_files(input_file):
    # Read the input CSV file
    df = pd.read_excel(input_file)
    
    # Check if 'Group_CategoryTitle' or 'SeriesHeading' is empty
    easy_df = df[df[['Group_CategoryTitle', 'SeriesHeading']].isnull().all(axis=1)][['ProgramName', 'Degree']]
    hard_df = df[~df[['Group_CategoryTitle', 'SeriesHeading']].isnull().all(axis=1)][['ProgramName', 'Degree']]
    
    # Remove duplicates, keeping the first occurrence based on ProgramName
    easy_df = easy_df.drop_duplicates(subset=['ProgramName'], keep='first')
    hard_df = hard_df.drop_duplicates(subset=['ProgramName'], keep='first')
    
    # Save to CSV files
    easy_df.to_csv('easy.csv', index=False)
    hard_df.to_csv('hard.csv', index=False)

# Example usage
input_file = 'Data/2024-25_Academic_Program_Catalog_with_Courses_with_pre-req,_co-req_diverse_cultures_10-1-24.xlsx'  # Replace with the actual input file path
categorize_files(input_file)