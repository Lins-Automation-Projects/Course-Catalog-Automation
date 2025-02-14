import pandas as pd

def sort_programs_in_csv(input_file, output_file):
    """
    Reads a CSV file, sorts the Program column alphabetically, and saves to a new file.
    
    Parameters:
    input_file (str): Path to the input CSV file
    output_file (str): Path where the sorted CSV will be saved
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Verify 'Program' column exists
        if 'Program' not in df.columns:
            raise ValueError("CSV file does not contain a 'Program' column")
        
        # Sort the dataframe by the Program column
        df_sorted = df.sort_values('Program', ignore_index=True)
        
        # Save the sorted dataframe
        df_sorted.to_csv(output_file, index=False)
        print(f"Successfully sorted programs and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find file {input_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    sort_programs_in_csv("C:/Repos/LinsAutomationProject/Course-Catalog-Automation/New_Work/Work_In_Progress/Final_Programs.csv", "C:/Repos/LinsAutomationProject/Course-Catalog-Automation/New_Work/Work_In_Progress/Final_Programs.csv")