# %% [markdown]
# # Maximu (Main Authomation Script)
# 
# This is version 2.0 of the main automation script with some key updates and new capabilities. Changes made are:
# - Description Categorization 
# 
# Script Purpose:
# 
# This script processes the main ISRS dataset to generate an optimized and well-structured dataset that effectively organizes course content.
# 
# Step 1: Load the data

# %%
import pandas as pd

def load_csv_to_dataframe(file_path):
    """
    Loads a CSV file into a Pandas DataFrame.
    
    Parameters:
    file_path (str): The path to the CSV file.
    
    Returns:
    pd.DataFrame: A DataFrame containing the CSV data.
    """
    try:
        df = pd.read_csv(file_path)
        print("CSV file loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

# Ask the user to input the file path
file_path = input("Enter the full file path of the CSV file: ")
main_record = load_csv_to_dataframe(file_path)

# %% [markdown]
# Step 2: Check the existence of PreReqToMajor 

# %%
# Define output file
output_file = "Parsing Scripts/Scripts/new_csv.csv"

# Create new DataFrame with required columns
new_df = pd.DataFrame(columns=["Program", "hasPrereqToMajor", "prereqToMajorList"])

has_prereq_to_major = False
# Process each unique program from main_record
for program in main_record["ProgramName"].unique():
    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Prerequisites to the Major" exists in the description
    has_prereq_to_major = any("Prerequisites to the Major" in desc for desc in program_description)

    # Append the program details to new_df
    new_df = pd.concat([new_df, pd.DataFrame([{
        "Program": program,
        "hasPrereqToMajor": has_prereq_to_major,
    }])], ignore_index=True)



# %% [markdown]
# Step 3 If PreReqs Exist create a list of PreReqs

# %%
# %%
import pandas as pd
import re

def extract_credits(description):
    """
    Extracts the first number from a 'Choose X Credit(s)' description and returns it as 'credits_X'.
    
    Args:
        description (str): The input string containing the credit description.
        
    Returns:
        str: A string in the format 'credits_X' where X is the extracted number, or 'credits_unknown' if no number is found.
    """
    match = re.search(r'Choose\s*(\d+)', str(description))
    
    if match:
        credits = match.group(1)
        return f'credits_{credits}'
    else:
        return 'credits_unknown'

# Process only the programs where hasPrereqToMajor is True
for index, row in new_df.iterrows():
    if row["hasPrereqToMajor"]:
        # Extract relevant rows from main_record where description contains "Prerequisites to the Major"
        prereq_rows = main_record[main_record["Description"].astype(str).str.contains("Prerequisites to the Major", na=False)]
        
        prereq_list = []  # List to store processed prerequisite courses
        
        for _, prereq_row in prereq_rows.iterrows():
            subject_course = f"{prereq_row['SubjectAbbreviation']} {prereq_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(prereq_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for prereq_entry in prereq_list:
                    if prereq_entry[0] == credit_label:
                        prereq_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    prereq_list.append([credit_label, subject_course])
            else:
                prereq_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted prerequisite list
        new_df.at[index, "prereqToMajorList"] = prereq_list



# %% [markdown]
# Step 4 Check for Gen Eds

# %%
# Add a new column 'hasReqGenEds' to new_df without re-creating it
new_df["hasReqGenEds"] = False


hasReqGenEds = False
# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Required General Education" exists in the description
    has_req_gen_eds = any("Required General Education" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasReqGenEds"] = has_req_gen_eds

# %% [markdown]
# Step 6 Create the list of Gen Eds if it exists

# %%
# Ensure the new column 'reqGenEdsList' exists in new_df
new_df["reqGenEdsList"] = None

# Process only the programs where hasReqGenEds is True
for index, row in new_df.iterrows():
    if row["hasReqGenEds"]:
        # Extract relevant rows from main_record where description contains "Required General Education"
        gen_ed_rows = main_record[main_record["Description"].astype(str).str.contains("Required General Education", na=False)]
        
        gen_ed_list = []  # List to store processed general education courses
        
        for _, gen_ed_row in gen_ed_rows.iterrows():
            subject_course = f"{gen_ed_row['SubjectAbbreviation']} {gen_ed_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(gen_ed_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for gen_ed_entry in gen_ed_list:
                    if gen_ed_entry[0] == credit_label:
                        gen_ed_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    gen_ed_list.append([credit_label, subject_course])
            else:
                gen_ed_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted general education list
        new_df.at[index, "reqGenEdsList"] = gen_ed_list

# %% [markdown]
# Step 7 Check for Major Common Core and Compliling a list of major courses

# %%
# Add a new column 'hasMajorCommonCore' to new_df without re-creating it
new_df["hasMajorCommonCore"] = False

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Major Common Core" exists in the description
    has_major_common_core = any("Major Common Core" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasMajorCommonCore"] = has_major_common_core

# --- PART 2: Extract Major Common Core Courses ---

# Ensure the new column 'majorCommonCoreList' exists in new_df
new_df["majorCommonCoreList"] = None

# Process only the programs where hasMajorCommonCore is True
for index, row in new_df.iterrows():
    if row["hasMajorCommonCore"]:
        # Extract relevant rows from main_record where description contains "Major Common Core"
        common_core_rows = main_record[main_record["Description"].astype(str).str.contains("Major Common Core", na=False)]
        
        common_core_list = []  # List to store processed major common core courses
        
        for _, common_core_row in common_core_rows.iterrows():
            subject_course = f"{common_core_row['SubjectAbbreviation']} {common_core_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(common_core_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for core_entry in common_core_list:
                    if core_entry[0] == credit_label:
                        core_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    common_core_list.append([credit_label, subject_course])
            else:
                common_core_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted major common core list
        new_df.at[index, "majorCommonCoreList"] = common_core_list

# %% [markdown]
# Step 8 Check for Thesis Capstone and Populate List Accordingly

# %%
# Add a new column 'hasThesisCapstone' to new_df without re-creating it
new_df["hasThesisCapstone"] = False

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Capstone Course" exists in the description
    has_thesis_capstone = any("Capstone Course" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasThesisCapstone"] = has_thesis_capstone

# --- PART 2: Extract Capstone Courses ---

# Ensure the new column 'ChooseThesisCapstone' exists in new_df
new_df["ChooseThesisCapstone"] = None

# Process only the programs where hasThesisCapstone is True
for index, row in new_df.iterrows():
    if row["hasThesisCapstone"]:
        # Extract relevant rows from main_record where description contains "Capstone Course"
        capstone_rows = main_record[main_record["Description"].astype(str).str.contains("Capstone Course", na=False)]
        
        capstone_list = []  # List to store processed capstone courses
        
        for _, capstone_row in capstone_rows.iterrows():
            subject_course = f"{capstone_row['SubjectAbbreviation']} {capstone_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(capstone_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for capstone_entry in capstone_list:
                    if capstone_entry[0] == credit_label:
                        capstone_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    capstone_list.append([credit_label, subject_course])
            else:
                capstone_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted capstone course list
        new_df.at[index, "ChooseThesisCapstone"] = capstone_list



# %% [markdown]
# Step 9 Check for Major Restricted Electives and Populate List Accordingly

# %%
# Define output file
output_file = "Parsing Scripts/Scripts/new_csv.csv"

# Add a new column 'hasMajorRestrictiveElectives' to new_df without re-creating it
new_df["hasMajorRestrictiveElectives"] = False

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Major Restricted Electives" exists in the description
    has_major_restrictive_electives = any("Major Restricted Electives" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasMajorRestrictiveElectives"] = has_major_restrictive_electives

# --- PART 2: Extract Major Restricted Electives Courses ---

# Ensure the new column 'majorRestrictiveElectivesList' exists in new_df
new_df["majorRestrictiveElectivesList"] = None

# Process only the programs where hasMajorRestrictiveElectives is True
for index, row in new_df.iterrows():
    if row["hasMajorRestrictiveElectives"]:
        # Extract relevant rows from main_record where description contains "Major Restricted Electives"
        restricted_electives_rows = main_record[main_record["Description"].astype(str).str.contains("Major Restricted Electives", na=False)]
        
        restricted_electives_list = []  # List to store processed major restricted electives courses
        
        for _, restricted_electives_row in restricted_electives_rows.iterrows():
            subject_course = f"{restricted_electives_row['SubjectAbbreviation']} {restricted_electives_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(restricted_electives_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for elective_entry in restricted_electives_list:
                    if elective_entry[0] == credit_label:
                        elective_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    restricted_electives_list.append([credit_label, subject_course])
            else:
                restricted_electives_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted major restricted electives list
        new_df.at[index, "majorRestrictiveElectivesList"] = restricted_electives_list


# %% [markdown]
# Step 10 Check for Major Unresticted Electives

# %%
# Define output file
output_file = "Parsing Scripts/Scripts/new_csv.csv"

# Add a new column 'hasMajorUnrestrictedElectives' to new_df without re-creating it
new_df["hasMajorUnrestrictedElectives"] = False

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Major Unrestricted Electives" exists in the description
    has_major_unrestricted_electives = any("Major Unrestricted Electives" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasMajorUnrestrictedElectives"] = has_major_unrestricted_electives

# --- PART 2: Extract Major Unrestricted Electives Courses ---

# Ensure the new column 'majorUnrestrictedElectivesList' exists in new_df
new_df["majorUnrestrictedElectivesList"] = None

# Process only the programs where hasMajorUnrestrictedElectives is True
for index, row in new_df.iterrows():
    if row["hasMajorUnrestrictedElectives"]:
        # Extract relevant rows from main_record where description contains "Major Unrestricted Electives"
        unrestricted_electives_rows = main_record[main_record["Description"].astype(str).str.contains("Major Unrestricted Electives", na=False)]
        
        unrestricted_electives_list = []  # List to store processed major unrestricted electives courses
        
        for _, unrestricted_electives_row in unrestricted_electives_rows.iterrows():
            subject_course = f"{unrestricted_electives_row['SubjectAbbreviation']} {unrestricted_electives_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(unrestricted_electives_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for elective_entry in unrestricted_electives_list:
                    if elective_entry[0] == credit_label:
                        elective_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    unrestricted_electives_list.append([credit_label, subject_course])
            else:
                unrestricted_electives_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted major unrestricted electives list
        new_df.at[index, "majorUnrestrictedElectivesList"] = unrestricted_electives_list


# %% [markdown]
# Step 11 Check for other Gradrequirements and create a list for that

# %%
# Add a new column 'hasOtherGradReq' to new_df without re-creating it
new_df["hasOtherGradReq"] = False

# Process each unique program from main_record
for index, row in new_df.iterrows():
    program = row["Program"]

    # Extract description for the program
    program_description = main_record.loc[main_record["ProgramName"] == program, "Description"].astype(str).tolist()

    # Check if "Other Graduation Requirements" exists in the description
    has_other_grad_req = any("Other Graduation Requirements" in desc for desc in program_description)

    # Update the new_df with the new column value
    new_df.at[index, "hasOtherGradReq"] = has_other_grad_req

# --- PART 2: Extract Other Graduation Requirements ---

# Ensure the new column 'otherGradReq' exists in new_df
new_df["otherGradReq"] = None

# Process only the programs where hasOtherGradReq is True
for index, row in new_df.iterrows():
    if row["hasOtherGradReq"]:
        # Extract relevant rows from main_record where description contains "Other Graduation Requirements"
        grad_req_rows = main_record[main_record["Description"].astype(str).str.contains("Other Graduation Requirements", na=False)]
        
        grad_req_list = []  # List to store processed graduation requirements
        
        for _, grad_req_row in grad_req_rows.iterrows():
            subject_course = f"{grad_req_row['SubjectAbbreviation']} {grad_req_row['CourseNumber']}"
            
            # Use extract_credits function to determine credit label
            credit_label = extract_credits(grad_req_row["GroupCredits"])
            
            # Check if GroupCredits has a valid credit label
            if credit_label != 'credits_unknown':
                found = False
                for grad_entry in grad_req_list:
                    if grad_entry[0] == credit_label:
                        grad_entry.append(subject_course)
                        found = True
                        break
                
                if not found:
                    grad_req_list.append([credit_label, subject_course])
            else:
                grad_req_list.append(subject_course)  # Append as a separate list entry if no valid credits
        
        # Update the new_df with the formatted graduation requirements list
        new_df.at[index, "otherGradReq"] = grad_req_list


# %% [markdown]
# Add the dataframe to the csv

# %%
import os

# Append to existing CSV or create a new one if it doesn't exist
if os.path.exists(output_file):
    new_df.to_csv(output_file, mode='a', header=False, index=False)
else:
    new_df.to_csv(output_file, mode='w', header=True, index=False)

print(f"Data appended to {output_file} successfully!")
print("Test")



