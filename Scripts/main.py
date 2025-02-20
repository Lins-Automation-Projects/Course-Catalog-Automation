# Description: This script will read the Academic Catalog file and create separate CSV files for each program and degree.

import pandas as pd
import os

# Load the CSV file
# path will differ per file system
df = pd.read_csv("C:/Users/Snagg/Downloads/AcademicCatalog.csv")

# Ensure that the path is correct to reflect the file system:
# ***/New_Work/Seperate_Programs_and_degress-CSV_Files
output_dir = "C:\Repos\LinsAutomationProject\Course-Catalog-Automation\SeperateProgramsCSVFiles"
os.makedirs(output_dir, exist_ok=True)

# Group by 'ProgramName' and 'Degree' and save each group as a separate CSV
for (program, degree), group in df.groupby(["ProgramName", "Degree"]):
    filename = f"{output_dir}/{program.replace('/', '_').replace(' ', '_')}_{degree.replace('/', '_').replace(' ', '_')}.csv"
    group.to_csv(filename, index=False)
    print(f"Saved: {filename}")
